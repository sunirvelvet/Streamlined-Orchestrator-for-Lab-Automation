from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import json
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
scheduler = BackgroundScheduler()
scheduler.start()

tasks = {}
workers = {}

def add_task(task_id, task_data):
    start_time = datetime.fromisoformat(task_data['startTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
    end_time = datetime.fromisoformat(task_data['endTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
    duration = int((end_time - start_time).total_seconds() / 3600)  # Convert duration to integer
    tasks[task_id] = {
        "taskName": task_data['taskName'],
        "startTime": start_time,
        "endTime": end_time,
        "duration": duration,
        "equipment": task_data['equipment'],
        "assignedTo": task_data['assignedTo'],
        "priority": task_data['priority'],
        "dependencies": task_data['dependencies']
    }
    # Convert datetime objects to strings before emitting
    task_copy = tasks[task_id].copy()
    task_copy['startTime'] = task_copy['startTime'].isoformat()
    task_copy['endTime'] = task_copy['endTime'].isoformat()
    # Emit task added event
    socketio.emit('task_added', {'task_id': task_id, 'task': task_copy})

@app.route('/tasks', methods=['POST'])
def add_task_route():
    task_data = request.json
    task_id = task_data['taskId']
    add_task(task_id, task_data)
    return jsonify({"status": "Task added", "task_id": task_id}), 200

@app.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task_route(task_id):
    if task_id in tasks:
        del tasks[task_id]
        # Emit task deleted event
        socketio.emit('task_deleted', {'task_id': task_id})
        return jsonify({"status": "Task deleted"}), 200
    return jsonify({"status": "Task not found"}), 404

@socketio.on('connect')
def handle_connect():
    emit('tasks', tasks)

@socketio.on('disconnect')
def handle_disconnect():
    pass

if __name__ == '__main__':
    socketio.run(app, debug=True)
