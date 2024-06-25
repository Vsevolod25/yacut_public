from datetime import datetime
from http import HTTPStatus
from random import choices
from re import match
from string import ascii_letters, digits

from flask import url_for

from . import db
from .constants import (
    MAX_LENGTH_SHORT,
    MAX_LENGTH_URL,
    MIN_LENGTH_SHORT,
    REDIRECT_VIEW,
    SHORT_REGULAR_EXPRESSION
)
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

    def filter_by_short(self, short_id):
        return self.query.filter_by(short=short_id).first()

    def get_unique_short_id(self):
        short_id = ''.join(choices(ascii_letters + digits, k=6))
        while self.filter_by_short(short_id):
            short_id = ''.join(choices(ascii_letters + digits, k=6))
        return short_id

    def create_urlmap(self, original, custom_id, api=False):
        if api:
            self.validate_urlmap(original, custom_id)
        if not custom_id:
            custom_id = self.get_unique_short_id()
        else:
            if self.filter_by_short(custom_id):
                raise ValidationError(
                    'Предложенный вариант короткой ссылки уже существует.'
                )
        urlmap = URLMap(original=original, short=custom_id)
        db.session.add(urlmap)
        db.session.commit()
        return urlmap.to_dict()

    def validate_urlmap(self, original, custom_id):
        if not original:
            raise ValidationError(
                '"url" является обязательным полем!'
            )
        if custom_id:
            if (
                (not match(SHORT_REGULAR_EXPRESSION, custom_id)) |
                (len(custom_id) not in range(
                    MIN_LENGTH_SHORT, MAX_LENGTH_SHORT + 1
                ))
            ):
                raise ValidationError(
                    'Указано недопустимое имя для короткой ссылки'
                )
        return custom_id

    def get_urlmap(self, short_id):
        urlmap = self.filter_by_short(short_id)
        if not urlmap:
            raise InvalidAPIUsage(
                'Указанный id не найден', HTTPStatus.NOT_FOUND
            )
        return urlmap
