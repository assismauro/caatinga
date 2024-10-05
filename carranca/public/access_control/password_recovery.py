"""
    *Password Recovery*
    Part of Public Access Control Processes

    Equipe da Canoa -- 2024
    mgd
"""
# cSpell:ignore tmpl passwordrecovery wtforms

from flask import render_template, request
import secrets

from ...helpers.db_helper import persist_record
from ...helpers.email_helper import send_email
from ...helpers.error_helper import ModuleErrorCode
from ...helpers.ui_texts_helper import add_msg_error, add_msg_success
from ...helpers.route_helper import (
    public_route,
    init_form_vars,
    get_input_text,
    is_external_ip_ready,
    get_account_form_data,
    public_route__password_reset,
)
from ..models import Users, get_user_where
from ..wtforms import PasswordRecoveryForm


def password_recovery():
    from ...Shared import shared as shared

    task_code = ModuleErrorCode.ACCESS_CONTROL_PW_RECOVERY.value
    tmpl_form, template, tmpl_form, texts = init_form_vars()
    try:
        task_code += 1  # 1
        tmpl_form = PasswordRecoveryForm(request.form)
        task_code += 1  # 2
        template, is_get, texts = get_account_form_data('passwordrecovery')
        task_code += 1  # 3
        send_to = '' if is_get else get_input_text('user_email').lower()
        task_code += 1  # 4
        record_to_update = None if is_get else get_user_where(email=send_to)

        if is_get:
            pass
        elif record_to_update is None:
            add_msg_error('emailNotRegistered', texts)
        elif not is_external_ip_ready(shared.app_config):
            add_msg_error('noExternalIP', texts)
        else:
            task_code += 1  # 5
            token = secrets.token_urlsafe()
            task_code += 1  # 6
            url = f"http://{shared.app_config.SERVER_EXTERNAL_IP}{shared.app_config.SERVER_EXTERNAL_PORT}{public_route(public_route__password_reset, token= token)}"
            task_code += 1  # 7
            send_email(send_to, 'passwordRecovery_email', {'url': url})
            task_code += 1  # 8
            record_to_update.recover_email_token = token
            task_code += 1  # 9
            persist_record(record_to_update, task_code)
            add_msg_success('emailSent', texts)
            task_code = 0
    except Exception as e:  # TODO: log
        msg = add_msg_error('errorPasswordRecovery', texts, task_code)
        print(f"{e} - {msg}")

    return render_template(template, form=tmpl_form, **texts)

# eof
