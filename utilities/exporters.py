"""Export utilities for saving blog content in various formats."""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import zipfile
import tempfile
import shutil

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

try:
    import markdown2
    MARKDOWN2_AVAILABLE = True
except ImportError:
    MARKDOWN2_AVAILABLE = False

try:
    from jinja2 import Template, Environment, FileSystemLoader
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    Template = None

from utilities.logger import get_logger
from utilities.models import BlogPost, Section, ImageMeta

logger = get_logger("exporters")


class ExportFormat:
    """Export format types."""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    WORDPRESS = "wordpress"
    MEDIUM = "medium"
    PDF = "pdf"


class BlogExporter:
    """Main exporter class for blog content."""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"BlogExporter initialized with output directory: {self.output_dir}")
    
    def _generate_filename(self, slug: str, format: str) -> str:
        """Generate filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{slug}_{timestamp}.{format}"
    
    def save_markdown(self, blog_post: BlogPost, filename: Optional[str] = None) -> Path:
        """Save blog post as markdown file."""
        if filename is None:
            filename = self._generate_filename(blog_post.slug, "md")
        
        filepath = self.output_dir / filename
        content = blog_post.to_markdown()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.success(f"Markdown saved to: {filepath}")
        return filepath
    
    def save_html(self, blog_post: BlogPost, filename: Optional[str] = None, template: Optional[str] = None) -> Path:
        """Save blog post as HTML file."""
        if filename is None:
            filename = self._generate_filename(blog_post.slug, "html")
        
        filepath = self.output_dir / filename
        
        if template and JINJA2_AVAILABLE:
            # Use custom template if provided
            html_content = self._render_with_template(blog_post, template)
        else:
            # Use default HTML generation
            html_content = self._generate_full_html(blog_post)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.success(f"HTML saved to: {filepath}")
        return filepath
    
    def _generate_full_html(self, blog_post: BlogPost) -> str:
        """Generate complete HTML document."""
        # Get meta tags if SEO metadata exists
        meta_tags = ""
        if blog_post.seo_metadata:
            meta_tags = "\n".join(blog_post.seo_metadata.to_meta_tags())
        else:
            meta_tags = f"<title>{blog_post.title}</title>"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {meta_tags}
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 2em;
            margin-bottom: 1em;
            font-weight: 600;
        }}
        h1 {{ font-size: 2.5em; }}
        h2 {{ font-size: 2em; }}
        h3 {{ font-size: 1.5em; }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 2em auto;
        }}
        .meta {{
            color: #666;
            font-size: 0.9em;
            margin: 1em 0;
        }}
        .tags {{
            margin: 1em 0;
        }}
        .tag {{
            display: inline-block;
            background: #f0f0f0;
            padding: 0.3em 0.8em;
            margin: 0.2em;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        .featured-image {{
            margin: 2em 0;
        }}
        .introduction {{
            font-size: 1.1em;
            font-style: italic;
            color: #555;
            margin: 2em 0;
        }}
        .conclusion {{
            margin-top: 3em;
            padding-top: 2em;
            border-top: 1px solid #e0e0e0;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            padding-left: 1em;
            margin-left: 0;
            font-style: italic;
        }}
        code {{
            background: #f4f4f4;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background: #f4f4f4;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
        }}
        pre code {{
            background: none;
            padding: 0;
        }}
    </style>
</head>
<body>
    {blog_post.to_html()}
</body>
</html>"""
        return html
    
    def _render_with_template(self, blog_post: BlogPost, template_path: str) -> str:
        """Render blog post with Jinja2 template."""
        if not JINJA2_AVAILABLE:
            logger.warning("Jinja2 not available, using default HTML generation")
            return self._generate_full_html(blog_post)
        
        try:
            template_dir = Path(template_path).parent
            template_name = Path(template_path).name
            
            env = Environment(loader=FileSystemLoader(template_dir))
            template = env.get_template(template_name)
            
            return template.render(blog_post=blog_post)
        except Exception as e:
            logger.error(f"Template rendering failed: {e}")
            return self._generate_full_html(blog_post)
    
    def save_json(self, blog_post: BlogPost, filename: Optional[str] = None) -> Path:
        """Save blog post as JSON file."""
        if filename is None:
            filename = self._generate_filename(blog_post.slug, "json")
        
        filepath = self.output_dir / filename
        
        # Convert blog post to dictionary
        data = self._blog_post_to_dict(blog_post)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.success(f"JSON saved to: {filepath}")
        return filepath
    
    def _blog_post_to_dict(self, blog_post: BlogPost) -> Dict[str, Any]:
        """Convert BlogPost to dictionary."""
        return {
            "title": blog_post.title,
            "slug": blog_post.slug,
            "author": blog_post.author,
            "category": blog_post.category,
            "tags": blog_post.tags,
            "summary": blog_post.summary,
            "introduction": blog_post.introduction,
            "sections": [
                {
                    "heading": section.heading,
                    "content": section.content,
                    "level": section.level,
                    "keywords": section.keywords,
                    "word_count": section.word_count,
                    "images": [
                        {
                            "url": img.url,
                            "alt_text": img.alt_text,
                            "title": img.title
                        } for img in section.images
                    ]
                } for section in blog_post.sections
            ],
            "conclusion": blog_post.conclusion,
            "seo_metadata": {
                "title": blog_post.seo_metadata.title,
                "meta_description": blog_post.seo_metadata.meta_description,
                "keywords": blog_post.seo_metadata.keywords
            } if blog_post.seo_metadata else None,
            "featured_image": {
                "url": blog_post.featured_image.url,
                "alt_text": blog_post.featured_image.alt_text
            } if blog_post.featured_image else None,
            "status": blog_post.status.value,
            "created_at": blog_post.created_at.isoformat(),
            "updated_at": blog_post.updated_at.isoformat(),
            "published_at": blog_post.published_at.isoformat() if blog_post.published_at else None,
            "word_count": blog_post.word_count,
            "reading_time": blog_post.reading_time,
            "internal_links": blog_post.internal_links,
            "external_links": blog_post.external_links
        }
    
    def save_wordpress_xml(self, blog_post: BlogPost, filename: Optional[str] = None) -> Path:
        """Save blog post as WordPress-compatible XML."""
        if filename is None:
            filename = self._generate_filename(blog_post.slug, "xml")
        
        filepath = self.output_dir / filename
        
        # Convert markdown to HTML if needed
        content_html = blog_post.to_html()
        
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
    <item>
        <title><![CDATA[{blog_post.title}]]></title>
        <link>{blog_post.slug}</link>
        <pubDate>{blog_post.created_at.strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
        <dc:creator><![CDATA[{blog_post.author}]]></dc:creator>
        <guid isPermaLink="false">{blog_post.slug}</guid>
        <description><![CDATA[{blog_post.summary or ''}]]></description>
        <content:encoded><![CDATA[{content_html}]]></content:encoded>
        <wp:post_name><![CDATA[{blog_post.slug}]]></wp:post_name>
        <wp:status><![CDATA[{blog_post.status.value}]]></wp:status>
        <wp:post_type><![CDATA[post]]></wp:post_type>
        <category domain="category" nicename="{blog_post.category or 'uncategorized'}"><![CDATA[{blog_post.category or 'Uncategorized'}]]></category>
"""
        
        # Add tags
        for tag in blog_post.tags:
            xml_content += f'        <category domain="post_tag" nicename="{tag.lower().replace(" ", "-")}"><![CDATA[{tag}]]></category>\n'
        
        xml_content += """    </item>
</channel>
</rss>"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        logger.success(f"WordPress XML saved to: {filepath}")
        return filepath
    
    def create_export_bundle(self, blog_post: BlogPost, formats: List[str] = None) -> Path:
        """Create a ZIP bundle with multiple export formats."""
        if formats is None:
            formats = [ExportFormat.MARKDOWN, ExportFormat.HTML, ExportFormat.JSON]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save in each format
            files = []
            for format in formats:
                if format == ExportFormat.MARKDOWN:
                    file = self.save_markdown(blog_post, filename=f"{blog_post.slug}.md")
                elif format == ExportFormat.HTML:
                    file = self.save_html(blog_post, filename=f"{blog_post.slug}.html")
                elif format == ExportFormat.JSON:
                    file = self.save_json(blog_post, filename=f"{blog_post.slug}.json")
                elif format == ExportFormat.WORDPRESS:
                    file = self.save_wordpress_xml(blog_post, filename=f"{blog_post.slug}.xml")
                else:
                    continue
                
                # Copy to temp directory
                shutil.copy(file, temp_path / file.name)
                files.append(file.name)
            
            # Create ZIP file
            zip_filename = self._generate_filename(blog_post.slug, "zip")
            zip_path = self.output_dir / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in files:
                    file_path = temp_path / file
                    zipf.write(file_path, file)
            
            logger.success(f"Export bundle created: {zip_path}")
            return zip_path


class StreamlitExporter:
    """Streamlit-specific export utilities."""
    
    @staticmethod
    def create_download_button(
        content: Union[str, bytes],
        filename: str,
        mime_type: str = "text/plain",
        button_text: str = "Download",
        key: Optional[str] = None
    ):
        """Create a Streamlit download button."""
        if not STREAMLIT_AVAILABLE:
            logger.warning("Streamlit not available")
            return
        
        # Convert string to bytes if needed
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        st.download_button(
            label=button_text,
            data=content,
            file_name=filename,
            mime=mime_type,
            key=key
        )
    
    @staticmethod
    def create_download_link(
        content: Union[str, bytes],
        filename: str,
        link_text: str = "Click here to download"
    ) -> str:
        """Create a download link (HTML anchor tag)."""
        # Convert string to bytes if needed
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        # Encode content to base64
        b64 = base64.b64encode(content).decode()
        
        # Create download link
        href = f'<a href="data:file/txt;base64,{b64}" download="{filename}">{link_text}</a>'
        return href
    
    @staticmethod
    def display_export_options(blog_post: BlogPost, exporter: BlogExporter):
        """Display export options in Streamlit UI."""
        if not STREAMLIT_AVAILABLE:
            logger.warning("Streamlit not available")
            return
        
        st.subheader("💾 Export Options")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📝 Markdown", key="export_md"):
                filepath = exporter.save_markdown(blog_post)
                with open(filepath, 'r') as f:
                    content = f.read()
                StreamlitExporter.create_download_button(
                    content=content,
                    filename=f"{blog_post.slug}.md",
                    mime_type="text/markdown",
                    button_text="⬇ Download Markdown",
                    key="download_md"
                )
        
        with col2:
            if st.button("🌐 HTML", key="export_html"):
                filepath = exporter.save_html(blog_post)
                with open(filepath, 'r') as f:
                    content = f.read()
                StreamlitExporter.create_download_button(
                    content=content,
                    filename=f"{blog_post.slug}.html",
                    mime_type="text/html",
                    button_text="⬇ Download HTML",
                    key="download_html"
                )
        
        with col3:
            if st.button("📄 JSON", key="export_json"):
                filepath = exporter.save_json(blog_post)
                with open(filepath, 'r') as f:
                    content = f.read()
                StreamlitExporter.create_download_button(
                    content=content,
                    filename=f"{blog_post.slug}.json",
                    mime_type="application/json",
                    button_text="⬇ Download JSON",
                    key="download_json"
                )
        
        with col4:
            if st.button("📦 Bundle", key="export_bundle"):
                zip_path = exporter.create_export_bundle(blog_post)
                with open(zip_path, 'rb') as f:
                    content = f.read()
                StreamlitExporter.create_download_button(
                    content=content,
                    filename=f"{blog_post.slug}_bundle.zip",
                    mime_type="application/zip",
                    button_text="⬇ Download Bundle",
                    key="download_bundle"
                )
        
        # WordPress export option
        with st.expander("WordPress Export"):
            if st.button("Generate WordPress XML", key="export_wp"):
                filepath = exporter.save_wordpress_xml(blog_post)
                with open(filepath, 'r') as f:
                    content = f.read()
                StreamlitExporter.create_download_button(
                    content=content,
                    filename=f"{blog_post.slug}.xml",
                    mime_type="application/xml",
                    button_text="⬇ Download WordPress XML",
                    key="download_wp"
                )
                st.info("Import this XML file in WordPress: Tools > Import > WordPress")
    
    @staticmethod
    def preview_content(blog_post: BlogPost, format: str = "markdown"):
        """Preview blog content in Streamlit."""
        if not STREAMLIT_AVAILABLE:
            logger.warning("Streamlit not available")
            return
        
        if format == "markdown":
            st.markdown(blog_post.to_markdown())
        elif format == "html":
            st.components.v1.html(blog_post.to_html(), height=800, scrolling=True)
        elif format == "json":
            exporter = BlogExporter()
            data = exporter._blog_post_to_dict(blog_post)
            st.json(data)


# Convenience functions
def export_blog_post(
    blog_post: BlogPost,
    format: str = ExportFormat.MARKDOWN,
    output_dir: str = "output",
    filename: Optional[str] = None
) -> Path:
    """Quick export function for blog posts."""
    exporter = BlogExporter(output_dir)
    
    if format == ExportFormat.MARKDOWN:
        return exporter.save_markdown(blog_post, filename)
    elif format == ExportFormat.HTML:
        return exporter.save_html(blog_post, filename)
    elif format == ExportFormat.JSON:
        return exporter.save_json(blog_post, filename)
    elif format == ExportFormat.WORDPRESS:
        return exporter.save_wordpress_xml(blog_post, filename)
    else:
        raise ValueError(f"Unsupported format: {format}")


def batch_export(
    blog_posts: List[BlogPost],
    formats: List[str] = None,
    output_dir: str = "output"
) -> List[Path]:
    """Export multiple blog posts."""
    if formats is None:
        formats = [ExportFormat.MARKDOWN]
    
    exporter = BlogExporter(output_dir)
    exported_files = []
    
    for blog_post in blog_posts:
        for format in formats:
            try:
                filepath = export_blog_post(blog_post, format, output_dir)
                exported_files.append(filepath)
            except Exception as e:
                logger.error(f"Failed to export {blog_post.slug} as {format}: {e}")
    
    return exported_files
