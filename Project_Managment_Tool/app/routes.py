from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('project.list_projects'))
    return render_template('welcome.html')

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('dashboard/admin_dashboard.html')

@main.route('/project_manager/dashboard')
@login_required
def project_manager_dashboard():
    return render_template('dashboard/pm_dashboard.html')

@main.route('/team_member/dashboard')
@login_required
def team_member_dashboard():
    return render_template('dashboard/team_dashboard.html')
