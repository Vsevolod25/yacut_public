from re import match

from flask import jsonify, request

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_original(short_id):
    urlmap = URLMap.query.filter_by(short=short_id).first()
    if urlmap:
        return jsonify({'url': urlmap.to_dict()['url']}), 200
    raise InvalidAPIUsage('Указанный id не найден', 404)


@app.route('/api/id/', methods=['POST'])
def add_urlmap():
    try:
        data = request.get_json()
    except Exception:
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')
    if 'custom_id' not in data or not data['custom_id']:
        data['custom_id'] = get_unique_short_id()
        while URLMap.query.filter_by(short=data['custom_id']).first():
            data['custom_id'] = get_unique_short_id()
    else:
        custom_id = data['custom_id']
        if not match(r'[a-zA-Z0-9]{1,16}$', custom_id):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if URLMap.query.filter_by(short=custom_id).first():
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
    urlmap = URLMap()
    urlmap.from_dict(data)
    db.session.add(urlmap)
    db.session.commit()
    urlmap_dict = urlmap.to_dict()
    return jsonify(
        {
            'url': urlmap_dict['url'],
            'short_link': f'{request.host_url}{urlmap_dict["short_link"]}'
        }
    ), 201
