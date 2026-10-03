import hashlib
from functools import lru_cache

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@lru_cache(maxsize=None)
def _content_hash(path):
    found = finders.find(path)
    if not found:
        return ''
    with open(found, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:10]


@register.simple_tag
def static_v(path):
    """Like {% static %}, plus ?v=<content hash> so browsers and the service
    worker fetch the new file after a deploy instead of a cached copy."""
    if settings.DEBUG:
        _content_hash.cache_clear()  # pick up edits without restarting runserver
    version = _content_hash(path)
    url = static(path)
    return f'{url}?v={version}' if version else url
