from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Project, User
from .forms import ProjectForm

project = Blueprint('project', __name__, url_prefix='/projects')

@project.route('/')
@login_required
def list_projects():
    # List Projects
    if current_user.role == 'admin':
        projects = Project.query.all()
    elif current_user.role == 'project_manager':
        projects = Project.query.filter_by(manager_id=current_user.id).all()
    else:
        projects = current_user.projects  # Assigned projects only
    return render_template('project/project_list.html', projects=projects)

@project.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    # Creating Project function
    if current_user.role not in ['admin', 'project_manager']:
        flash("You don't have permission to create projects.", "danger")
        return redirect(url_for('main.home'))

    form = ProjectForm()

    if current_user.role == 'admin':
        # Admin selects the manager
        form.manager.choices = [(u.id, u.name) for u in User.query.filter_by(role='project_manager').all()]
    else:
        # Project Manager: auto-assign self as manager
        form.manager.choices = [(current_user.id, current_user.name)]
        form.manager.data = current_user.id

    if form.validate_on_submit():
        new_project = Project(
            name=form.name.data,
            description=form.description.data,
            deadline=form.deadline.data,
            status=form.status.data,
            manager_id=form.manager.data
        )
        db.session.add(new_project)
        db.session.commit()
        flash("Project created successfully.", "success")

        # Redirect based on role
        if current_user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        else:
            return redirect(url_for('main.project_manager_dashboard'))

    return render_template('project/create_project.html', form=form)

@project.route('/dashboard')
@login_required
def project_dashboard():
    # For Project dashboard
    if current_user.role == 'admin':
        projects = Project.query.all()
    elif current_user.role == 'project_manager':
        projects = Project.query.filter_by(manager_id=current_user.id).all()
    else:
        projects = current_user.projects

    project_data = []
    for project in projects:
        total_tasks = len(project.tasks)
        completed_tasks = len([task for task in project.tasks if task.status.lower() == 'completed'])
        percent_complete = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

        project_data.append({
            'project': project,
            'percent_complete': percent_complete
        })

    return render_template('project/dashboard_project.html', projects=project_data)
