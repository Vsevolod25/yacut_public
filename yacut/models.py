from datetime import datetime
from re import match

from sqlalchemy.orm import validates

from . import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), nullable=False)
    short = db.Column(db.String(16), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())

    @validates('short')
    def validate_email(self, key, short):
        assert match(r'[a-zA-Z0-9]{1,16}$', short)
        return short

    def from_dict(self, data):
        setattr(self, 'original', data['url'])
        setattr(self, 'short', data['custom_id'])

    def to_dict(self):
        return dict(
            id=self.id,
            url=self.original,
            short_link=self.short,
            timestamp=self.timestamp
        )
