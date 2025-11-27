import os
import subprocess
import datetime
from flask import Flask, render_template, jsonify, send_from_directory, request

app = Flask(__name__, static_folder="static", template_folder="templates")

ROOT = os.path.abspath(os.getcwd())            # /app inside container
CERTS_DIR = os.path.join(ROOT, "certs")
LOG_DIR = os.path.join(ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "pki.log")

# ensure dirs
os.makedirs(CERTS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(os.path.join(CERTS_DIR, "intermediate"), exist_ok=True)
os.makedirs(os.path.join(CERTS_DIR, "server"), exist_ok=True)

ALLOWED_EXT = {".pem", ".crt", ".cer", ".csr"}

def log(msg):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    line = f"{ts} {msg}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

def run_script(script_name):
    """Run script in app folder; return dict"""
    script_path = os.path.join(ROOT, script_name)
    log(f"Виклик скрипта: {script_name}")
    try:
        proc = subprocess.run(
            ["python", script_path],
            capture_output=True, text=True, cwd=ROOT, check=False
        )
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        if proc.returncode == 0:
            log(f"OK {script_name}: {out}")
            return {"ok": True, "out": out}
        else:
            log(f"ERR {script_name}: {err or out}")
            return {"ok": False, "out": err or out}
    except Exception as e:
        log(f"EXC {script_name}: {e}")
        return {"ok": False, "out": str(e)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/run/<action>", methods=["POST"])
def api_run(action):
    # map action to script filename
    mapping = {
        "create_root": "init_root_ca.py",
        "create_intermediate": "init_intermediate_ca.py",
        "create_server": "generate_server_cert.py",
        "create_client": "generate_client_cert.py"
    }
    script = mapping.get(action)
    if not script:
        return jsonify({"ok": False, "out": "Невідома дія"}), 400
    result = run_script(script)
    return jsonify(result)

@app.route("/api/list_certs", methods=["GET"])
def list_certs():
    files = []
    # only include allowed extensions and produce relative paths
    for rootdir, _, filenames in os.walk(CERTS_DIR):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in ALLOWED_EXT:
                full = os.path.join(rootdir, fn)
                rel = os.path.relpath(full, CERTS_DIR).replace("\\", "/")
                files.append(rel)
    files.sort()
    return jsonify(files)

@app.route("/certs/<path:filename>")
def get_cert(filename):
    # prevent path traversal
    safe = os.path.normpath(filename)
    if safe.startswith(".."):
        return "Forbidden", 403
    full = os.path.join(CERTS_DIR, safe)
    if not os.path.exists(full):
        return "Not found", 404
    directory = os.path.dirname(full)
    fname = os.path.basename(full)
    return send_from_directory(directory, fname, as_attachment=True)

@app.route("/api/logs")
def api_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify({"ok": True, "log": ""})
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return jsonify({"ok": True, "log": f.read()})

if __name__ == "__main__":
    # production: host 0.0.0.0
    app.run(host="0.0.0.0", port=5000)
