from speeddb import constants as cn, oembed_cache
from flask import abort

def get_page_count(clip_count):
    ''' get_page_count figures out the number of pages required for a given number of clips '''
    page_count = clip_count // cn.SEARCH_CLIPS_PER_PAGE
    if clip_count % cn.SEARCH_CLIPS_PER_PAGE != 0:
        page_count += 1
    return page_count

def get_clips_on_page(clips, page):
    ''' get_clips_on_page returns a slice of the clips list containing the clips on a given page.
    This function also retrieves the embedded content '''
    clips_on_page = clips[(page - 1) * cn.SEARCH_CLIPS_PER_PAGE : page * cn.SEARCH_CLIPS_PER_PAGE]
    for clip in clips_on_page:
        clip.embed = oembed_cache.get_cached_embed(clip.url)
    return clips_on_page