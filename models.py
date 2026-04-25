from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sent_emails = db.relationship(
        "Email", foreign_keys="Email.sender_id", backref="sender", lazy=True
    )
    received_emails = db.relationship(
        "Email", foreign_keys="Email.recipient_id", backref="recipient", lazy=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Email(db.Model):
    __tablename__ = "emails"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Spam classification results
    spam_label = db.Column(db.String(10))
    spam_confidence = db.Column(db.Float)
    spam_reasons = db.Column(db.Text)
    spam_risk_flags = db.Column(db.Text)
    spam_safe_summary = db.Column(db.Text)

    def __repr__(self):
        return f"<Email {self.id} from={self.sender_id} to={self.recipient_id}>"
