"""
   Equipe da Canoa -- 2024

   textsHelper.py
   Retrieve ui texts item for current language
   (refactored from helper.py)
   mgd 2024-04-03

"""

# cSpell:ignore getDictResultset dbquery connstr adaptabrasil

from .dbQuery import getValues, getDictResultset
from .py_helper import is_str_none_or_empty


# see below defs:
#  get_text      returns the `text` column of table ui_items (for a given `name`/`section``)
#  get_section   returns an dic[str,str] of columns `name` & `text` of table ui_items (for a given `section`)
#
#  get_msg_error returns the `text` column of table ui_items (for a given `name` of section 'sec_Error')

#   get_msg_error, add_msg_success, add_msg_error
#


# === local var ===========================================

msg_error= 'msgError'
msg_success= 'msgSuccess'


# Local vars
user_locale = 'pt-br'   # TODO:  browser || user property
msg_not_found = "Message '{0}' (not registered §: {1})"

# see table ui_sections.name
# this two sections are special (id=1 & id=2):
#  they group all msgError and msgSuccess
sec_Error = 'secError'
sec_Success = 'secSuccess'

# === local def ===========================================

def _get_select(cols: str, section: str, item: str = None):
    # returns Select query for the current locale, section and, eventually, for only one item
    # use SQL lower(item) better than item.lower (use db locale)
    item_filter = "" if item is None else f" and (item_lower = lower('{item}'))"
    # ** /!\ ******************************************************************
    #  don't use <schema>.table_name. Must set
    #  ALTER ROLE canoa_connstr IN DATABASE adaptabrasil SET search_path=canoa;
    query = (
        f"select {cols} from vw_ui_texts "
        f"where "
        f"(locale = '{user_locale}') and (section_lower = lower('{section}')){item_filter};"
    )
    return query


# returns tuple(text, title) for the item/section pair
def _get_row(item: str, section: str) -> tuple[str, str]:
    select = _get_select("text, title", section, item)
    result = getValues(select)
    return ("", "") if result == None else result

# returns text for the item/section pair & adds/replace name:(key, value) to the dictionary
def _add_msg(item: str, section: str, name: str, texts: dict[str, str] = None, *args) -> str:
    s = get_text(item, section)
    try:
        value = '' if s is None else (s.format(*args) if args else s)
    except:
        value = s

    if texts:
        texts[name] = value

    return value

def _texts_init():
    # initialize 'msg_not_found' str
    text, _ = _get_row('messageNotFound', sec_Error)
    mnf =  msg_not_found if is_str_none_or_empty(text) else text
    return mnf

# === public ==============================================

# TODO: returns a dict<string, string> with the HTML info except for.. not ready, still working...
def get_html(section: str) -> dict[str, str]:
    imgList = get_text('images', section);
    # filter if not is_str_none_or_empty(imgList)
    # select item, text from vw_ui_texts v where v.section_lower = 'html_file' and item not in ('image3.png',  'image4.png')
    query = _get_select("item, text", section)
    return getDictResultset(query)

def get_section(section: str) -> dict[str, str]:
    # returns a dict<string, string>
    query = _get_select("item, text", section)
    return getDictResultset(query)

def get_text(item: str, section: str) -> str:
    # returns text for the item/section pair. if not found, a `warning message`
    text, _ = _get_row(item, section)
    if is_str_none_or_empty(text):
        text =  msg_not_found.format(item, section)
    return text

def add_msg_error(item: str, texts: dict[str, str] = None, *args) -> str:
    # returns text for the item/'sec_Error' pair and adds pair to texts => texts.add( text, 'msgError')
    return _add_msg(item, sec_Error, msg_error, texts, *args)

def add_msg_success(item: str, texts: dict[str, str] = None, *args) -> str:
    """
        returns `text` for the [item, 'sec_Success'] pair
        (of the vw_ui_texts wonderful view)
        and adds the pair to `texts` => texts.add(text, 'msgSuccess')
    """
    return _add_msg(item, sec_Success, msg_success, texts, *args)

def get_msg_error(item: str) -> str:
    # returns text for the item/'sec_Error' pair, adds the pair to texts => texts.add( text, 'msgError')
    return add_msg_error(item)

msg_not_found = _texts_init()

# eof