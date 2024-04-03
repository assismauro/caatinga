# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
#mgd from flask import render_template, request, Markup
from flask import render_template
from flask_login import login_required
from jinja2 import TemplateNotFound
from apps.home import helper
import apps.home.logHelper as logHelper
from apps.home.texts import get_text

log = logHelper.Log2Database()

# ============= Index ============== #
@blueprint.route('/index')
# @login_required não pode ter, index é 'livre', depende do menu
def index():
    return render_template('home/index.html', pageTitle='Home')


# ============= Documents ============== #
@blueprint.route('/docs/<docName>')
def docs(docName):
    group= 'document_part'
    base= docName
    template= f'{base}_{{}}'
    body= get_text(template.format('body'), group)
    style= get_text(template.format('style'), group)

    return render_template('home/documentDisplay.html',  **{'documentTitle': f'{docName} Document', 'documentStyle': style, 'documentBody': body })


