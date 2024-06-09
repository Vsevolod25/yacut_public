from http import HTTPStatus

from flask import jsonify, request, url_for

from . import app
from .error_handlers import (
    InvalidAPIUsage, InvalidShortNameException, RepeatedShortException
)
from .models import URLMap


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original(short_id):
    urlmap = URLMap().get_urlmap(short_id)
    if not urlmap:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
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
        urlmap_dict = URLMap().create_urlmap(url, data.get('custom_id'))
    except InvalidShortNameException:
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )
    except RepeatedShortException:
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )
    return jsonify(
        {
            'url': urlmap_dict['url'],
            'short_link': url_for(
                'redirect_view',
                short_id=urlmap_dict['short_link'],
                _external=True
            )[:-1]
        }
    ), HTTPStatus.CREATED
