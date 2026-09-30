from app.auth.security import create_access_token, decode_access_token, hash_password, verify_password

def test_password_hashing():
    raw = "StrongPassword123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed)
    assert not verify_password("wrong", hashed)

def test_access_token_round_trip():
    token = create_access_token("42")
    assert decode_access_token(token) == "42"
