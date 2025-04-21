from datetime import datetime, timedelta, timezone
from flask import Blueprint, flash, render_template, redirect, request, url_for
from flask_login import current_user, login_required
from .forms import UpdateProfileForm
from app.models import Project, Task, User
from app import db

main = Blueprint('main', __name__)
from flask_login import current_user

@main.route('/')
def home():
    # Home route for role wise dashboards
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
    # Admin Dashboard
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
    # Project Manager Dashboard
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
    #Team Member dashboard
    if current_user.role != 'team_member':
        return redirect(url_for('main.home'))

    tasks = current_user.tasks

    # Search Bar
    search_query = request.args.get('search', '').lower()
    if search_query:
        tasks = [task for task in tasks if
                 search_query in task.title.lower() or
                 search_query in task.description.lower()]

    # Due date filter 
    filter_due = request.args.get('due_filter', 'all')
    today = datetime.now(timezone.utc).date()

    if filter_due == 'today':
        tasks = [task for task in tasks if task.due_date and task.due_date == today]
    elif filter_due == 'week':
        end_of_week = today + timedelta(days=7)
        tasks = [task for task in tasks if task.due_date and today <= task.due_date <= end_of_week]

     # Priority filter
    priority_filter = request.args.get('priority', '').lower()
    if priority_filter in ['low', 'medium', 'high']:
        tasks = [task for task in tasks if task.priority.lower() == priority_filter]

    return render_template('dashboard/team_dashboard.html', tasks=tasks, search_query=search_query, filter_due=filter_due, priority_filter=priority_filter)

@main.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    # Edit user route
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
    # Delete User route
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

@main.route('/view_tasks/<int:project_id>', methods=['GET'])
@login_required
def view_tasks(project_id):
    # View Task route
    project = Project.query.get(project_id)
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('main.admin_dashboard'))

    tasks = project.tasks  
    return render_template('tasks/task_list.html', project=project, tasks=tasks)

@main.route('/<int:project_id>/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(project_id, task_id):
    # Route for deleting task
    project = Project.query.get(project_id)
    task = Task.query.get_or_404(task_id)

    # Only allow admin or project manager who owns the project
    if current_user.role not in ['admin', 'project_manager'] or (
        current_user.role == 'project_manager' and task.project.manager_id != current_user.id):
        flash("You don't have permission to delete this task.", 'danger')
        return redirect(url_for('task.list_tasks', project_id=project.id))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.view_tasks', project_id=project_id))

@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Route to update profile
    form = UpdateProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data

        if form.password.data:
            current_user.set_password(form.password.data)

        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.home'))

    return render_template('profile.html', form=form)

@main.route('/project/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    # To edit project
    project = Project.query.get(project_id)
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('main.home'))

    # Allow only admin or project manager who owns the project
    if current_user.role not in ['admin', 'project_manager'] or (
        current_user.role == 'project_manager' and project.manager_id != current_user.id):
        flash("You don't have permission to edit this project.", 'danger')
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        project.name = request.form['name']
        project.status = request.form['status']
        deadline_str = request.form['deadline']
        project.deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None

        try:
            db.session.commit()
            flash('Project updated successfully.', 'success')
            # Redirect based on the user's role
            return redirect(url_for('main.project_manager_dashboard') if current_user.role == 'project_manager' else url_for('main.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating project: {str(e)}', 'danger')

    return render_template('dashboard/edit_project.html', project=project)

@main.route('/project/delete/<int:project_id>', methods=['GET'])
@login_required
def delete_project(project_id):
    # Delete Project
    project = Project.query.get(project_id)
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('main.home'))

    # Allow only admin or the assigned project manager
    if current_user.role not in ['admin', 'project_manager'] or (
        current_user.role == 'project_manager' and project.manager_id != current_user.id):
        flash("You don't have permission to delete this project.", 'danger')
        return redirect(url_for('main.home'))

    try:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting project: {str(e)}', 'danger')

    return redirect(url_for('main.project_manager_dashboard') if current_user.role == 'project_manager' else url_for('main.admin_dashboard'))
