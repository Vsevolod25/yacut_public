from datetime import datetime
from http import HTTPStatus
from random import choices
from re import match
from string import ascii_letters, digits

from flask import url_for

from . import db
from .constants import MAX_LENGTH_SHORT, MAX_LENGTH_URL, REDIRECT_VIEW
from .error_handlers import InvalidAPIUsage, ValidationError


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(MAX_LENGTH_URL), nullable=False)
    short = db.Column(
        db.String(MAX_LENGTH_SHORT), unique=True, nullable=False
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())

    def to_dict(self):
        return dict(
            id=self.id,
            url=self.original,
            short_link=url_for(
                REDIRECT_VIEW, short_id=self.short, _external=True
            )[:-1],
            timestamp=self.timestamp
        )

    def get_unique_short_id(self):
        short_id = ''.join(choices(ascii_letters + digits, k=6))
        while URLMap.query.filter_by(short=short_id).first():
            short_id = ''.join(choices(ascii_letters + digits, k=6))
        return short_id

    def create_urlmap(self, original, custom_id, api=False):
        if not custom_id:
            custom_id = self.get_unique_short_id()
        else:
            if api:
                self.validate_custom_id(custom_id)
            if URLMap.query.filter_by(short=custom_id).first():
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
        urlmap = URLMap(original=original, short=custom_id)
        db.session.add(urlmap)
        db.session.commit()
        return urlmap.to_dict()

    def validate_custom_id(self, custom_id):
        if not match(r'[a-zA-Z0-9]{1,16}$', custom_id):
            raise ValidationError(
                'Указано недопустимое имя для короткой ссылки'
            )
        return custom_id

    def get_urlmap(self, short_id):
        urlmap = self.query.filter_by(short=short_id).first()
        if not urlmap:
            raise InvalidAPIUsage(
                'Указанный id не найден', HTTPStatus.NOT_FOUND
            )
        return urlmap
