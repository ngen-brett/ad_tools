import os
import getpass
import socket
import ssl
from dotenv import load_dotenv
from ldap3 import Server, Connection, ALL, NTLM, SIMPLE, Tls

# Load environment variables from .env
load_dotenv()

BASE_DN             = os.getenv('BASE_DN')
DOMAIN              = os.getenv('DOMAIN')
LDAP_SERVER         = os.getenv('LDAP_SERVER')
BIND_USER_DN        = os.getenv('BIND_USER_DN')
BIND_USER_UPN       = os.getenv('BIND_USER_UPN')
BIND_USER_DN_SUFFIX = os.getenv('BIND_USER_DN_SUFFIX')

def prompt_credentials():
    """
    Prompt for bind credentials, supporting full DN, UPN, or interactive input.
    Returns a tuple (bind_identity, password).
    """
    password = getpass.getpass("Bind password: ")

    if BIND_USER_DN:
        return BIND_USER_DN, password
    if BIND_USER_UPN:
        return BIND_USER_UPN, password

    default_user = getpass.getuser()
    user = input(f"Bind user [{default_user}]: ").strip() or default_user

    if BIND_USER_DN_SUFFIX:
        dn = f"CN={user},{BIND_USER_DN_SUFFIX}"
        return dn, password

    upn = f"{user}@{DOMAIN}"
    return upn, password

def discover_dc_simple(domain: str) -> str:
    """
    Discover a domain controller by trying common hostnames.
    """
    patterns = [f"dc.{domain}", f"dc1.{domain}", f"ad.{domain}", f"ldap.{domain}", domain]
    for host in patterns:
        try:
            socket.gethostbyname(host)
            return f"ldap://{host}"
        except socket.gaierror:
            continue
    raise RuntimeError(f"Could not discover DC for {domain}. Set LDAP_SERVER in .env.")

def get_connection():
    """
    Establish LDAP connection, ignoring LDAPS cert verification.
    """
    if not BASE_DN:
        raise ValueError("BASE_DN must be set in .env")
    if not DOMAIN and not LDAP_SERVER:
        raise ValueError("Either DOMAIN or LDAP_SERVER must be set in .env")

    server_url = LDAP_SERVER or discover_dc_simple(DOMAIN)
    print(f"Connecting to: {server_url}")

    use_ssl = server_url.lower().startswith('ldaps://')
    tls_config = Tls(validate=ssl.CERT_NONE) if use_ssl else None

    server = Server(server_url, use_ssl=use_ssl, get_info=ALL, tls=tls_config)
    bind_id, pwd = prompt_credentials()

    auth = NTLM if '\\' in bind_id and '@' not in bind_id else SIMPLE

    try:
        conn = Connection(server, user=bind_id, password=pwd, authentication=auth, auto_bind=True)
        print(f"Connected via {auth} as {bind_id}")
        return conn
    except Exception as err:
        print(f"{auth} bind failed: {err}")
        if auth == NTLM and 'MD4' in str(err):
            print("Install pycryptodome for NTLM: pip install pycryptodome")
        raise

def search(conn, search_filter: str, attributes):
    """
    Perform LDAP search under BASE_DN.
    """
    conn.search(search_base=BASE_DN, search_filter=search_filter, attributes=attributes)
    return conn.entries

