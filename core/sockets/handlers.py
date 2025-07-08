from flask_socketio import SocketIO, emit
from flask import request
from core.control.database import db, User, Message
from datetime import datetime

socketio = SocketIO()

active_users = {}

@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.is_active = True
            user.last_active = datetime.utcnow()
            db.session.commit()
            active_users[user_id] = request.sid
            emit('user_status', {'user_id': user_id, 'is_active': True}, broadcast=True)
            print(f"User {user.username} connected")
        else:
            print(f"Invalid user_id {user_id} on connect")
    else:
        print("Anonymous user connected")

@socketio.on('disconnect')
def handle_disconnect():
    user_id_to_remove = None
    for user_id, sid in active_users.items():
        if sid == request.sid:
            user_id_to_remove = user_id
            break

    if user_id_to_remove:
        user = User.query.get(user_id_to_remove)
        if user:
            user.is_active = False
            db.session.commit()
            del active_users[user_id_to_remove]
            emit('user_status', {'user_id': user_id_to_remove, 'is_active': False}, broadcast=True)
            print(f"User {user.username} disconnected")
    else:
        print("Anonymous user disconnected")

@socketio.on('message')
def handle_message(data):
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    content = data.get('content')

    if not all([sender_id, receiver_id, content]):
        print("Invalid message data")
        return

    message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.session.add(message)
    db.session.commit()

    # Emit to receiver if online
    if str(receiver_id) in active_users:
        emit('new_message', {
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'content': content,
            'timestamp': message.timestamp.isoformat()
        }, room=active_users[str(receiver_id)])
    
    # Emit to sender for confirmation/display
    emit('message_sent', {
        'sender_id': sender_id,
        'receiver_id': receiver_id,
        'content': content,
        'timestamp': message.timestamp.isoformat()
    }, room=request.sid)

    print(f"Message from {sender_id} to {receiver_id}: {content}")

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