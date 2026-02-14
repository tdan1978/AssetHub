import ssl
from typing import Any

from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException
from ldap3.utils.conv import escape_filter_chars


def build_server(config):
    return Server(config.host, port=config.port, use_ssl=config.use_ssl, get_info=ALL)


def bind_service(config):
    server = build_server(config)
    conn = Connection(server, user=config.bind_dn or None, password=config.bind_password or None, auto_bind=False)
    conn.open()
    if config.use_starttls and not config.use_ssl:
        conn.start_tls()
    if not conn.bind():
        result = conn.result or {}
        message = result.get("message") or result.get("description") or "LDAP bind failed"
        raise LDAPException(message)
    return conn


def build_user_filter(config, username: str | None = None) -> str:
    base = config.user_filter or "(objectClass=user)"
    if username is None:
        return base
    safe_username = escape_filter_chars(username)
    if "{username}" in base:
        return base.replace("{username}", safe_username)
    return f"(&{base}({config.username_attr}={safe_username}))"


def search_users(config) -> list[Any]:
    conn = bind_service(config)
    attrs = list({
        config.username_attr,
        config.display_name_attr,
        config.email_attr,
        config.phone_attr,
        config.dept_attr,
    })
    user_filter = build_user_filter(config)
    conn.search(search_base=config.base_dn, search_filter=user_filter, search_scope=SUBTREE, attributes=attrs)
    entries = conn.entries
    conn.unbind()
    return entries


def search_user(config, username: str):
    conn = bind_service(config)
    attrs = list({
        config.username_attr,
        config.display_name_attr,
        config.email_attr,
        config.phone_attr,
        config.dept_attr,
    })
    user_filter = build_user_filter(config, username=username)
    conn.search(search_base=config.base_dn, search_filter=user_filter, search_scope=SUBTREE, attributes=attrs)
    entry = conn.entries[0] if conn.entries else None
    conn.unbind()
    return entry


def authenticate_user(config, username: str, password: str):
    entry = search_user(config, username)
    if not entry:
        return None
    server = build_server(config)
    user_dn = entry.entry_dn
    user_conn = Connection(server, user=user_dn, password=password, auto_bind=False)
    user_conn.open()
    if config.use_starttls and not config.use_ssl:
        user_conn.start_tls()
    if not user_conn.bind():
        return None
    user_conn.unbind()
    return entry


def extract_attr(entry, attr: str) -> str | None:
    if not entry or not attr:
        return None
    try:
        value = entry[attr].value
    except Exception:
        value = None
    if isinstance(value, list):
        return value[0] if value else None
    return value
