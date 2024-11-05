from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity

from werkzeug.security import check_password_hash

from app.extensions import db, login_manager
from app.models import User, ExpiredToken
from app.forms import LoginForm
from app.helpers.db_helpers import db_connection, create_table

from datetime import datetime, timezone

current_track = None # this will hold the current track in memory

login_bp = Blueprint('login', __name__)
api_bp = Blueprint('api', __name__)
jwt_bp = Blueprint('jwt', __name__)

connection = db_connection()
create_table(connection)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_bp.route('/')
def index():
    return render_template('index.html')

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('login.dashboard'))
        flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)

@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.index'))

@login_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template(
        'dashboard.html',
        name=current_user.username
    )

@jwt_bp.route('/api/token', methods=['POST'])
def create_token():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

    access_token = create_access_token(identity=user_data)
    refresh_token = create_refresh_token(identity=user_data)
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

# create a route to refresh the JWT token
@jwt_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    user_data = get_jwt_identity()
    new_access_token = create_access_token(identity=user_data)

    return jsonify(access_token=new_access_token), 200

# create a route that allows a user to revoke their own token
@jwt_bp.route('/api/revoke', methods=['POST'])
@jwt_required(verify_type=False)
def invalidate():
    jti = get_jwt()["jti"]
    exp_timestamp = get_jwt()["exp"]
    expires_at = datetime.fromtimestamp(exp_timestamp, timezone.utc)

    # add the token to the blacklist
    revoked_token = ExpiredToken(jti=jti, expires_at=expires_at)
    db.session.add(revoked_token)
    db.session.commit()

    return jsonify({'msg': 'Token revoked successfully'}), 200

@api_bp.route('/api/song-update', methods=['POST'])
@jwt_required()
def update_song():
    global current_track
    data = request.get_json()
    current_track = data.get("track", "No track info available")
    with open ("current_track.txt", "w") as f:
        f.write(current_track)

    print(f"Updated track info: {current_track}", flush=True)
    return jsonify({"status": "success"}), 200
