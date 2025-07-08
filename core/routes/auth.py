from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from core.control.database import db, User
from core.sockets.handlers import socketio 

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    user.is_active = True
    db.session.commit()

    return jsonify({'message': 'Logged in successfully', 'user_id': user.id}), 200

@auth_bp.route("/delete_user", methods=["DELETE"])
def delete_user():
    data      = request.get_json()
    username  = data.get("username")
    password  = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid credentials"}), 401

    user_id = user.id
    db.session.delete(user)
    db.session.commit()

    # let every socket client update its roster
    socketio.emit("user_deleted", {"user_id": user_id}, broadcast=True)

    return jsonify({"message": "User deleted successfully"}), 200



@auth_bp.route("/users", methods=["GET"])
def list_users():
    """Return every user that currently exists (REST flavour)."""
    users = User.query.with_entities(User.id, User.username, User.is_active).all()
    return jsonify(
        [{"id": u.id, "username": u.username, "is_active": u.is_active} for u in users]
    ), 200
