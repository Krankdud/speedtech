from flask import jsonify
from speeddb.views import blueprint
from speeddb.models.tags import Tag

@blueprint.route('/_get-tags')
def get_tags():
    tags = Tag.query.all()
    tag_names = list(map(lambda tag: tag.name, tags))
    return jsonify(tag_names)