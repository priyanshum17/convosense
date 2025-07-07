from core.database.users import UserLedger, create, get_by_username
from core.database.messages import Message, send, inbox



test_user = UserLedger(username="weast_user", password="secret123")
try:
        created_user = create(test_user)
        print("User created:", created_user)
except Exception as e:
        print("User creation failed:", e)
        created_user = get_by_username("test_user")
        print("Loaded existing user:", created_user)