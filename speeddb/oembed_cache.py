import logging
import time
from flask import Markup
from pyembed.core import PyEmbed
from werkzeug.contrib.cache import SimpleCache, MemcachedCache, FileSystemCache
from speeddb import statsd

cache = None
log = logging.getLogger('flask.app')

def init_cache(cache_type="simple", memcached_servers=[], cache_dir=None, timeout=259200):
    ''' init_cache creates the oembed cache with the given cache type

    cache_type - 'simple', 'memcached', or 'file'. Determines which type of cache to use
    memcached_servers - List of memcached servers. Must be set if cache_type is 'memcached'.
    cache_dir - Directory for a file system cache. Must be set if cache_type is 'file'.
    timeout - Timeout in seconds. Default is 3 days.
    '''
    global cache
    if cache_type == 'simple':
        cache = SimpleCache(default_timeout=timeout)
    elif cache_type == 'memcached':
        cache = MemcachedCache(servers=memcached_servers, default_timeout=timeout)
    elif cache_type == 'file':
        cache = FileSystemCache(cache_dir, default_timeout=timeout)

def get(url):
    ''' get obtains the html for an embedded video '''
    embed_html = cache.get(url)
    if embed_html == None:
        start = time.time()

        try:
            embed_html = PyEmbed().embed(url)

            dt = int((time.time() - start) * 1000)
            if 'youtube' in url:
                statsd.timing('oembed.get.youtube', dt)
            elif 'twitch' in url:
                statsd.timing('oembed.get.twitch', dt)
            elif 'twitter' in url:
                statsd.timing('oembed.get.twitter', dt)
            else:
                statsd.timing('oembed.get.other', dt)

            cache.set(url, embed_html)
            statsd.incr('oembed.cache.miss')
        except KeyError as error:
            log.warning("Could not obtain clip from oembed for url: %s", url)
            raise
    else:
        statsd.incr('oembed.cache.hit')
    return Markup(embed_html)
