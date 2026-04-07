from flask import Flask, jsonify, request, abort
from config import Config
from src.models.task import db
from src.models.task import Task
from src.schemas.schemas import TaskSchema
from pydantic import ValidationError

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.before_request
def create_table():
    db.create_all()


@app.route("/api/tasks", methods=['GET'])
def get_tasks():
    tasks_list = []
    for task in Task.query.all():
        tasks_list.append({'id': task.id, 'title': task.title, 'description': task.description,
                           'completed': task.completed, 'created_at': task.created_at,
                           'updated_at': task.updated_at, 'priority': task.priority})

    return jsonify({
        "tasks": tasks_list
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
