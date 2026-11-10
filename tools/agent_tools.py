import os
import re
import ssl
import socket
import shutil
import subprocess
import urllib.request
import urllib.error
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKSPACE = os.path.join(ROOT, "workspace")
os.makedirs(WORKSPACE, exist_ok=True)

def clean_host(value):
    value = value.strip()
    if "://" in value:
        value = urlparse(value).hostname or ""
    value = value.split("/")[0].split(":")[0].strip().lower()
    if not value or len(value) > 253:
        raise ValueError("Enter a valid hostname.")
    if not re.fullmatch(r"[a-z0-9.-]+", value):
        raise ValueError("Invalid hostname characters.")
    if value.startswith(".") or value.endswith("."):
        raise ValueError("Invalid hostname.")
    return value

def dns_lookup(target):
    host = clean_host(target)
    try:
        results = socket.getaddrinfo(host, None)
        addresses = sorted(set(item[4][0] for item in results))
        return "DNS RESULTS FOR " + host + "\n" + "\n".join(addresses)
    except Exception as e:
        return "DNS lookup failed: " + str(e)

def http_headers(target):
    host = clean_host(target)
    url = "https://" + host + "/"
    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "VERNTY-ONE/3.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            lines = ["HTTP STATUS: " + str(response.status)]
            lines += [str(k) + ": " + str(v) for k, v in response.headers.items()]
            return "\n".join(lines)
    except urllib.error.HTTPError as e:
        lines = ["HTTP STATUS: " + str(e.code)]
        lines += [str(k) + ": " + str(v) for k, v in e.headers.items()]
        return "\n".join(lines)
    except Exception as e:
        return "HTTPS header check failed: " + str(e)

def tls_check(target):
    host = clean_host(target)
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as secure:
                cert = secure.getpeercert()
                return (
                    "TLS CONNECTION: SUCCESS\n"
                    "HOST: " + host + "\n"
                    "TLS VERSION: " + str(secure.version()) + "\n"
                    "CERTIFICATE SUBJECT: " + str(cert.get("subject")) + "\n"
                    "CERTIFICATE EXPIRY: " + str(cert.get("notAfter"))
                )
    except Exception as e:
        return "TLS check failed: " + str(e)

def nmap_scan(target, authorized=False):
    if not authorized:
        return "Scan cancelled. Explicit authorization is required."
    host = clean_host(target)
    binary = shutil.which("nmap")
    if not binary:
        return "Nmap is not installed. Install it with: pkg install nmap"
    try:
        result = subprocess.run(
            [binary, "-F", "-T2", "-Pn", host],
            capture_output=True, text=True, timeout=35
        )
        return (result.stdout or result.stderr or "No scan output.")[:7000]
    except subprocess.TimeoutExpired:
        return "Scan stopped: time limit reached."
    except Exception as e:
        return "Nmap error: " + str(e)

def create_python_file(filename, code):
    filename = os.path.basename(filename.strip())
    if not filename.endswith(".py"):
        filename += ".py"
    if not re.fullmatch(r"[A-Za-z0-9_-]+\.py", filename):
        return "Invalid filename. Use letters, numbers, underscores or hyphens."
    if len(code) > 20000:
        return "Code is too large. Limit: 20,000 characters."

    path = os.path.join(WORKSPACE, filename)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        return "Python file created:\n" + path
    except Exception as e:
        return "File creation failed: " + str(e)

def check_python_file(filename):
    filename = os.path.basename(filename.strip())
    if not re.fullmatch(r"[A-Za-z0-9_-]+\.py", filename):
        return "Invalid Python filename."
    path = os.path.join(WORKSPACE, filename)
    if not os.path.isfile(path):
        return "File not found: " + path
    try:
        with open(path, encoding="utf-8") as f:
            source = f.read()
        compile(source, path, "exec")
        return "SYNTAX CHECK PASSED\n" + path
    except SyntaxError as e:
        return "SYNTAX ERROR: line " + str(e.lineno) + ": " + str(e.msg)
    except Exception as e:
        return "Check failed: " + str(e)
