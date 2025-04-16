from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import Project, db, Task
from .forms import TaskForm

task_bp = Blueprint('task', __name__, url_prefix='/tasks')

@task_bp.route('/')
@login_required
def list_tasks():
    if current_user.role == 'admin':
        tasks = Task.query.all()
    elif current_user.role == 'project_manager':
        tasks = Task.query.join(Task.project).filter(Project.manager_id == current_user.id).all()

    else:
        tasks = current_user.tasks
    return render_template('tasks/task_list.html', tasks=tasks)

@task_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            status=form.status.data,
            project=form.project.data
        )
        for user in form.assigned_users.data:
            task.assigned_users.append(user)
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('task.list_tasks'))
    return render_template('tasks/create_task.html', form=form)

@task_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Ensure the user has permission to edit the task
    if current_user.role not in ['admin', 'project_manager'] or (
        current_user.role == 'project_manager' and task.project.manager_id != current_user.id):
        flash("You don't have permission to edit this task.", 'danger')
        return redirect(url_for('task.list_tasks'))

    # Create a form and populate it with the task's data
    form = TaskForm(obj=task)

    # Pre-populate the form with assigned users and project
    if request.method == 'GET':
        form.assigned_users.data = task.assigned_users
        form.project.data = task.project

    # Handle form submission
    if form.validate_on_submit():
        form.populate_obj(task)  # Populate the task object with form data
        task.assigned_users = form.assigned_users.data  # Update assigned users
        db.session.commit()  # Commit the changes to the database
        flash('Task updated successfully!', 'success')
        return redirect(url_for('task.list_tasks'))

    return render_template('tasks/edit_task.html', form=form, task=task)

@task_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Only allow admin or project manager who owns the project
    if current_user.role not in ['admin', 'project_manager'] or (
        current_user.role == 'project_manager' and task.project.manager_id != current_user.id):
        flash("You don't have permission to delete this task.", 'danger')
        return redirect(url_for('task.list_tasks'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('task.list_tasks'))

@task_bp.route('/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)

    if current_user.role == 'team_member' and current_user in task.assigned_users:
        task.status = 'Completed'
        db.session.commit()
        flash('Task marked as completed.', 'success')
    else:
        flash("You are not allowed to complete this task.", 'danger')

    return redirect(url_for('task.list_tasks'))
