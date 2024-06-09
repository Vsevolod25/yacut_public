from random import choices
from string import ascii_letters, digits

from flask import abort, flash, redirect, request, render_template

from . import app, db
from .forms import URLMapForm
from .models import URLMap


def get_unique_short_id():
    return ''.join(choices(ascii_letters + digits, k=6))


@app.route('/', methods=['GET', 'POST'])
def main_view():
    form = URLMapForm()
    if form.validate_on_submit():
        short = form.custom_id.data
        if short:
            if URLMap.query.filter_by(short=short).first():
                flash(
                    'Предложенный вариант короткой ссылки уже существует.',
                    'repeated_short'
                )
                return render_template('create_short.html', form=form)
        else:
            short = get_unique_short_id()
            while URLMap.query.filter_by(short=short).first():
                short = get_unique_short_id()
        urlmap = URLMap(
            original=form.original_link.data,
            short=short,
        )
        db.session.add(urlmap)
        db.session.commit()
        flash('Ваша новая ссылка готова:\n', 'success')
        flash(f'{request.host_url}{short}', 'short')
    return render_template('create_short.html', form=form)


@app.route('/<short_id>/', strict_slashes=False)
def redirect_view(short_id):
    urlmap = URLMap.query.filter_by(short=short_id).first()
    if urlmap:
        return redirect(urlmap.original)
    abort(404)
