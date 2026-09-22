import pytest
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_verification_logic():
    hashed = pwd_context.hash("secret123")
    assert pwd_context.verify("secret123", hashed) is True
    assert pwd_context.verify("wrong_password", hashed) is False
