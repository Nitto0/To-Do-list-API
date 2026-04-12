from flask import Flask, jsonify, request, abort
from config import Config
from src.models.task import db
from src.models.task import Task
from src.schemas.schemas import TaskSchema
from pydantic import ValidationError
import math

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.before_request
def create_table():
    db.create_all()


@app.route("/api/tasks", methods=['GET'])
def get_tasks():
    page = 1
    per_page = 10

    if request.json:
        parameters = request.json
        page = parameters['page'] if 'page' in parameters else page
        per_page = parameters['per_page'] if 'per_page' in parameters else per_page

    tasks_list = []
    for index, task in enumerate(Task.query.all()):
        if (index >= (page - 1) * per_page) and index < per_page * (page + 1):
            tasks_list.append({'id': task.id, 'title': task.title, 'description': task.description,
                               'completed': task.completed, 'created_at': task.created_at,
                               'updated_at': task.updated_at, 'priority': task.priority})
    total_tasks = Task.query.count()
    return jsonify({
        "tasks": tasks_list,
        "pagination": {
            'page': page,
            'per_page': per_page,
            'total_pages': math.ceil(total_tasks / per_page),
            'total_items': total_tasks
        }
    }), 200


@app.route("/api/tasks/<int:task_id>")
def get_task(task_id):
    task = Task.query.get(task_id)
    if task:
        return jsonify({
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "completed": task.completed,
            "id": task.id,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }), 200
    else:
        abort(404, "Task not Found")


@app.route("/api/tasks", methods=['POST'])
def create_task():
    new_task = request.json

    if 'title' not in new_task or 'description' not in new_task:
        abort(400, description='You should write title and description of task!')

    if 'priority' not in new_task:
        new_task['priority'] = 1

    if 'completed' not in new_task:
        new_task['completed'] = False

    try:
        validate_task = TaskSchema(title=new_task['title'], description=new_task['description'],
                                   priority=new_task['priority'], completed=new_task['completed'])
        print(f'''Success validation!
                  Title: {validate_task.title},
                  description: {validate_task.description}
                  priority: {validate_task.priority},
                  completed: {validate_task.completed}'''
              )
    except ValidationError:
        abort(400, description="Error validation!")

    task = Task(title=new_task['title'], description=new_task['description'],
                priority=new_task['priority'], completed=new_task['completed'])

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "completed": task.completed,
        "id": task.id,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }), 201


@app.route("/api/tasks/<int:task_id>", methods=['PATCH'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        abort(404, description="Task not Found")

    updated_data = request.json

    updates = {
        'title': updated_data['title'] if 'title' in updated_data else task.title,
        'description': updated_data['description'] if 'description' in updated_data else task.description,
        'completed': updated_data['completed'] if 'completed' in updated_data else task.completed,
        'priority': updated_data['priority'] if 'priority' in updated_data else task.priority
    }

    try:
        validate_task = TaskSchema(title=updates['title'], description=updates['description'],
                                   completed=updates['completed'], priority=updates['priority'])
        print(f'''Success validation!
                          Title: {validate_task.title},
                          description: {validate_task.description}
                          priority: {validate_task.priority},
                          completed: {validate_task.completed}'''
              )
    except ValidationError:
        abort(400, description="Error validation!")

    for key, value in updates.items():
        setattr(task, key, value)

    db.session.commit()
    return jsonify({
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "completed": task.completed,
        "id": task.id,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }), 200


@app.route("/api/tasks/<int:task_id>", methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        abort(404, description="Task not Found")

    db.session.delete(task)
    db.session.commit()
    return "", 204


@app.route("/api/tasks/statistics")
def get_statistics():
    pass
