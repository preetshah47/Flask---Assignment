from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, db
from .forms import LoginForm, CreateUserForm
from werkzeug.security import check_password_hash, generate_password_hash
from . import auth  # Ensure 'auth' is imported correctly

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):  
            login_user(user)
            flash('Logged in successfully.', 'success')

            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            elif user.role == 'project_manager':
                return redirect(url_for('main.project_manager_dashboard'))
            elif user.role == 'team_member':
                return redirect(url_for('main.team_member_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash("You are not authorized to view this page.")
        return redirect(url_for('dashboard'))

    form = CreateUserForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.')
            return redirect(url_for('auth.create_user'))

        new_user = User(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            role=form.role.data
        )
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully!')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('auth/create_user.html', form=form)
