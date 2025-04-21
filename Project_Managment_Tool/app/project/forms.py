from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired
from app.models import User

# Project creation form
class ProjectForm(FlaskForm):
    name = StringField('Project Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    deadline = DateField('Deadline', format='%Y-%m-%d')
    status = SelectField('Status', choices=[
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ])
    manager = SelectField('Project Manager', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Project')
