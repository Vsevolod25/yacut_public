from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp, URL

from .constants import MAX_LENGTH_URL, MIN_LENGTH_URL


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[
            DataRequired(message='Обязательное поле'),
            URL(message='Введите ссылку'),
            Length(
                MIN_LENGTH_URL,
                MAX_LENGTH_URL,
                message=(
                    'Ссылка не должна быть длиннее '
                    f'{MAX_LENGTH_URL} символов.'
                )
            )
        ]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Regexp(
                regex=r'[a-zA-Z0-9]{1,16}$',
                message=(
                    'Допускаются только символы, не нарушающие формат ссылки'
                )
            ),
            Optional()
        ]
    )
    submit = SubmitField('Добавить')
