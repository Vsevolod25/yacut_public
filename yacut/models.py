from datetime import datetime
from re import match

from . import db
from .constants import MAX_LENGTH_SHORT, MAX_LENGTH_URL
from .error_handlers import InvalidShortNameException, RepeatedShortException
from .functions import get_unique_short_id


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
            short_link=self.short,
            timestamp=self.timestamp
        )

    def create_urlmap(self, original, short=None):
        if short:
            if URLMap.query.filter_by(short=short).first():
                raise RepeatedShortException
            if not match(r'[a-zA-Z0-9]{1,16}$', short):
                raise InvalidShortNameException
        else:
            short = get_unique_short_id()
            while URLMap.query.filter_by(short=short).first():
                short = get_unique_short_id()
        urlmap = URLMap(original=original, short=short)
        db.session.add(urlmap)
        db.session.commit()
        return urlmap.to_dict()

    def get_urlmap(self, short):
        return self.query.filter_by(short=short).first()
