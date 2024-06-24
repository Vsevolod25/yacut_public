from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import (
    InvalidAPIUsage, ValidationError
)
from .models import URLMap


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original(short_id):
    urlmap = URLMap().get_urlmap(short_id)
    return jsonify({'url': urlmap.original}), HTTPStatus.OK


@app.route('/api/id/', methods=['POST'])
def add_urlmap():
    data = request.get_json(silent=True)
    if data is None:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    url = data.get('url')
    if not url:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    try:
        urlmap_dict = URLMap().create_urlmap(
            url, data.get('custom_id'), api=True
        )
    except ValidationError as error:
        raise InvalidAPIUsage(str(error))
    return jsonify(
        {
            'url': urlmap_dict['url'],
            'short_link': urlmap_dict['short_link']
        }
    ), HTTPStatus.CREATED
