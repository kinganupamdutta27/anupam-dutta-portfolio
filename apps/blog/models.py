"""
Blog app models for future blog functionality.

Contains Wagtail Page models for a blog section that can be
expanded as needed. The blog is a child of the HomePage.
"""

import logging

from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

logger = logging.getLogger(__name__)


class BlogIndexPage(Page):
    """
    Blog listing page - the parent page for all blog posts.

    Displays a paginated list of blog posts.
    """

    intro = RichTextField(
        blank=True,
        help_text="Introduction text displayed at the top of the blog listing.",
    )
    posts_per_page = models.PositiveIntegerField(
        default=10,
        help_text="Number of posts to display per page.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("posts_per_page"),
    ]

    template = "blog/blog_index_page.html"
    max_count = 1
    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.BlogPage"]

    class Meta:
        verbose_name = "Blog Index Page"

    def get_context(self, request, *args, **kwargs):
        """Add paginated blog posts to context."""
        context = super().get_context(request, *args, **kwargs)
        try:
            from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

            blog_posts = (
                BlogPage.objects.live()
                .descendant_of(self)
                .order_by("-first_published_at")
            )
            paginator = Paginator(blog_posts, self.posts_per_page)
            page_number = request.GET.get("page", 1)

            try:
                posts = paginator.page(page_number)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)

            context["posts"] = posts
        except Exception as e:
            logger.error(f"Error loading blog posts: {e}", exc_info=True)
            context["posts"] = []

        return context


class BlogPage(Page):
    """
    Individual blog post page.

    Uses StreamField for flexible content composition.
    """

    date = models.DateField(
        help_text="Publication date.",
    )
    excerpt = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief excerpt for listing pages.",
    )
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Featured image for the blog post.",
    )
    body = StreamField(
        [
            ("heading", blocks.CharBlock(form_classname="title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("code", blocks.TextBlock(help_text="Code snippet")),
            ("quote", blocks.BlockQuoteBlock()),
            (
                "raw_html",
                blocks.RawHTMLBlock(
                    help_text="Use sparingly - raw HTML content.",
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("excerpt"),
        FieldPanel("featured_image"),
        FieldPanel("body"),
        FieldPanel("tags"),
    ]

    template = "blog/blog_page.html"
    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["tag_list"] = [
            tag.strip() for tag in self.tags.split(",") if tag.strip()
        ]
        return context
