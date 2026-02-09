"""
URL configuration for Anupam Dutta Portfolio.

Routes:
    /admin/     → Django Admin (Unfold)
    /cms/       → Wagtail CMS Admin
    /documents/ → Wagtail Document serving
    /contact/   → Contact form endpoints
    /           → Wagtail page serving (portfolio)
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    # Django Admin (Unfold themed)
    path("admin/", admin.site.urls),
    # Wagtail CMS Admin
    path("cms/", include(wagtailadmin_urls)),
    # Wagtail Documents
    path("documents/", include(wagtaildocs_urls)),
    # Contact Form API
    path("contact/", include("apps.contact.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Wagtail catch-all (must be last)
urlpatterns += [
    path("", include(wagtail_urls)),
]
