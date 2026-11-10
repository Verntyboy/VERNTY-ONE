import os
import json
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(ROOT, "memory", "vernty.db")
CONFIG = os.path.join(ROOT, "memory", "config.json")

MODES = {
    "general": "You are VERNTY ONE, a friendly, practical personal AI assistant created by Vernty Boy. Be useful, honest and concise.",
    "code": "You are VERNTY DEVELOPER. Help with Python, websites, debugging and Termux. Give complete, copy-ready code. Consider Android 10 and limited phone resources. Never claim code was run unless verified.",
    "security": "You are VERNTY SECURITY. Teach defensive cybersecurity, DNS, HTTP, TLS and authorized testing. Only assist with systems the user owns or has permission to test. Never facilitate credential theft or unauthorized access.",
    "creator": "You are VERNTY CREATOR. Produce original engaging TikTok scripts, African mystery stories, hooks, voiceovers, captions, scene directions and video prompts.",
    "research": "You are VERNTY RESEARCHER. Explain topics carefully, distinguish facts from uncertainty, and never invent sources or claim to have browsed the live web."
}

def database():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    with sqlite3.connect(DB) as con:
        con.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created TEXT NOT NULL
        )""")

def save(role, content):
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO messages(role,content,created) VALUES(?,?,?)",
            (role, content, datetime.now().isoformat())
        )

def history(limit=40):
    with sqlite3.connect(DB) as con:
        rows = con.execute(
            "SELECT role,content FROM messages ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

def local_tool(message):
    q = message.lower().strip()
    if q in ("help", "/help"):
        return (
            "VERNTY ONE COMMANDS\n"
            "/code [task] - Developer mode\n"
            "/security [task] - Security mode\n"
            "/creator [task] - Creator mode\n"
            "/research [task] - Research mode\n"
            "status - System status\n"
            "time - Phone time\n"
            "help - Commands"
        )
    if q in ("status", "/status"):
        return (
            "VERNTY ONE 3.0\n"
            "Dashboard: Ready\n"
            "SQLite memory: Active\n"
            "Online AI: " + ("Configured" if os.environ.get("GROQ_API_KEY") or os.path.isfile(CONFIG) else "Not configured") + "\n"
            "Agent modes: " + str(len(MODES)) + "\n"
            "Local tools: DNS / HTTP / TLS / Python file tools\n"
            "Nmap: " + ("Installed" if __import__("shutil").which("nmap") else "Not installed")
        )
    if q in ("time", "/time"):
        return "Phone time: " + datetime.now().astimezone().isoformat()
    return None

def online_ai(message, mode="general"):
    try:
        api_key = os.environ.get("GROQ_API_KEY", "").strip()

        if api_key:
            cfg = {
                "url": os.environ.get(
                    "GROQ_API_URL",
                    "https://api.groq.com/openai/v1/chat/completions"
                ),
                "model": os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b"),
                "key": api_key
            }
        else:
            with open(CONFIG, encoding="utf-8") as f:
                cfg = json.load(f)

        messages = [{"role": "system", "content": MODES.get(mode, MODES["general"])}]
        messages.extend(history(6)[:-1])
        messages.append({"role": "user", "content": message})

        payload = json.dumps({
            "model": cfg["model"],
            "messages": messages,
            "temperature": 0.6,
            "max_completion_tokens": 900
        }).encode("utf-8")

        req = urllib.request.Request(
            cfg["url"], data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "VERNTY-ONE/3.0 Android Termux",
                "Authorization": "Bearer " + cfg["key"]
            }
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        return "AI API ERROR " + str(e.code) + ": " + detail[:1000]
    except Exception as e:
        return "AI CONNECTION ERROR: " + str(e)

def chat(message):
    message = str(message).strip()[:4000]
    if not message:
        return "Please enter a message."

    mode = "general"
    original = message
    for prefix, selected in (
        ("/code ", "code"),
        ("/security ", "security"),
        ("/creator ", "creator"),
        ("/research ", "research")
    ):
        if message.lower().startswith(prefix):
            mode = selected
            message = message[len(prefix):].strip()
            break

    save("user", original)
    answer = local_tool(message) if mode == "general" else None
    if answer is None:
        answer = online_ai(message, mode)
    save("assistant", answer)
    return answer

database()


def clear_history():
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM messages")
        con.commit()
