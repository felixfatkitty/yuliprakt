import os
from flask import Flask, request, jsonify, render_template_string
from models import db, Project, Task
from log_parser import log_action, parse_logs

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tasks.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Tracker & Manager</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e2e; color: #cdd6f4; max-width: 900px; margin: 0 auto; padding: 25px; }
        h1 { color: #cba6f7; text-align: center; }
        h2 { color: #89b4fa; font-size: 1.1rem; margin-top: 0; }
        .box { background: #313244; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); }
        form { display: flex; flex-direction: column; gap: 12px; }
        input, select, button { padding: 12px; border: 1px solid #45475a; border-radius: 6px; font-size: 14px; background: #1e1e2e; color: #cdd6f4; }
        button { background-color: #a6e3a1; color: #11111b; font-weight: bold; cursor: pointer; border: none; transition: 0.2s; }
        button:hover { background-color: #94e2d5; }
        .task-card { background: #181825; border-left: 5px solid #89b4fa; padding: 12px 15px; margin-bottom: 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center; }
        .badge { background: #45475a; padding: 3px 8px; border-radius: 6px; font-size: 11px; color: #f9e2af; margin-left: 8px; }
        .btn-del { background: #f38ba8; color: #11111b; padding: 6px 12px; font-size: 12px; }
        .btn-del:hover { background: #eba0ac; }
        .log-box { background: #11111b; color: #a6e3a1; font-family: monospace; padding: 10px; border-radius: 6px; font-size: 12px; max-height: 150px; overflow-y: auto; }
    </style>
</head>
<body>
    <h1>🚀 Менеджер Задач и Проектов (`yuliprakt`)</h1>

    <div class="box">
        <h2>Новый проект</h2>
        <form id="projForm">
            <input type="text" id="projTitle" placeholder="Название проекта" required>
            <button type="submit">Создать проект</button>
        </form>
    </div>

    <div class="box">
        <h2>Новая задача</h2>
        <form id="taskForm">
            <input type="text" id="taskDesc" placeholder="Описание задачи..." required>
            <select id="taskPriority">
                <option value="Low">Низкий приоритет</option>
                <option value="Medium" selected>Средний приоритет</option>
                <option value="High">Высокий приоритет</option>
            </select>
            <select id="taskProject">
                <option value="">Без проекта</option>
            </select>
            <button type="submit">Добавить задачу</button>
        </form>
    </div>

    <div class="box">
        <h2>Список задач</h2>
        <div id="tasksList">Загрузка данных...</div>
    </div>

    <div class="box">
        <h2>📋 Системный лог (Лог-парсер)</h2>
        <div id="logsList" class="log-box">Загрузка логов...</div>
    </div>

    <script>
        async function fetchProjects() {
            const res = await fetch('/api/projects');
            const data = await res.json();
            const select = document.getElementById('taskProject');
            select.innerHTML = '<option value="">Без проекта</option>';
            data.forEach(p => {
                select.innerHTML += `<option value="${p.id}">${p.title}</option>`;
            });
        }

        async function fetchTasks() {
            const res = await fetch('/api/tasks');
            const tasks = await res.json();
            const pRes = await fetch('/api/projects');
            const projects = await pRes.json();
            const pMap = Object.fromEntries(projects.map(p => [p.id, p.title]));

            const list = document.getElementById('tasksList');
            if (tasks.length === 0) {
                list.innerHTML = '<p style="color: #a6adc8;">Список задач пуст.</p>';
                return;
            }

            list.innerHTML = '';
            tasks.forEach(t => {
                const projName = t.project_id ? pMap[t.project_id] || 'Проект' : 'Без проекта';
                list.innerHTML += `
                    <div class="task-card">
                        <div>
                            <strong>${t.description}</strong>
                            <span class="badge">${t.priority}</span>
                            <span class="badge" style="color:#89b4fa;">${projName}</span>
                        </div>
                        <button class="btn-del" onclick="removeTask(${t.id})">Удалить</button>
                    </div>
                `;
            });
            fetchLogs();
        }

        async function fetchLogs() {
            const res = await fetch('/api/logs');
            const logs = await res.json();
            const logBox = document.getElementById('logsList');
            logBox.innerHTML = logs.join('<br>');
            logBox.scrollTop = logBox.scrollHeight;
        }

        document.getElementById('projForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = document.getElementById('projTitle').value;
            await fetch('/api/projects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title })
            });
            document.getElementById('projTitle').value = '';
            fetchProjects();
            fetchLogs();
        });

        document.getElementById('taskForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const description = document.getElementById('taskDesc').value;
            const priority = document.getElementById('taskPriority').value;
            const project_id = document.getElementById('taskProject').value || null;

            await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description, priority, project_id: project_id ? parseInt(project_id) : null })
            });
            document.getElementById('taskDesc').value = '';
            fetchTasks();
        });

        async function removeTask(id) {
            await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
            fetchTasks();
        }

        fetchProjects();
        fetchTasks();
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    log_action("VIEW", "Открыта главная страница интерфейса")
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/projects', methods=['GET', 'POST'])
def manage_projects():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Название проекта обязательно'}), 400
        proj = Project(title=data['title'])
        db.session.add(proj)
        db.session.commit()
        log_action("CREATE_PROJECT", f"Создан проект: {proj.title}")
        return jsonify({'id': proj.id, 'status': 'Проект успешно создан'}), 201

    projects = Project.query.all()
    return jsonify([p.to_dict() for p in projects]), 200

@app.route('/api/tasks', methods=['GET', 'POST'])
def manage_tasks():
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'description' not in data:
            return jsonify({'error': 'Описание задачи обязательно'}), 400
        
        task = Task(
            description=data['description'],
            priority=data.get('priority', 'Medium'),
            project_id=data.get('project_id')
        )
        db.session.add(task)
        db.session.commit()
        log_action("CREATE_TASK", f"Добавлена задача: {task.description} [Приоритет: {task.priority}]")
        return jsonify({'id': task.id, 'status': 'Задача успешно добавлена'}), 201

    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks]), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def remove_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Задача не найдена'}), 404
    desc = task.description
    db.session.delete(task)
    db.session.commit()
    log_action("DELETE_TASK", f"Удалена задача ID {task_id}: {desc}")
    return jsonify({'status': f'Задача {task_id} удалена'}), 200

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(parse_logs()), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)