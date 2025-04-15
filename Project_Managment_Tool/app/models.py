from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='team_member')  # 'admin', 'project_manager', 'team_member'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)  # Required for Flask-Login

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    deadline = db.Column(db.Date)
    status = db.Column(db.String(50), default='Not Started')  # Not Started, In Progress, Completed
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    manager = db.relationship('User', backref='managed_projects')
    members = db.relationship('User', secondary='project_members', backref='projects')

project_members = db.Table('project_members',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='To Do')  # e.g., 'To Do', 'In Progress', 'Completed'
    priority = db.Column(db.String(50), default='Medium')  # e.g., 'Low', 'Medium', 'High'
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # User assigned to the task

    def __repr__(self):
        return f'<Task {self.name}>'