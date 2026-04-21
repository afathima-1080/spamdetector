import json
import logging
import os

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from urllib.parse import urlparse, urljoin

from models import Email, User, db
from spam_detector import classify_email

load_dotenv()

logger = logging.getLogger(__name__)

app = Flask(__name__)
_secret_key = os.environ.get("SECRET_KEY")
if not _secret_key:
    logger.warning(
        "SECRET_KEY environment variable is not set. "
        "Using an insecure default — do not use this in production."
    )
app.config["SECRET_KEY"] = _secret_key or "dev-secret-key-change-me"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql://localhost/spamdetector"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def _is_safe_redirect_url(target: str) -> bool:
    """Return True only when *target* resolves to the same host as the app."""
    host_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and host_url.netloc == test_url.netloc


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("inbox"))
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("inbox"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next", "")
            # Guard against open-redirect: only follow same-host relative paths
            if next_page and _is_safe_redirect_url(next_page):
                return redirect(next_page)
            return redirect(url_for("inbox"))
        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("inbox"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        error = None
        if not username:
            error = "Username is required."
        elif not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif password != confirm:
            error = "Passwords do not match."
        elif User.query.filter_by(username=username).first():
            error = "Username already taken."
        elif User.query.filter_by(email=email).first():
            error = "Email already registered."

        if error:
            flash(error, "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Inbox
# ---------------------------------------------------------------------------

@app.route("/inbox")
@login_required
def inbox():
    emails = (
        Email.query.filter_by(recipient_id=current_user.id)
        .order_by(Email.sent_at.desc())
        .all()
    )
    return render_template("inbox.html", emails=emails)


# ---------------------------------------------------------------------------
# Compose
# ---------------------------------------------------------------------------

@app.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    spam_result = None
    form_data = {}

    if request.method == "POST":
        recipient_username = request.form.get("recipient", "").strip()
        subject = request.form.get("subject", "").strip()
        body = request.form.get("body", "").strip()
        action = request.form.get("action", "send")

        form_data = {
            "recipient": recipient_username,
            "subject": subject,
            "body": body,
        }

        error = None
        recipient = None
        if not recipient_username:
            error = "Recipient is required."
        elif not subject:
            error = "Subject is required."
        elif not body:
            error = "Body is required."
        else:
            recipient = User.query.filter_by(username=recipient_username).first()
            if not recipient:
                error = f"User '{recipient_username}' not found."

        if error:
            flash(error, "danger")
            return render_template("compose.html", spam_result=None, form_data=form_data)

        # Run spam classification
        try:
            result = classify_email(body)
            spam_result = {
                "label": result.label,
                "confidence": result.confidence,
                "reasons": result.reasons,
                "risk_flags": result.risk_flags,
                "safe_summary": result.safe_summary,
            }
        except Exception as exc:
            logger.error("Spam classification failed: %s", exc)
            flash("Spam detection service is currently unavailable. Email will be sent without classification.", "warning")
            spam_result = None

        if action == "check":
            # Just show the result, don't send yet
            return render_template(
                "compose.html", spam_result=spam_result, form_data=form_data
            )

        # action == "send" — save and deliver
        email = Email(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            subject=subject,
            body=body,
            spam_label=spam_result["label"] if spam_result else None,
            spam_confidence=spam_result["confidence"] if spam_result else None,
            spam_reasons=json.dumps(spam_result["reasons"]) if spam_result else None,
            spam_risk_flags=json.dumps(spam_result["risk_flags"]) if spam_result else None,
            spam_safe_summary=spam_result["safe_summary"] if spam_result else None,
        )
        db.session.add(email)
        db.session.commit()
        flash("Email sent successfully!", "success")
        return redirect(url_for("inbox"))

    return render_template("compose.html", spam_result=spam_result, form_data=form_data)


# ---------------------------------------------------------------------------
# Email detail
# ---------------------------------------------------------------------------

@app.route("/email/<int:email_id>")
@login_required
def email_detail(email_id):
    email = Email.query.get_or_404(email_id)

    # Only sender or recipient may view the email
    if email.sender_id != current_user.id and email.recipient_id != current_user.id:
        flash("You do not have permission to view this email.", "danger")
        return redirect(url_for("inbox"))

    reasons = json.loads(email.spam_reasons) if email.spam_reasons else []
    risk_flags = json.loads(email.spam_risk_flags) if email.spam_risk_flags else []

    return render_template(
        "email_detail.html",
        email=email,
        reasons=reasons,
        risk_flags=risk_flags,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
