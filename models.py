from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title
        }

class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(20), default='Medium')
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'priority': self.priority,
            'project_id': self.project_id
        }