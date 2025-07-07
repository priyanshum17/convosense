from core.database.users import UserLedger, create, get_by_username
from core.database.messages import Message, send, inbox


def main():
    test_user = UserLedger(username="test_user", password="secret123")
    try:
        created_user = create(test_user)
        print("User created:", created_user)
    except Exception as e:
        print("User creation failed:", e)
        created_user = get_by_username("test_user")
        print("Loaded existing user:", created_user)

    message = Message(
        sender_id=created_user.user_id,
        receiver_id=created_user.user_id,
        content="Hello, this is a test message!",
    )

    sent_msg = send(message)
    print("✉️ Sent message:", sent_msg)

    inbox_messages = inbox(created_user.user_id)
    print(f"📥 Inbox for {created_user.username}:")
    for msg in inbox_messages:
        print("-", msg)


if __name__ == "__main__":
    main()
