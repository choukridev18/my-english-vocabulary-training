import sqlite3
import os
from functools import wraps
from flask import Flask, request, jsonify, render_template, g, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "vocab-training-secret-2026-x9z"
DB_PATH = os.path.join(os.path.dirname(__file__), "vocabulary.db")


# ─── DB helpers ───────────────────────────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                username   TEXT    NOT NULL UNIQUE,
                email      TEXT    NOT NULL UNIQUE,
                password   TEXT    NOT NULL,
                role       TEXT    NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS words (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                english    TEXT    NOT NULL,
                french     TEXT    NOT NULL,
                mastered   INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, english)
            );

            CREATE TABLE IF NOT EXISTS quiz_sessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                correct    INTEGER DEFAULT 0,
                incorrect  INTEGER DEFAULT 0,
                mode       TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        # Migration : add role column if it doesn't exist yet
        cols = [r[1] for r in db.execute("PRAGMA table_info(users)").fetchall()]
        if "role" not in cols:
            db.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'")
            db.commit()


# ─── Auth decorator ───────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Connecte-toi pour accéder à cette page.", "warning")
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Connecte-toi pour accéder à cette page.", "warning")
            return redirect(url_for("login_page"))
        if session.get("role") != "admin":
            flash("Accès réservé à l'administrateur.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# ─── Auth routes ──────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register_page():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email",    "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm  = request.form.get("confirm",  "").strip()

        if not username or not email or not password:
            flash("Tous les champs sont obligatoires.", "error")
        elif "@" not in email or "." not in email.split("@")[-1]:
            flash("Adresse email invalide.", "error")
        elif len(password) < 6:
            flash("Le mot de passe doit faire au moins 6 caractères.", "error")
        elif password != confirm:
            flash("Les mots de passe ne correspondent pas.", "error")
        else:
            try:
                db = get_db()
                # First user registered becomes admin automatically
                user_count = db.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
                role = "admin" if user_count == 0 else "user"
                db.execute(
                    "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                    (username, email, generate_password_hash(password), role)
                )
                db.commit()
                user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                session["user_id"]  = user["id"]
                session["username"] = user["username"]
                session["role"]     = user["role"]
                flash(f"Bienvenue {username} ! Ton compte est créé.", "success")
                return redirect(url_for("index"))
            except sqlite3.IntegrityError as e:
                if "username" in str(e):
                    flash("Ce pseudo est déjà pris.", "error")
                else:
                    flash("Cette adresse email est déjà utilisée.", "error")

        # Re-render form with already-typed values so user doesn't retype everything
        return render_template("register.html", form_username=username, form_email=email)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        db   = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

        if not user or not check_password_hash(user["password"], password):
            flash("Pseudo ou mot de passe incorrect.", "error")
        else:
            session["user_id"]  = user["id"]
            session["username"] = user["username"]
            session["role"]     = user["role"]
            flash(f"Bon retour {user['username']} !", "success")
            return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Tu es déconnecté.", "info")
    return redirect(url_for("login_page"))


@app.route("/forgot", methods=["GET", "POST"])
def forgot_page():
    found_user = None
    form_email = ""

    if request.method == "POST":
        action = request.form.get("action", "lookup")
        email  = request.form.get("email", "").strip().lower()
        form_email = email
        db     = get_db()

        if action == "lookup":
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if user:
                found_user = {"username": user["username"], "email": email}
            else:
                flash("Aucun compte associé à cet email.", "error")

        elif action == "reset":
            new_password = request.form.get("new_password", "").strip()
            confirm      = request.form.get("confirm_password", "").strip()
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
            if not user:
                flash("Email introuvable.", "error")
            elif len(new_password) < 6:
                flash("Le mot de passe doit faire au moins 6 caractères.", "error")
                found_user = {"username": user["username"], "email": email}
            elif new_password != confirm:
                flash("Les mots de passe ne correspondent pas.", "error")
                found_user = {"username": user["username"], "email": email}
            else:
                db.execute(
                    "UPDATE users SET password = ? WHERE email = ?",
                    (generate_password_hash(new_password), email)
                )
                db.commit()
                flash("Mot de passe réinitialisé avec succès ! Tu peux te connecter.", "success")
                return redirect(url_for("login_page"))

    return render_template("forgot.html", found_user=found_user, form_email=form_email)


@app.route("/settings")
@login_required
def settings_page():
    return render_template("settings.html")


@app.route("/settings/username", methods=["POST"])
@login_required
def change_username():
    new_username = request.form.get("new_username", "").strip()
    password     = request.form.get("password", "").strip()
    uid          = session["user_id"]
    db           = get_db()
    user         = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()

    if not check_password_hash(user["password"], password):
        flash("Mot de passe incorrect.", "error")
    elif not new_username:
        flash("Le pseudo ne peut pas être vide.", "error")
    elif new_username == user["username"]:
        flash("C'est déjà ton pseudo actuel.", "error")
    else:
        try:
            db.execute("UPDATE users SET username = ? WHERE id = ?", (new_username, uid))
            db.commit()
            session["username"] = new_username
            flash(f"Pseudo changé en « {new_username} » avec succès !", "success")
        except sqlite3.IntegrityError:
            flash("Ce pseudo est déjà pris.", "error")
    return redirect(url_for("settings_page"))


@app.route("/settings/delete-account", methods=["POST"])
@login_required
def delete_account():
    uid = session["user_id"]
    db  = get_db()
    db.execute("DELETE FROM words WHERE user_id = ?", (uid,))
    db.execute("DELETE FROM quiz_sessions WHERE user_id = ?", (uid,))
    db.execute("DELETE FROM users WHERE id = ?", (uid,))
    db.commit()
    session.clear()
    flash("Ton compte a été supprimé définitivement.", "info")
    return redirect(url_for("register_page"))


@app.route("/settings/password", methods=["POST"])
@login_required
def change_password():
    current  = request.form.get("current_password", "").strip()
    new_pwd  = request.form.get("new_password",     "").strip()
    confirm  = request.form.get("confirm_password", "").strip()
    uid      = session["user_id"]
    db       = get_db()
    user     = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()

    if not check_password_hash(user["password"], current):
        flash("Mot de passe actuel incorrect.", "error")
    elif len(new_pwd) < 6:
        flash("Le nouveau mot de passe doit faire au moins 6 caractères.", "error")
    elif new_pwd != confirm:
        flash("Les mots de passe ne correspondent pas.", "error")
    else:
        db.execute("UPDATE users SET password = ? WHERE id = ?",
                   (generate_password_hash(new_pwd), uid))
        db.commit()
        flash("Mot de passe changé avec succès !", "success")
    return redirect(url_for("settings_page"))# ─── UI Routes ────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/add")
@login_required
def add_page():
    return render_template("add.html")


@app.route("/training")
@login_required
def training_page():
    return render_template("training.html")


@app.route("/list")
@login_required
def list_page():
    db    = get_db()
    uid   = session["user_id"]
    words = db.execute("SELECT * FROM words WHERE user_id=? ORDER BY english ASC", (uid,)).fetchall()
    stats = _get_stats(db, uid)
    return render_template("list.html", words=words, stats=stats)


# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route("/api/words", methods=["GET"])
@login_required
def api_get_words():
    db    = get_db()
    uid   = session["user_id"]
    words = db.execute("SELECT * FROM words WHERE user_id=? ORDER BY english ASC", (uid,)).fetchall()
    return jsonify([dict(w) for w in words])


@app.route("/api/words", methods=["POST"])
@login_required
def api_add_word():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corps JSON manquant"}), 400

    english = data.get("english", "").strip().lower()
    french  = data.get("french",  "").strip().lower()

    if not english or not french:
        return jsonify({"error": "Les champs english et french sont obligatoires"}), 400

    try:
        db     = get_db()
        uid    = session["user_id"]
        cursor = db.execute(
            "INSERT INTO words (user_id, english, french) VALUES (?, ?, ?)",
            (uid, english, french)
        )
        db.commit()
        return jsonify({"id": cursor.lastrowid, "english": english, "french": french, "mastered": 0}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Ce mot existe déjà dans ta liste"}), 409


@app.route("/api/words/<int:word_id>", methods=["DELETE"])
@login_required
def api_delete_word(word_id):
    db     = get_db()
    uid    = session["user_id"]
    result = db.execute("DELETE FROM words WHERE id=? AND user_id=?", (word_id, uid))
    db.commit()
    if result.rowcount == 0:
        return jsonify({"error": "Mot introuvable"}), 404
    return jsonify({"message": "Mot supprimé"}), 200


@app.route("/api/words/<int:word_id>/master", methods=["PATCH"])
@login_required
def api_toggle_master(word_id):
    db   = get_db()
    uid  = session["user_id"]
    word = db.execute("SELECT * FROM words WHERE id=? AND user_id=?", (word_id, uid)).fetchone()
    if not word:
        return jsonify({"error": "Mot introuvable"}), 404
    new_status = 0 if word["mastered"] else 1
    db.execute("UPDATE words SET mastered=? WHERE id=? AND user_id=?", (new_status, word_id, uid))
    db.commit()
    return jsonify({"id": word_id, "mastered": new_status}), 200


@app.route("/api/words/quiz", methods=["GET"])
@login_required
def api_get_quiz_words():
    db    = get_db()
    uid   = session["user_id"]
    words = db.execute(
        "SELECT * FROM words WHERE user_id=? AND mastered=0 ORDER BY RANDOM()", (uid,)
    ).fetchall()
    return jsonify([dict(w) for w in words])


@app.route("/api/quiz/save", methods=["POST"])
@login_required
def api_save_quiz():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corps JSON manquant"}), 400

    db  = get_db()
    uid = session["user_id"]
    db.execute(
        "INSERT INTO quiz_sessions (user_id, correct, incorrect, mode) VALUES (?, ?, ?, ?)",
        (uid, data.get("correct", 0), data.get("incorrect", 0), data.get("mode", "mix"))
    )
    db.commit()
    return jsonify({"message": "Session sauvegardée"}), 201


@app.route("/api/stats", methods=["GET"])
@login_required
def api_get_stats():
    return jsonify(_get_stats(get_db(), session["user_id"]))


@app.route("/api/words/reset", methods=["DELETE"])
@login_required
def api_reset_words():
    db  = get_db()
    uid = session["user_id"]
    db.execute("DELETE FROM words WHERE user_id=?", (uid,))
    db.execute("DELETE FROM quiz_sessions WHERE user_id=?", (uid,))
    db.commit()
    return jsonify({"message": "Base réinitialisée"}), 200


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_stats(db, user_id):
    total    = db.execute("SELECT COUNT(*) as c FROM words WHERE user_id=?", (user_id,)).fetchone()["c"]
    mastered = db.execute("SELECT COUNT(*) as c FROM words WHERE user_id=? AND mastered=1", (user_id,)).fetchone()["c"]
    row      = db.execute(
        "SELECT SUM(correct) as c, SUM(correct+incorrect) as t FROM quiz_sessions WHERE user_id=?",
        (user_id,)
    ).fetchone()
    correct_total  = row["c"] or 0
    total_questions = row["t"] or 0
    success_rate   = round(correct_total / total_questions * 100, 1) if total_questions > 0 else 0
    return {
        "total_words":     total,
        "mastered_words":  mastered,
        "success_rate":    success_rate,
        "total_questions": int(total_questions),
    }


# ─── Admin routes ─────────────────────────────────────────────────────────────

@app.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()
    users = db.execute("""
        SELECT u.id, u.username, u.email, u.role, u.created_at,
               COUNT(DISTINCT w.id)  AS word_count,
               COUNT(DISTINCT q.id)  AS quiz_count
        FROM users u
        LEFT JOIN words w         ON w.user_id = u.id
        LEFT JOIN quiz_sessions q ON q.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at ASC
    """).fetchall()

    global_stats = db.execute("""
        SELECT
            (SELECT COUNT(*) FROM users)         AS total_users,
            (SELECT COUNT(*) FROM words)          AS total_words,
            (SELECT COUNT(*) FROM quiz_sessions)  AS total_sessions
    """).fetchone()

    return render_template("admin.html", users=users, stats=global_stats)


@app.route("/admin/users/<int:uid>/delete", methods=["POST"])
@admin_required
def admin_delete_user(uid):
    if uid == session["user_id"]:
        flash("Tu ne peux pas supprimer ton propre compte depuis l'admin.", "error")
        return redirect(url_for("admin_dashboard"))
    db = get_db()
    user = db.execute("SELECT username FROM users WHERE id = ?", (uid,)).fetchone()
    if user:
        db.execute("DELETE FROM users WHERE id = ?", (uid,))
        db.commit()
        flash(f"Compte « {user['username']} » supprimé.", "success")
    else:
        flash("Utilisateur introuvable.", "error")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/users/<int:uid>/toggle-role", methods=["POST"])
@admin_required
def admin_toggle_role(uid):
    if uid == session["user_id"]:
        flash("Tu ne peux pas modifier ton propre rôle.", "error")
        return redirect(url_for("admin_dashboard"))
    db   = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    if not user:
        flash("Utilisateur introuvable.", "error")
        return redirect(url_for("admin_dashboard"))
    new_role = "user" if user["role"] == "admin" else "admin"
    db.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, uid))
    db.commit()
    flash(f"« {user['username']} » est maintenant {new_role}.", "success")
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5002)
