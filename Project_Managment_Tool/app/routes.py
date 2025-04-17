from datetime import datetime
from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from app.models import Project, User
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('project.list_projects'))
    return render_template('welcome.html')

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    projects = Project.query.all()
    total_users = User.query.count()
    users = User.query.all()
    total_projects = len(projects)
    completed_projects = len([p for p in projects if p.status == 'Completed'])

    return render_template(
        'dashboard/admin_dashboard.html',
        projects=projects,
        users=users,
        total_users=total_users,
        total_projects=total_projects,
        completed_projects=completed_projects
    )


@main.route('/project_manager/dashboard')
@login_required
def project_manager_dashboard():
    return render_template('dashboard/pm_dashboard.html')

@main.route('/team_member/dashboard')
@login_required
def team_member_dashboard():
    return render_template('dashboard/team_dashboard.html')

@main.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.role = request.form['role']
        try:
            db.session.commit()
            flash('User updated successfully.', 'success')
            return redirect(url_for('main.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user: {str(e)}', 'danger')
    return render_template('dashboard/edit_user.html', user=user)

@main.route('/admin/delete_user/<int:user_id>', methods=['GET'])
@login_required
def delete_user(user_id):
    # Ensure the current user is an admin
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    # Fetch the user by ID
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    # Deleting the user from the database
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')

    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/delete_project/<int:project_id>', methods=['GET'])
@login_required
def delete_project(project_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    project = Project.query.get(project_id)
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    try:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting project: {str(e)}', 'danger')

    return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/view_tasks/<int:project_id>', methods=['GET'])
@login_required
def view_tasks(project_id):
    project = Project.query.get(project_id)
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    tasks = project.tasks  
    return render_template('tasks/task_list.html', project=project, tasks=tasks)

@main.route('/admin/edit_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    project = Project.query.get(project_id)
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    if request.method == 'POST':
        project.name = request.form['name']
        project.status = request.form['status']
        deadline_str = request.form['deadline']
        project.deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None

        try:
            db.session.commit()
            flash('Project updated successfully.', 'success')
            return redirect(url_for('main.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'danger')

    return render_template('dashboard/edit_project.html', project=project)