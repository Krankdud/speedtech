from flask import Markup
from pyembed.core import PyEmbed
from werkzeug.contrib.cache import SimpleCache, MemcachedCache

cache = None

def init_cache(cache_type="simple", memcached_servers=[], timeout=259200):
    global cache
    if cache_type == 'simple':
        cache = SimpleCache(default_timeout=timeout)
    elif cache_type == 'memcached':
        cache = MemcachedCache(servers=memcached_servers, default_timeout=timeout)

def get_cached_embed(url):
    embed_html = cache.get(url)
    if embed_html == None:
        embed_html = PyEmbed().embed(url)
        cache.set(url, embed_html)
    return Markup(embed_html)