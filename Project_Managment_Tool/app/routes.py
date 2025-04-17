from datetime import datetime
from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from app.models import Project, User
from app import db

main = Blueprint('main', __name__)
from flask_login import current_user

@main.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('main.admin_dashboard'))
        elif current_user.role == 'project_manager':
            return redirect(url_for('main.project_manager_dashboard'))
        elif current_user.role == 'team_member':
            return redirect(url_for('main.team_member_dashboard'))
    return render_template('welcome.html')
@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.home'))

    search_query = request.args.get('search', '').lower()
    status_filter = request.args.get('status', '')

    all_projects = Project.query.all()
    users = User.query.all()

    # Apply search and status filter
    filtered_projects = [
        p for p in all_projects
        if (search_query in p.name.lower()) and
           (status_filter == '' or p.status == status_filter)
    ]

    # Analytics should reflect all data, not filtered ones
    total_users = len(users)
    total_projects = len(all_projects)
    completed_projects = len([p for p in all_projects if p.status == 'Completed'])

    return render_template(
        'dashboard/admin_dashboard.html',
        projects=filtered_projects,
        users=users,
        total_users=total_users,
        total_projects=total_projects,
        completed_projects=completed_projects,
        search_query=search_query,
        status_filter=status_filter
    )



@main.route('/project_manager/dashboard')
@login_required
def project_manager_dashboard():
    if current_user.role != 'project_manager':
        return redirect(url_for('main.home'))

    projects = Project.query.filter_by(manager_id=current_user.id).all()

    # Calculate progress for each project
    project_data = []
    for project in projects:
        total_tasks = len(project.tasks)
        completed_tasks = len([task for task in project.tasks if task.status == 'Completed'])
        progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

        project_data.append({
            'project': project,
            'progress': progress,
            'completed_tasks': completed_tasks,
            'total_tasks': total_tasks
        })
    return render_template('dashboard/pm_dashboard.html', project_data=project_data)

@main.route('/team_member/dashboard')
@login_required
def team_member_dashboard():
    if current_user.role != 'team_member':
        return redirect(url_for('main.home'))

    tasks = current_user.tasks

    return render_template('dashboard/team_dashboard.html', tasks=tasks)

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