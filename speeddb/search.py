from collections import namedtuple
import os
import whoosh.index as index
import whoosh.fields as fields
import whoosh.qparser as qparser
from speeddb import constants as cn, statsd
from speeddb.models.clips import Clip

clip_index = None

def create_index(directory):
    ''' create_index creates a Whoosh index for clips in the given directory '''
    global clip_index

    if not os.path.exists(directory):
        os.makedirs(directory)

    if index.exists_in(directory):
        clip_index = index.open_dir(directory)
    else:
        schema = fields.Schema(id=fields.NUMERIC(stored=True), title=fields.TEXT, description=fields.TEXT, tags=fields.TEXT(stored=True), user=fields.TEXT)
        clip_index = index.create_in(directory, schema)

@statsd.timer('search.add_clip')
def add_clip(clip):
    ''' add_clip adds the given clip to the index '''
    writer = clip_index.writer()

    # Create a string containing all of the tags so they can be included in the search
    tags = ''
    for tag in clip.tags:
        tags += tag.name.replace('-', ' ') + ' '

    writer.add_document(id=clip.id,
                        title=clip.title,
                        description=clip.description,
                        tags=tags.strip(),
                        user=clip.user.username)
    writer.commit()

def add_clips(clips):
    ''' utility function for adding a list of clips '''
    writer = clip_index.writer()

    for clip in clips:
        tags = ''
        for tag in clip.tags:
            tags += tag.name.replace('-', ' ') + ' '

        writer.add_document(id=clip.id,
                            title=clip.title,
                            description=clip.description,
                            tags=tags.strip(),
                            user=clip.user.username)
    
    writer.commit()

@statsd.timer('search.remove_clip')
def remove_clip(clip):
    ''' remove_clip removes the given clip from the index '''
    writer = clip_index.writer()
    writer.delete_by_term('id', clip.id)
    writer.commit()

@statsd.timer('search.search_clips')
def search_clips(query, page):
    ''' search_clips returns the clips found by the given query
    Clips are stored in a named tuple called ClipSearchResults.
    ClipSearchResults has two fields:
    - clips: a list of Clip objects on the page
    - length: the total number of clips that match the query
    '''
    parser = qparser.MultifieldParser(['title', 'description', 'tags', 'user'], clip_index.schema)
    with clip_index.searcher() as searcher:
        results = searcher.search_page(parser.parse(query), page, pagelen=cn.SEARCH_CLIPS_PER_PAGE)

        clips = []
        for result in results:
            clips.append(Clip.query.get(result['id']))

        ClipSearchResults = namedtuple('ClipSearchResults', ['clips', 'length'])
        return ClipSearchResults(clips, len(results))