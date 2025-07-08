# ─────────────────────── core/sockets/handlers.py ────────────────────────────
from datetime import datetime
from flask import request
from flask_socketio import SocketIO, emit
from core.control.database import db, User, Message

socketio = SocketIO()
active_users: dict[str, str] = {}  # user_id → sid

@socketio.on("connect")
def handle_connect():
    """Mark user as active, broadcast status, then push any undelivered messages."""
    user_id = request.args.get("user_id")

    if not user_id:
        print("Anonymous user connected")
        return

    user = User.query.get(user_id)
    if not user:
        print(f"Invalid user_id {user_id} on connect")
        return

    user.is_active  = True
    user.last_active = datetime.utcnow()
    db.session.commit()
    active_users[str(user_id)] = request.sid

    emit("user_status", {"user_id": user_id, "is_active": True}, broadcast=True)
    print(f"User {user.username} connected")

    undelivered = (
        Message.query
        .filter_by(receiver_id=user_id, delivered=False)
        .order_by(Message.timestamp)
        .all()
    )
    for m in undelivered:
        emit(
            "new_message",
            {
                "sender_id":   m.sender_id,
                "receiver_id": m.receiver_id,
                "content":     m.content,
                "timestamp":   m.timestamp.isoformat(),
            },
            room=request.sid,
        )
        m.delivered = True
    if undelivered:
        db.session.commit()


@socketio.on("message")
def handle_message(data: dict):
    """Store message, confirm to sender, deliver immediately if receiver online."""
    sender_id   = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    content     = data.get("content")

    if not all([sender_id, receiver_id, content]):
        print("Invalid message data")
        return

    message = Message(
        sender_id  = sender_id,
        receiver_id= receiver_id,
        content    = content,
    )
    db.session.add(message)
    db.session.commit()

    if str(receiver_id) in active_users:
        emit(
            "new_message",
            {
                "sender_id":   sender_id,
                "receiver_id": receiver_id,
                "content":     content,
                "timestamp":   message.timestamp.isoformat(),
            },
            room=active_users[str(receiver_id)],
        )
        message.delivered = True
        db.session.commit()

    emit(
        "message_sent",
        {
            "sender_id":   sender_id,
            "receiver_id": receiver_id,
            "content":     content,
            "timestamp":   message.timestamp.isoformat(),
        },
        room=request.sid,
    )

    print(f"Message {sender_id} → {receiver_id}: {content}")


@socketio.on('get_active_users')
def get_active_users():
    active_user_ids = [int(uid) for uid in active_users.keys()]
    users = User.query.filter(User.id.in_(active_user_ids)).all()
    active_user_list = [{'id': user.id, 'username': user.username} for user in users]
    emit('active_users_list', active_user_list)
    print("Active users requested")

@socketio.on('get_user_status')
def get_user_status(data):
    user_id = data.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            emit('user_status', {'user_id': user_id, 'is_active': user.is_active})
        else:
            print(f"User {user_id} not found for status check")
    else:
        print("No user_id provided for status check")

@socketio.on("get_all_users")
def get_all_users_socket():
    """Return every user (active or not) over Socket.IO."""
    users = User.query.with_entities(User.id, User.username, User.is_active).all()
    emit(
        "all_users_list",
        [
            {"id": u.id, "username": u.username, "is_active": u.is_active}
            for u in users
        ],
    )