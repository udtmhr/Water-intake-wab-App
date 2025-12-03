from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, WaterLog
from utils import calculate_daily_goal, send_line_message
from datetime import datetime, timedelta
import os

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///water_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-fallback')
app.config['LINE_CHANNEL_ACCESS_TOKEN'] = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/settings', methods=['GET', 'POST'])
@login_required
def update_settings():
    if request.method == 'GET':
        return jsonify(current_user.to_dict())

    data = request.json
    height = data.get('height')
    weight = data.get('weight')
    age = data.get('age')
    gender = data.get('gender')
    
    # LINE Settings
    line_user_id = data.get('line_user_id')
    # line_channel_token = data.get('line_channel_token') # No longer used per user

    if not all([height, weight, age, gender]):
        return jsonify({'error': 'Missing required fields'}), 400

    daily_goal = calculate_daily_goal(weight, age)

    current_user.height = height
    current_user.weight = weight
    current_user.age = age
    current_user.gender = gender
    current_user.daily_goal = daily_goal
    current_user.line_user_id = line_user_id
    # current_user.line_channel_token = line_channel_token
    
    db.session.commit()
    return jsonify({'message': 'Settings updated', 'daily_goal': daily_goal})

@app.route('/api/intake', methods=['POST'])
# Note: Sensor data might come from a device without auth cookie. 
# For MVP, we assume sensor sends data for a specific user or we use a token.
# BUT, the request was "Place and Measure". 
# If the sensor is dumb, it might not know the user.
# For now, let's assume the sensor mimics the logged-in user OR we just use the first user for sensor data if no auth.
# However, to support multi-user properly, the sensor needs to identify the user.
# Let's keep it simple: The sensor endpoint requires a user_id or username in the payload if not authenticated.
def record_intake():
    data = request.json
    amount = data.get('amount')
    timestamp_val = data.get('timestamp')
    username = data.get('username') # Optional if authenticated

    if amount is None:
        return jsonify({'error': 'Amount is required'}), 400
    
    target_user = current_user
    if not target_user.is_authenticated:
        target_user = None
        if username:
            target_user = User.query.filter_by(username=username).first()
        
        # Fallback for single-user sensor simulation if only one user exists
        if not target_user:
             target_user = User.query.first()
        
        if not target_user:
            return jsonify({'error': 'User not found or not authenticated'}), 401

    if timestamp_val:
        try:
            timestamp = datetime.fromtimestamp(timestamp_val)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid timestamp format'}), 400
    else:
        timestamp = datetime.utcnow()

    log = WaterLog(user_id=target_user.id, amount=amount, timestamp=timestamp)
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Intake recorded', 'amount': amount})

@app.route('/api/intake', methods=['DELETE'])
def reset_intake():
    # For testing: Clear logs for the target user to simulate "no drink" state
    data = request.json or {}
    username = data.get('username')
    
    target_user = current_user
    if not target_user.is_authenticated:
        target_user = None
        if username:
            target_user = User.query.filter_by(username=username).first()
        if not target_user:
             target_user = User.query.first()
        if not target_user:
            return jsonify({'error': 'User not found'}), 401

    # Delete logs
    WaterLog.query.filter_by(user_id=target_user.id).delete()
    # Reset notification timer
    target_user.last_notification_sent = None
    
    db.session.commit()
    return jsonify({'message': 'Water logs reset'})

@app.route('/api/status', methods=['GET'])
@login_required
def get_status():
    # Calculate total intake for today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    logs = WaterLog.query.filter_by(user_id=current_user.id).filter(WaterLog.timestamp >= today_start).all()
    total_intake = sum(log.amount for log in logs)
    
    percentage = min(100, int((total_intake / current_user.daily_goal) * 100)) if current_user.daily_goal > 0 else 0

    # Check time since last drink
    last_drink = WaterLog.query.filter_by(user_id=current_user.id).order_by(WaterLog.timestamp.desc()).first()
    alert = False
    if last_drink:
        time_since_last = datetime.utcnow() - last_drink.timestamp
        if time_since_last.total_seconds() > 7200: # 2 hours
            alert = True
            
            # LINE Notification Logic
            if current_user.line_user_id and app.config['LINE_CHANNEL_ACCESS_TOKEN']:
                # Check if we already sent a notification recently (e.g., in the last 2 hours)
                last_sent = current_user.last_notification_sent
                if not last_sent or (datetime.utcnow() - last_sent).total_seconds() > 7200:
                    success = send_line_message(
                        app.config['LINE_CHANNEL_ACCESS_TOKEN'],
                        current_user.line_user_id,
                        "水分をとりましょう！🚰 2時間以上経過しています。"
                    )
                    if success:
                        current_user.last_notification_sent = datetime.utcnow()
                        db.session.commit()

    return jsonify({
        'configured': current_user.height is not None,
        'daily_goal': current_user.daily_goal,
        'current_intake': total_intake,
        'percentage': percentage,
        'percentage': percentage,
        'alert': alert,
        'username': current_user.username,
        'line_configured': bool(current_user.line_user_id and app.config['LINE_CHANNEL_ACCESS_TOKEN'])
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
