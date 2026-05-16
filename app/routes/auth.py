from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from app.demo import DEMO_ACCOUNTS

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        login_id = (request.form.get('login_id') or '').strip()
        password = request.form.get('password') or ''
        
        # specific for postgresql (ilike), but generic sqlalchemy 'ilike' usually works
        user = User.query.filter((User.email.ilike(login_id)) | (User.username.ilike(login_id))).first()
        
        if user and user.check_password(password):
            if not user.is_approved:
                flash('Account pending approval. Please wait for an administrator to verify your details.', 'warning')
                return render_template('auth/login.html', demo_accounts=DEMO_ACCOUNTS)

            login_user(user)
            flash('Login successful!', 'success')

            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student.dashboard'))

            return redirect(url_for('main.index'))

        flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('auth/login.html', demo_accounts=DEMO_ACCOUNTS)

@auth.before_app_request
def check_approval_status():
    if current_user.is_authenticated and not current_user.is_approved:
        logout_user()
        flash('Your account is pending approval or has been suspended.', 'warning')
        return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''
        role = request.form.get('role')

        if role not in {'student', 'teacher'}:
            flash('Invalid account role selected.', 'danger')
            return render_template('auth/register.html')

        if not username or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('auth/register.html')
            
        # Create User
        user = User(username=username, email=email, role=role, is_approved=False)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        
        # Create Placeholder Profile
        from app.models import Student, Teacher, Department, Class
        from datetime import date
        
        # Get default dependencies (Assuming 'GEN' dept exists from seed)
        dept = Department.query.filter_by(code='GEN').first()
        
        if role == 'student':
            student = Student(
                user_id=user.id,
                first_name=username, # Provisional
                last_name='(Pending)',
                department_id=dept.id if dept else None,
                admission_date=date.today()
            )
            db.session.add(student)
        elif role == 'teacher':
            teacher = Teacher(
                user_id=user.id,
                first_name=username, # Provisional
                last_name='(Pending)',
                department_id=dept.id if dept else None,
                joining_date=date.today()
            )
            db.session.add(teacher)
            
        db.session.commit()
        flash('Account created! Please wait for admin approval.', 'info')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
