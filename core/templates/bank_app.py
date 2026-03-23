from flask import Flask, request, session, redirect, url_for, render_template_string, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change_this_secret"
DB = "bank.db"

BASE_HTML = '''
<!doctype html>
<html>
<head><meta charset="utf-8"><title>Bank App</title></head>
<body>
  <h2>{{ title }}</h2>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <ul>{% for m in messages %}<li>{{ m }}</li>{% endfor %}</ul>
    {% endif %}
  {% endwith %}
  {{ body|safe }}
  <hr>
  <a href="/">Inicio</a>
  {% if session.get('user_id') %}
    | <a href="/dashboard">Dashboard</a>
    | <a href="/logout">Salir</a>
  {% endif %}
</body>
</html>
'''

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = conn()
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS accounts(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      balance REAL NOT NULL DEFAULT 0,
      FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS transactions(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      account_id INTEGER NOT NULL,
      type TEXT NOT NULL,
      amount REAL NOT NULL,
      note TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY(account_id) REFERENCES accounts(id)
    );
    ''')
    c.commit()
    c.close()

def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    c = conn()
    u = c.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    c.close()
    return u

def account_by_user(user_id):
    c = conn()
    a = c.execute("SELECT * FROM accounts WHERE user_id=?", (user_id,)).fetchone()
    c.close()
    return a

@app.route("/")
def home():
    if current_user():
        return redirect(url_for("dashboard"))
    body = '''
    <a href="/register">Crear cuenta</a><br>
    <a href="/login">Iniciar sesion</a>
    '''
    return render_template_string(BASE_HTML, title="Bank App", body=body)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 6:
            flash("Usuario minimo 3 chars y password minimo 6.")
            return redirect(url_for("register"))
        c = conn()
        try:
            c.execute(
                "INSERT INTO users(username,password_hash,created_at) VALUES(?,?,?)",
                (username, generate_password_hash(password), datetime.utcnow().isoformat()),
            )
            uid = c.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()["id"]
            c.execute("INSERT INTO accounts(user_id,balance) VALUES(?,?)", (uid, 0))
            c.commit()
            flash("Cuenta creada. Ahora inicia sesion.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Usuario ya existe.")
        finally:
            c.close()
    body = '''
    <form method="post">
      Usuario: <input name="username"><br>
      Password: <input name="password" type="password"><br>
      <button>Registrar</button>
    </form>
    '''
    return render_template_string(BASE_HTML, title="Registro", body=body)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        c = conn()
        u = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        c.close()
        if not u or not check_password_hash(u["password_hash"], password):
            flash("Credenciales invalidas.")
            return redirect(url_for("login"))
        session["user_id"] = u["id"]
        return redirect(url_for("dashboard"))
    body = '''
    <form method="post">
      Usuario: <input name="username"><br>
      Password: <input name="password" type="password"><br>
      <button>Entrar</button>
    </form>
    '''
    return render_template_string(BASE_HTML, title="Login", body=body)

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesion cerrada.")
    return redirect(url_for("home"))

@app.route("/dashboard")
def dashboard():
    u = current_user()
    if not u:
        return redirect(url_for("login"))
    a = account_by_user(u["id"])
    body = f'''
    <p>Usuario: <b>{u["username"]}</b></p>
    <p>Saldo actual: <b>{a["balance"]:.2f}</b></p>
    <a href="/deposit">Depositar</a><br>
    <a href="/withdraw">Retirar</a><br>
    <a href="/transfer">Transferir</a><br>
    <a href="/history">Historial</a><br>
    '''
    return render_template_string(BASE_HTML, title="Dashboard", body=body)

def add_tx(account_id, ttype, amount, note):
    c = conn()
    c.execute(
        "INSERT INTO transactions(account_id,type,amount,note,created_at) VALUES(?,?,?,?,?)",
        (account_id, ttype, amount, note, datetime.utcnow().isoformat()),
    )
    c.commit()
    c.close()

@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    u = current_user()
    if not u:
        return redirect(url_for("login"))
    a = account_by_user(u["id"])
    if request.method == "POST":
        amount = float(request.form.get("amount", "0"))
        if amount <= 0:
            flash("Monto invalido.")
            return redirect(url_for("deposit"))
        c = conn()
        c.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", (amount, a["id"]))
        c.commit()
        c.close()
        add_tx(a["id"], "deposit", amount, "Deposito")
        flash("Deposito aplicado.")
        return redirect(url_for("dashboard"))
    body = '<form method="post">Monto: <input name="amount" type="number" step="0.01"><button>Depositar</button></form>'
    return render_template_string(BASE_HTML, title="Deposito", body=body)

@app.route("/withdraw", methods=["GET", "POST"])
def withdraw():
    u = current_user()
    if not u:
        return redirect(url_for("login"))
    a = account_by_user(u["id"])
    if request.method == "POST":
        amount = float(request.form.get("amount", "0"))
        if amount <= 0 or amount > a["balance"]:
            flash("Monto invalido o saldo insuficiente.")
            return redirect(url_for("withdraw"))
        c = conn()
        c.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", (amount, a["id"]))
        c.commit()
        c.close()
        add_tx(a["id"], "withdraw", amount, "Retiro")
        flash("Retiro aplicado.")
        return redirect(url_for("dashboard"))
    body = '<form method="post">Monto: <input name="amount" type="number" step="0.01"><button>Retirar</button></form>'
    return render_template_string(BASE_HTML, title="Retiro", body=body)

@app.route("/transfer", methods=["GET", "POST"])
def transfer():
    u = current_user()
    if not u:
        return redirect(url_for("login"))
    src = account_by_user(u["id"])
    if request.method == "POST":
        target_username = request.form.get("target", "").strip()
        amount = float(request.form.get("amount", "0"))
        if amount <= 0 or amount > src["balance"]:
            flash("Monto invalido o saldo insuficiente.")
            return redirect(url_for("transfer"))
        c = conn()
        tgt_user = c.execute("SELECT id FROM users WHERE username=?", (target_username,)).fetchone()
        if not tgt_user:
            c.close()
            flash("Usuario destino no existe.")
            return redirect(url_for("transfer"))
        tgt_acc = c.execute("SELECT id FROM accounts WHERE user_id=?", (tgt_user["id"],)).fetchone()
        c.execute("UPDATE accounts SET balance = balance - ? WHERE id=?", (amount, src["id"]))
        c.execute("UPDATE accounts SET balance = balance + ? WHERE id=?", (amount, tgt_acc["id"]))
        c.commit()
        c.close()
        add_tx(src["id"], "transfer_out", amount, f"A {target_username}")
        add_tx(tgt_acc["id"], "transfer_in", amount, f"De {u['username']}")
        flash("Transferencia realizada.")
        return redirect(url_for("dashboard"))
    body = '''
    <form method="post">
      Usuario destino: <input name="target"><br>
      Monto: <input name="amount" type="number" step="0.01"><br>
      <button>Transferir</button>
    </form>
    '''
    return render_template_string(BASE_HTML, title="Transferencia", body=body)

@app.route("/history")
def history():
    u = current_user()
    if not u:
        return redirect(url_for("login"))
    a = account_by_user(u["id"])
    c = conn()
    rows = c.execute(
        "SELECT type, amount, note, created_at FROM transactions WHERE account_id=? ORDER BY id DESC LIMIT 100",
        (a["id"],),
    ).fetchall()
    c.close()
    lines = ["<ul>"]
    for r in rows:
        lines.append(f"<li>{r['created_at']} | {r['type']} | {r['amount']:.2f} | {r['note'] or ''}</li>")
    lines.append("</ul>")
    return render_template_string(BASE_HTML, title="Historial", body="".join(lines))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
