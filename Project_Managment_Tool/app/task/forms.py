from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from app.models import Project, User

def get_projects():
    return Project.query.all()

def get_users():
    return User.query.filter_by(role='team_member').all()


class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    due_date = DateField('Due Date')
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'), 
        ('Medium', 'Medium'), 
        ('High', 'High')
    ])
    status = SelectField('Status', choices=[
        ('To Do', 'To Do'), 
        ('In Progress', 'In Progress'), 
        ('Completed', 'Completed')
    ])
    project = QuerySelectField('Project', query_factory=get_projects, allow_blank=False, get_label='name')
    assigned_users = QuerySelectMultipleField('Assign To', query_factory=get_users, get_label='name')
    submit = SubmitField('Submit')
