"""Data models for blog automation system."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object
    Field = lambda *args, **kwargs: None


class ContentStatus(Enum):
    """Status of content generation."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ImageSource(Enum):
    """Image source types."""
    PIXABAY = "pixabay"
    UNSPLASH = "unsplash"
    PEXELS = "pexels"
    GENERATED = "generated"
    UPLOADED = "uploaded"


@dataclass
class ImageMeta:
    """Metadata for blog images."""
    url: str
    alt_text: str
    title: Optional[str] = None
    source: Optional[ImageSource] = None
    width: Optional[int] = None
    height: Optional[int] = None
    file_size: Optional[int] = None
    mime_type: str = "image/jpeg"
    attribution: Optional[str] = None
    license: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_markdown(self) -> str:
        """Convert to markdown image syntax."""
        return f"![{self.alt_text}]({self.url} \"{self.title or self.alt_text}\")"
    
    def to_html(self) -> str:
        """Convert to HTML img tag."""
        attrs = [f'src="{self.url}"', f'alt="{self.alt_text}"']
        if self.title:
            attrs.append(f'title="{self.title}"')
        if self.width:
            attrs.append(f'width="{self.width}"')
        if self.height:
            attrs.append(f'height="{self.height}"')
        return f"<img {' '.join(attrs)} />"


@dataclass
class SEOMetadata:
    """SEO metadata for blog posts."""
    title: str
    meta_description: str
    keywords: List[str] = field(default_factory=list)
    canonical_url: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    twitter_card: str = "summary_large_image"
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    schema_markup: Optional[Dict[str, Any]] = None
    
    def to_meta_tags(self) -> List[str]:
        """Generate HTML meta tags."""
        tags = [
            f'<title>{self.title}</title>',
            f'<meta name="description" content="{self.meta_description}">',
        ]
        
        if self.keywords:
            keywords_str = ', '.join(self.keywords)
            tags.append(f'<meta name="keywords" content="{keywords_str}">')
        
        if self.canonical_url:
            tags.append(f'<link rel="canonical" href="{self.canonical_url}">')
        
        # Open Graph tags
        if self.og_title:
            tags.append(f'<meta property="og:title" content="{self.og_title}">')
        if self.og_description:
            tags.append(f'<meta property="og:description" content="{self.og_description}">')
        if self.og_image:
            tags.append(f'<meta property="og:image" content="{self.og_image}">')
        
        # Twitter Card tags
        tags.append(f'<meta name="twitter:card" content="{self.twitter_card}">')
        if self.twitter_title:
            tags.append(f'<meta name="twitter:title" content="{self.twitter_title}">')
        if self.twitter_description:
            tags.append(f'<meta name="twitter:description" content="{self.twitter_description}">')
        if self.twitter_image:
            tags.append(f'<meta name="twitter:image" content="{self.twitter_image}">')
        
        return tags


@dataclass
class Section:
    """Blog post section."""
    heading: str
    content: str
    level: int = 2  # Heading level (h2, h3, etc.)
    subsections: List['Section'] = field(default_factory=list)
    images: List[ImageMeta] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    word_count: Optional[int] = None
    
    def __post_init__(self):
        if self.word_count is None:
            self.word_count = len(self.content.split())
    
    def to_markdown(self) -> str:
        """Convert section to markdown."""
        lines = []
        lines.append(f"{'#' * self.level} {self.heading}")
        lines.append("")
        
        # Add images if any
        for image in self.images:
            lines.append(image.to_markdown())
            lines.append("")
        
        lines.append(self.content)
        lines.append("")
        
        # Add subsections
        for subsection in self.subsections:
            lines.append(subsection.to_markdown())
        
        return "\n".join(lines)
    
    def to_html(self) -> str:
        """Convert section to HTML."""
        lines = []
        lines.append(f"<h{self.level}>{self.heading}</h{self.level}>")
        
        # Add images if any
        for image in self.images:
            lines.append(f'<figure>{image.to_html()}</figure>')
        
        # Convert content paragraphs
        paragraphs = self.content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                lines.append(f"<p>{para.strip()}</p>")
        
        # Add subsections
        for subsection in self.subsections:
            lines.append(subsection.to_html())
        
        return "\n".join(lines)


@dataclass
class BlogPost:
    """Complete blog post structure."""
    title: str
    slug: str
    author: str = "AI Assistant"
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    introduction: Optional[str] = None
    sections: List[Section] = field(default_factory=list)
    conclusion: Optional[str] = None
    seo_metadata: Optional[SEOMetadata] = None
    featured_image: Optional[ImageMeta] = None
    status: ContentStatus = ContentStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    word_count: Optional[int] = None
    reading_time: Optional[int] = None  # in minutes
    internal_links: List[str] = field(default_factory=list)
    external_links: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.update_metrics()
    
    def update_metrics(self):
        """Update word count and reading time."""
        total_words = 0
        
        if self.introduction:
            total_words += len(self.introduction.split())
        
        for section in self.sections:
            total_words += section.word_count or 0
        
        if self.conclusion:
            total_words += len(self.conclusion.split())
        
        self.word_count = total_words
        # Average reading speed: 200 words per minute
        self.reading_time = max(1, round(total_words / 200))
    
    def to_markdown(self) -> str:
        """Convert blog post to markdown."""
        lines = []
        
        # Front matter
        lines.append("---")
        lines.append(f"title: {self.title}")
        lines.append(f"author: {self.author}")
        lines.append(f"date: {self.created_at.strftime('%Y-%m-%d')}")
        if self.category:
            lines.append(f"category: {self.category}")
        if self.tags:
            lines.append(f"tags: [{', '.join(self.tags)}]")
        lines.append(f"status: {self.status.value}")
        lines.append(f"reading_time: {self.reading_time} min")
        lines.append("---")
        lines.append("")
        
        # Title
        lines.append(f"# {self.title}")
        lines.append("")
        
        # Featured image
        if self.featured_image:
            lines.append(self.featured_image.to_markdown())
            lines.append("")
        
        # Introduction
        if self.introduction:
            lines.append(self.introduction)
            lines.append("")
        
        # Sections
        for section in self.sections:
            lines.append(section.to_markdown())
        
        # Conclusion
        if self.conclusion:
            lines.append("## Conclusion")
            lines.append("")
            lines.append(self.conclusion)
            lines.append("")
        
        return "\n".join(lines)
    
    def to_html(self) -> str:
        """Convert blog post to HTML."""
        lines = []
        
        # Article wrapper
        lines.append('<article class="blog-post">')
        
        # Header
        lines.append('<header>')
        lines.append(f'<h1>{self.title}</h1>')
        lines.append(f'<div class="meta">')
        lines.append(f'<span class="author">By {self.author}</span>')
        lines.append(f'<time datetime="{self.created_at.isoformat()}">{self.created_at.strftime("%B %d, %Y")}</time>')
        lines.append(f'<span class="reading-time">{self.reading_time} min read</span>')
        lines.append('</div>')
        
        if self.tags:
            lines.append('<div class="tags">')
            for tag in self.tags:
                lines.append(f'<span class="tag">{tag}</span>')
            lines.append('</div>')
        
        lines.append('</header>')
        
        # Featured image
        if self.featured_image:
            lines.append(f'<div class="featured-image">{self.featured_image.to_html()}</div>')
        
        # Content
        lines.append('<div class="content">')
        
        if self.introduction:
            lines.append(f'<div class="introduction"><p>{self.introduction}</p></div>')
        
        for section in self.sections:
            lines.append('<section>')
            lines.append(section.to_html())
            lines.append('</section>')
        
        if self.conclusion:
            lines.append('<section class="conclusion">')
            lines.append('<h2>Conclusion</h2>')
            lines.append(f'<p>{self.conclusion}</p>')
            lines.append('</section>')
        
        lines.append('</div>')
        lines.append('</article>')
        
        return "\n".join(lines)


if PYDANTIC_AVAILABLE:
    class PydanticImageMeta(BaseModel):
        """Pydantic version of ImageMeta."""
        url: str
        alt_text: str
        title: Optional[str] = None
        source: Optional[str] = None
        width: Optional[int] = Field(None, gt=0)
        height: Optional[int] = Field(None, gt=0)
        file_size: Optional[int] = Field(None, gt=0)
        mime_type: str = "image/jpeg"
        attribution: Optional[str] = None
        license: Optional[str] = None
        tags: List[str] = Field(default_factory=list)
        
        @validator('mime_type')
        def validate_mime_type(cls, v):
            allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
            if v not in allowed:
                raise ValueError(f'mime_type must be one of {allowed}')
            return v
    
    class PydanticBlogPost(BaseModel):
        """Pydantic version of BlogPost with validation."""
        title: str = Field(..., min_length=1, max_length=200)
        slug: str = Field(..., pattern=r'^[a-z0-9-]+$')
        author: str = Field(default="AI Assistant", min_length=1)
        category: Optional[str] = None
        tags: List[str] = Field(default_factory=list, max_items=10)
        summary: Optional[str] = Field(None, max_length=500)
        introduction: Optional[str] = Field(None, max_length=1000)
        sections: List[Dict[str, Any]] = Field(default_factory=list)
        conclusion: Optional[str] = Field(None, max_length=1000)
        seo_metadata: Optional[Dict[str, Any]] = None
        featured_image: Optional[Dict[str, Any]] = None
        status: str = Field(default="draft")
        created_at: datetime = Field(default_factory=datetime.now)
        updated_at: datetime = Field(default_factory=datetime.now)
        published_at: Optional[datetime] = None
        word_count: Optional[int] = Field(None, ge=0)
        reading_time: Optional[int] = Field(None, ge=1)
        internal_links: List[str] = Field(default_factory=list)
        external_links: List[str] = Field(default_factory=list)
        
        @validator('status')
        def validate_status(cls, v):
            allowed = ['draft', 'in_progress', 'review', 'published', 'archived']
            if v not in allowed:
                raise ValueError(f'status must be one of {allowed}')
            return v
        
        class Config:
            json_encoders = {
                datetime: lambda v: v.isoformat()
            }


@dataclass
class AgentResponse:
    """Response from an AI agent."""
    agent_name: str
    content: Any
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time: Optional[float] = None  # in seconds


@dataclass
class GenerationConfig:
    """Configuration for blog generation."""
    topic: str
    target_word_count: int = 1500
    tone: str = "professional"
    style: str = "informative"
    target_audience: str = "general"
    include_images: bool = True
    optimize_seo: bool = True
    generate_meta: bool = True
    use_external_links: bool = True
    use_internal_links: bool = False
    max_sections: int = 5
    min_section_words: int = 200
    temperature: float = 0.7
    model: str = "gpt-4"
    language: str = "en"
    custom_instructions: Optional[str] = None
