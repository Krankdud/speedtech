from flask import Blueprint

blueprint = Blueprint('views', __name__, template_folder='../templates', static_folder='../static')