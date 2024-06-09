from flask import abort, flash, redirect, render_template, url_for

from . import app
from .error_handlers import RepeatedShortException
from .forms import URLMapForm
from .models import URLMap


@app.route('/', methods=['GET', 'POST'])
def main_view():
    form = URLMapForm()
    if not form.validate_on_submit():
        return render_template('create_short.html', form=form)
    try:
        urlmap_dict = URLMap().create_urlmap(
            form.original_link.data, form.custom_id.data
        )
    except RepeatedShortException:
        flash(
            'Предложенный вариант короткой ссылки уже существует.',
            'repeated_short'
        )
        return render_template('create_short.html', form=form)
    flash('Ваша новая ссылка готова:\n', 'success')
    flash(
        f'''{
            url_for("redirect_view",
            short_id=urlmap_dict["short_link"],
            _external=True)[:-1]
        }''',
        'short'
    )
    return render_template('create_short.html', form=form)


@app.route('/<short_id>/', strict_slashes=False)
def redirect_view(short_id):
    urlmap = URLMap().get_urlmap(short_id)
    if urlmap:
        return redirect(urlmap.original)
    abort(404)
