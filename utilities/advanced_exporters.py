from typing import Dict, Any
import json
from datetime import datetime

def create_wordpress_export(content: Dict[str, Any]) -> str:
    """Create WordPress-compatible XML export."""
    title = content.get('title', 'Untitled')
    body = content.get('content', '')
    
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wp="http://wordpress.org/export/1.2/">
<channel>
    <item>
        <title>{title}</title>
        <content:encoded><![CDATA[{body}]]></content:encoded>
        <wp:post_type>post</wp:post_type>
        <wp:status>draft</wp:status>
    </item>
</channel>
</rss>"""
    return xml

def create_medium_export(content: Dict[str, Any]) -> str:
    """Create Medium-compatible markdown export."""
    title = content.get('title', 'Untitled')
    body = content.get('content', '')
    tags = content.get('tags', [])
    
    markdown = f"""# {title}

Tags: {', '.join(tags)}

---

{body}
"""
    return markdown
