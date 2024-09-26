"""
    Model of the table of files uploaded by users

    mgd
    Equipe da Canoa -- 2024
    cSpell:ignore cuser
"""

# Equipe da Canoa -- 2024
#
# cSpell:ignore: nullable psycopg2

from psycopg2 import DatabaseError

from carranca import db Trocar com app_db de shared
from carranca.shared import app_log
from carranca.helpers.db_helper import persist_record, check_connection


class UserDataFiles(db.Model):
    __tablename__ = "user_data_files"

    id = db.Column(db.Integer, primary_key=True)
    ticket = db.Column(db.String(40), unique=True)
    id_users = db.Column(db.Integer)   # fk

    app_version = db.Column(db.String(12))
    process_version = db.Column(db.String(12))

    file_name = db.Column(db.String(80))
    original_name = db.Column(db.String(80), nullable=True, default=None)
    file_size = db.Column(db.Integer)
    file_crc32 = db.Column(db.Integer)
    from_os = db.Column(db.String(1))
    file_origin = db.Column(db.String(1))
    user_receipt = db.Column(db.String(14))

    # Process module
    ## saved at register.py
    a_received_at = db.Column(db.DateTime)
    b_process_started_at = db.Column(db.DateTime)
    c_check_started_at = db.Column(db.DateTime)
    d_register_started_at = db.Column(db.DateTime)
    ## saved at email.py
    e_unzip_started_at = db.Column(db.DateTime)
    f_submit_started_at = db.Column(db.DateTime)
    g_email_started_at = db.Column(db.DateTime)

    z_process_end_at = db.Column(db.DateTime)

    # event
    ## saved at email.py
    email_sent = db.Column(db.Boolean, default=False)
    report_ready_at = db.Column(db.DateTime)

    # Set on trigger
    # registered_at, at insert
    # email_sent_at, at email_sent = T
    # error_at, at error_code not 0

    # obsolete
    # upload_start_at = db.Column(db.DateTime)

    error_code = db.Column(db.Integer, nullable=True)
    error_msg = db.Column(db.String(200), nullable=True)
    error_text = db.Column(db.Text, nullable=True)
    success_text = db.Column(db.Text, nullable=True)


    def _get_record(uTicket):
        ''' gets the record with unique Key uTicket '''
        # this query also opens a connection, so persist_record works nice
        check_connection()
        records = db.session.query(UserDataFiles).filter_by(ticket=uTicket)
        if (records is None) or (records.count() == 0):
            record = None
        elif records.count() == 1:
            record= records.first()
        else:
            raise KeyError(f"The ticket {uTicket} return several records, expecting only one.")

        return record

    def _save(record, **kwargs) -> None:
        for attr, value in kwargs.items():
            if value is not None:
                setattr(record, attr, value)

        persist_record(db, record)
        return

    def _ins_or_upd(isInsert: bool, uTicket: str, **kwargs) -> None:
        try:
            msg_exists= f"The ticket '{uTicket}' is " + "{0} registered."
            isUpdate = not isInsert
            record_to_ins_or_upd= UserDataFiles._get_record(uTicket)
            if isUpdate and record_to_ins_or_upd is None:
                raise KeyError(msg_exists.format('not'))
            elif isInsert and record_to_ins_or_upd is not None:
                raise KeyError(msg_exists.format('already'))
            elif isInsert:
                record_to_ins_or_upd = UserDataFiles(ticket=uTicket)

            UserDataFiles._save(record_to_ins_or_upd, **kwargs)
        except Exception as e:
            operation = 'update' if isUpdate else 'insert to'
            msg_error = f"Cannot {operation} {UserDataFiles.__tablename__}.ticket = {uTicket} | Error {e}."
            app_log.error(msg_error)
            raise DatabaseError(msg_error)

    def insert(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(True, uTicket, **kwargs)

    def update(uTicket: str, **kwargs) -> None:
        UserDataFiles._ins_or_upd(False, uTicket, **kwargs)

# eof
