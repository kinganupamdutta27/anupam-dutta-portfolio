"""
Wagtail hooks for the Home app.

Customizes the Wagtail admin interface with additional
menu items, branding, and functionality.
"""

from wagtail import hooks
from django.utils.html import format_html
from django.templatetags.static import static


@hooks.register("insert_global_admin_css")
def global_admin_css():
    """Add custom CSS to the Wagtail admin."""
    return format_html(
        '<style>'
        '.content-wrapper {{ max-width: 1400px; }}'
        '.homepage-section-header {{ color: #667eea; font-weight: 600; '
        'border-bottom: 2px solid #667eea; padding-bottom: 0.5rem; '
        'margin-bottom: 1rem; }}'
        '</style>'
    )


@hooks.register("construct_main_menu")
def hide_unnecessary_menu_items(request, menu_items):
    """Hide menu items that are not needed for this portfolio site."""
    # Remove Documents menu item if not needed
    # menu_items[:] = [item for item in menu_items if item.name != "documents"]
    pass
