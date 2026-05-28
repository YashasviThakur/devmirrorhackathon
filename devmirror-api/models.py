"""
DevMirror — SQLAlchemy ORM models with Fernet encryption for OAuth tokens.
Database: SQLite (devmirror.db) in development, overridable via DATABASE_URL.
"""

import os
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey,
    CheckConstraint, create_engine, TypeDecorator,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, validates

# ── Encryption engine ──────────────────────────────────────────────────────────
_raw_key = os.getenv("FERNET_KEY", "")
if not _raw_key:
    _generated = Fernet.generate_key()
    print(
        f"[DevMirror] WARNING: FERNET_KEY not set. "
        f"Using ephemeral key — tokens will not survive restarts.\n"
        f"[DevMirror] Generated key (add to .env): {_generated.decode()}"
    )
    _fernet = Fernet(_generated)
else:
    _fernet = Fernet(_raw_key.encode() if isinstance(_raw_key, str) else _raw_key)


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy column type that transparently applies Fernet symmetric encryption.
    Values are encrypted before INSERT/UPDATE and decrypted on SELECT.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return _fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return _fernet.decrypt(value.encode()).decode()
        except (InvalidToken, Exception):
            return None


# ── ORM Base ───────────────────────────────────────────────────────────────────
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "account_type IN ('personal', 'institution')",
            name="chk_account_type",
        ),
    )

    id               = Column(Integer, primary_key=True, index=True)
    email            = Column(String, unique=True, index=True, nullable=False)
    password_hash    = Column(String, nullable=True)
    account_type     = Column(String, nullable=False, default="personal")
    institution_name = Column(String, nullable=True)
    goal_1           = Column(String, nullable=True)
    goal_2           = Column(String, nullable=True)
    goal_3           = Column(String, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    linked_accounts = relationship(
        "LinkedAccount",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @validates("account_type")
    def validate_account_type(self, key, value):
        if value not in ("personal", "institution"):
            raise ValueError(
                f"account_type must be 'personal' or 'institution', got '{value}'"
            )
        return value


class LinkedAccount(Base):
    __tablename__ = "linked_accounts"

    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    # Plain-text handles (non-sensitive)
    codeforces_handle = Column(String, nullable=True)
    leetcode_username = Column(String, nullable=True)

    # Google OAuth2 tokens — encrypted at rest via EncryptedString
    google_access_token  = Column(EncryptedString, nullable=True)
    google_refresh_token = Column(EncryptedString, nullable=True)
    google_token_scope   = Column(EncryptedString, nullable=True)
    google_token_expiry  = Column(DateTime, nullable=True)

    # GitHub OAuth2 tokens — encrypted at rest via EncryptedString
    github_access_token  = Column(EncryptedString, nullable=True)
    github_refresh_token = Column(EncryptedString, nullable=True)
    github_token_scope   = Column(EncryptedString, nullable=True)
    github_token_expiry  = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="linked_accounts")


# ── Database session factory ───────────────────────────────────────────────────
DATABASE_URL   = os.getenv("DATABASE_URL", "sqlite:///./devmirror.db")
_connect_args  = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine         = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal   = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
