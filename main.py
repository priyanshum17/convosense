from flask import Flask, render_template
from flask_socketio import SocketIO
from core.control.database import db
from core.routes.auth import auth_bp
from core.sockets.handlers import socketio
from flask import send_from_directory

app = Flask(__name__, static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)
socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet')

app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, port=5005)