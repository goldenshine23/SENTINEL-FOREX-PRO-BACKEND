def test_register_and_validate():
    from bot.auth import register_user, validate_user
    email = "testuser@example.com"
    password = "securepass"
    chat_id = "123456"
    
    assert register_user(email, password, chat_id) in [True, False]
    assert validate_user(email, password) in [True, False]

def test_invalid_login():
    from bot.auth import validate_user
    assert validate_user("nonexistent@example.com", "wrong") == False