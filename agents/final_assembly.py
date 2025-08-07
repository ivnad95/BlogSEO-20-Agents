import os
import json
import re
import zipfile
from datetime import datetime

class FinalAssemblyAgent:
    """
    Assembles all generated content and assets into a final, deliverable package.
    This is a code-based agent and does not use an LLM.
    This corresponds to agent A20.
    """

    def run(self, state: dict) -> dict:
        """
        Takes the final state and assembles HTML and a zip file.

        Args:
            state: The final shared state dictionary.

        Returns:
            The updated state with paths to the final deliverables.
        """
        draft = state.get('draft', {})
        schemas = state.get('schemas', {})
        generated_images = state.get('generated_images', [])
        topic = state.get('topic', 'final-article')

        if not draft.get('full_text'):
            return {'error': 'Final draft text is missing.'}

        # --- Create Output Directory ---
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # --- Prepare Content ---
        full_text_md = draft['full_text']
        # Convert basic markdown to HTML
        html_content = self._markdown_to_html(full_text_md)
        # Inject images into the HTML
        html_with_images = self._inject_images_into_html(html_content, generated_images)

        # --- Prepare Schemas ---
        schema_scripts = []
        if schemas.get('article_schema'):
            schema_scripts.append(f'<script type="application/ld+json">{json.dumps(schemas["article_schema"], indent=2)}</script>')
        if schemas.get('faq_schema'):
            schema_scripts.append(f'<script type="application/ld+json">{json.dumps(schemas["faq_schema"], indent=2)}</script>')
        
        # --- Assemble Final HTML ---
        final_html = self._create_full_html_doc(topic, schema_scripts, html_with_images)

        # --- Save HTML File ---
        slug = self._slugify(topic)
        html_filename = f"{slug}.html"
        html_filepath = os.path.join(output_dir, html_filename)
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(final_html)

        # --- Create Zip Archive ---
        zip_filename = f"{slug}.zip"
        zip_filepath = os.path.join(output_dir, zip_filename)
        image_paths = [img['image_path'] for img in generated_images if 'image_path' in img]
        self._create_zip_archive(zip_filepath, html_filepath, image_paths)

        state['final_package'] = {
            "html_file": html_filepath,
            "zip_archive": zip_filepath
        }
        return state

    def _markdown_to_html(self, md_text: str) -> str:
        """A simple markdown to HTML converter."""
        # Convert ## Headings
        html = re.sub(r'^##\s*(.*)', r'<h2>\1</h2>', md_text, flags=re.MULTILINE)
        # Convert # Headings
        html = re.sub(r'^#\s*(.*)', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        # Convert markdown links [text](url)
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
        # Wrap paragraphs in <p> tags, handling multiple newlines
        paragraphs = [f'<p>{p.strip()}</p>' for p in md_text.split('\n\n') if p.strip()]
        html = '\n'.join(paragraphs)
        return html

    def _inject_images_into_html(self, html: str, images: list) -> str:
        """Injects image tags into the HTML body."""
        if not images:
            return html
        
        paragraphs = html.split('</p>')
        # Simple strategy: insert an image every 3 paragraphs
        insert_interval = 3
        
        for i, image_data in enumerate(images):
            # The image path in the HTML should be relative for the zip file
            relative_path = os.path.join('images', os.path.basename(image_data.get('image_path', '')))
            alt_text = image_data.get("alt_text", "Descriptive image")
            img_tag = f'<figure><img src="{relative_path}" alt="{alt_text}"><figcaption>{alt_text}</figcaption></figure>'

            # Insert the image after a paragraph
            insert_index = min((i + 1) * insert_interval, len(paragraphs) - 1)
            if insert_index < len(paragraphs):
                paragraphs[insert_index] = paragraphs[insert_index] + img_tag

        return '</p>'.join(paragraphs)

    def _create_full_html_doc(self, title: str, schemas: list, body_content: str) -> str:
        """Wraps the content in a full HTML document structure."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; max-width: 800px; margin: 2rem auto; padding: 1rem; color: #333; }}
        h1, h2 {{ color: #1a1a1a; }}
        img {{ max-width: 100%; height: auto; margin: 1rem 0; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        figure {{ margin: 1.5rem 0; }}
        figcaption {{ font-size: 0.9em; color: #555; text-align: center; margin-top: 0.5rem; }}
        a {{ color: #0056b3; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        p {{ margin-bottom: 1em; }}
    </style>
    {''.join(schemas)}
</head>
<body>
    {body_content}
</body>
</html>
"""

    def _create_zip_archive(self, zip_path: str, html_path: str, image_paths: list):
        """Creates a zip file with the HTML and images."""
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add HTML file to the root of the zip
            zipf.write(html_path, os.path.basename(html_path))
            # Add image files, placing them in an 'images' subfolder within the zip
            for img_path in image_paths:
                if os.path.exists(img_path):
                    zipf.write(img_path, os.path.join('images', os.path.basename(img_path)))

    def _slugify(self, text: str) -> str:
        """Converts text to a URL-friendly slug."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'[\s-]+', '-', text).strip('-')
        return text if text else "unnamed-article"
