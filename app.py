from flask import Flask, render_template, request, jsonify
from models import db, User, WaterLog
from utils import calculate_daily_goal
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///water_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    height = data.get('height')
    weight = data.get('weight')
    age = data.get('age')
    gender = data.get('gender')

    if not all([height, weight, age, gender]):
        return jsonify({'error': 'Missing required fields'}), 400

    daily_goal = calculate_daily_goal(weight, age)

    user = User.query.first()
    if not user:
        user = User(height=height, weight=weight, age=age, gender=gender, daily_goal=daily_goal)
        db.session.add(user)
    else:
        user.height = height
        user.weight = weight
        user.age = age
        user.gender = gender
        user.daily_goal = daily_goal
    
    db.session.commit()
    return jsonify({'message': 'Settings updated', 'daily_goal': daily_goal})

@app.route('/api/intake', methods=['POST'])
def record_intake():
    data = request.json
    amount = data.get('amount')
    timestamp_val = data.get('timestamp')

    if amount is None:
        return jsonify({'error': 'Amount is required'}), 400
    
    # If timestamp is provided, use it, otherwise use current time
    if timestamp_val:
        try:
            timestamp = datetime.fromtimestamp(timestamp_val)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid timestamp format'}), 400
    else:
        timestamp = datetime.utcnow()

    log = WaterLog(amount=amount, timestamp=timestamp)
    db.session.add(log)
    db.session.commit()
    return jsonify({'message': 'Intake recorded', 'amount': amount})

@app.route('/api/status', methods=['GET'])
def get_status():
    user = User.query.first()
    if not user:
        return jsonify({'configured': False})

    # Calculate total intake for today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    logs = WaterLog.query.filter(WaterLog.timestamp >= today_start).all()
    total_intake = sum(log.amount for log in logs)
    
    # Calculate percentage
    percentage = min(100, int((total_intake / user.daily_goal) * 100)) if user.daily_goal > 0 else 0

    # Check time since last drink
    last_drink = WaterLog.query.order_by(WaterLog.timestamp.desc()).first()
    alert = False
    if last_drink:
        time_since_last = datetime.utcnow() - last_drink.timestamp
        # Alert if more than 2 hours (7200 seconds)
        if time_since_last.total_seconds() > 7200:
            alert = True
    else:
        # If no drink today yet, check if it's been a while since start of day? 
        # Or just ignore until first drink? Let's say if no drink for 2 hours since waking up (assuming 8am start)
        # For simplicity, let's just say if no logs at all, no alert yet.
        pass

    return jsonify({
        'configured': True,
        'daily_goal': user.daily_goal,
        'current_intake': total_intake,
        'percentage': percentage,
        'alert': alert
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
