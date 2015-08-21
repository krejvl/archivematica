from django.conf.urls import url, patterns
from django.conf import settings
from components.file import views

urlpatterns = patterns('',
    url(r'(?P<uuid>' + settings.UUID_REGEX + ')/$', views.file_details),
    url(r'(?P<uuid>' + settings.UUID_REGEX + ')/tags/$', views.transfer_file_tags),
    url(r'(?P<uuid>' + settings.UUID_REGEX + ')/bulk_extractor/$', views.bulk_extractor),
)