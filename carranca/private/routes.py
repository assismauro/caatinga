"""
    *Routes*
    Private Routes
    This routes are private, users _must be_ logged

    Equipe da Canoa -- 2024
    mgd
"""
# cSpell: ignore werkzeug wtforms receivefile tmpl

from flask import Blueprint, render_template
from flask_login import login_required

from ..helpers.pw_helper import internal_logout, nobody_is_logged
from ..helpers.route_helper import (
    bp_name,
    base_route_private,
    get_private_form_data,
    login_route,
    redirect_to,
)


# === module variables ====================================
bp_private = Blueprint(bp_name(base_route_private), base_route_private, url_prefix="")

# === Test _ route ========================================
@bp_private.route("/test_route")
def  test_route():
    from ..helpers.dwnLd_goo_helper import download_public_google_file

    i= download_public_google_file(
        # "https://drive.google.com/file/d/1iXyDi-NcGIobY0NY-fOQ34Ew-gcS0PzY/view?usp=sharing" #zip com pw
        # 'https://drive.google.com/file/d/1k4fW92-QGwp9SfMdHEE4WIFkKMJla763/view?usp=sharing'   #zipped
          "https://drive.google.com/file/d/1H0BfjYJrf0p_ehqDoUH0wXIJzbAXwUKd/view?usp=sharing" # argow.zipped
        ,"./uploaded_files/"
    )
    return str(i)

# === routes =============================================
@bp_private.route("/home")
def home():
    """
    `home` page is the _landing page_
     for *users* (logged visitors).

    It displays the main menu.
    """

    if nobody_is_logged():
        return redirect_to(login_route(), None)

    template, _, texts = get_private_form_data("home")
    return render_template(template, **texts)


@login_required
@bp_private.route("/receivefile", methods=["GET", "POST"])
def receivefile():
    """
    Through this route, the user sends a zip file or a URL for validation.

    If it passes the simple validations confronted in receive_file.py,
    it is unzipped and sent to data_validate
    (see module `data_validate`).
    The report generated by `data_validate` is sent by e-mail and
    a result message is displayed to the user.

    Part of Canoa `Data Validation` Processes
    """
    if nobody_is_logged():
        return redirect_to(login_route())
    else:
        from .receive_file import receive_file
        return receive_file()


@login_required
@bp_private.route("/changepassword", methods=["GET", "POST"])
def changepassword():
    """
    `changepassword` page, as it's name
    implies, allows the user to change
    is password, for what ever reason
    at all or none.
    Whew! That's four lines :--)
    """

    if nobody_is_logged():
        return redirect_to(login_route())
    else:
        from .access_control.password_change import do_password_change
        return do_password_change()


@bp_private.route("/logout")
def logout():
    """
    Logout the current user
    and the page is redirect to
    login
    """
    internal_logout()
    return redirect_to(login_route())


# eof
