from flask import Flask, jsonify
from config import Config
from src.models.task import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.before_request
def create_table():
    db.create_all()


@app.route("/api/tasks")
def get_tasks():
    tasks = []
    return jsonify({
        "tasks": tasks
    })
