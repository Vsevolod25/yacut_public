from flask import flash, redirect, render_template

from . import app
from .error_handlers import ValidationError
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
    except ValidationError:
        flash(
            'Предложенный вариант короткой ссылки уже существует.',
            'repeated_short'
        )
        return render_template('create_short.html', form=form)
    flash('Ваша новая ссылка готова:\n', 'success')
    flash(f'{urlmap_dict["short_link"]}', 'short')
    return render_template('create_short.html', form=form)


@app.route('/<short_id>/', strict_slashes=False)
def redirect_view(short_id):
    urlmap = URLMap().query.filter_by(short=short_id).first_or_404()
    return redirect(urlmap.original)
