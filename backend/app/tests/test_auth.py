from app.auth.security import create_access_token, decode_access_token, hash_password, verify_password

def test_password_hash_round_trip():
    password = "StrongPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)

def test_jwt_round_trip():
    token = create_access_token("123")
    assert decode_access_token(token) == "123"
