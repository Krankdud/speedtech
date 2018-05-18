from speeddb import constants as cn, oembed_cache
from flask import abort

def get_page_count(clip_count, clips_per_page=cn.SEARCH_CLIPS_PER_PAGE):
    ''' get_page_count figures out the number of pages required for a given number of clips '''
    page_count = clip_count // clips_per_page
    if clip_count % clips_per_page != 0:
        page_count += 1
    return page_count

def get_clips_on_page(clips, page, clips_per_page=cn.SEARCH_CLIPS_PER_PAGE):
    ''' get_clips_on_page returns a slice of the clips list containing the clips on a given page.
    This function also retrieves the embedded content '''
    clips_on_page = clips[(page - 1) * clips_per_page : page * clips_per_page]
    for clip in clips_on_page:
        clip.embed = oembed_cache.get(clip.url)
        clip.is_twitter = 'class="twitter-tweet"' in clip.embed
    return clips_on_page

def fetch_embeds_for_clips(clips):
    ''' fetch_embeds_for_clips gets the html for embedded videos for each clip from the cache '''
    for clip in clips:
        clip.embed = oembed_cache.get(clip.url)
        clip.is_twitter = 'class="twitter-tweet"' in clip.embed