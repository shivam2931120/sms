from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from datetime import date, datetime, timedelta
from app import db
from app.models import Student, Attendance, Fee, Mark, TimeTable, Homework, Event, Announcement
from app.uploads import save_student_photo

student = Blueprint('student', __name__, url_prefix='/student')

def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('Access denied.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def current_student_or_redirect():
    student_profile = Student.query.filter_by(user_id=current_user.id).first()
    if not student_profile:
        flash('Student profile not found.', 'warning')
        return None, redirect(url_for('main.index'))
    return student_profile, None

@student.route('')
@student.route('/')
@login_required
@student_required
def index():
    return redirect(url_for('student.dashboard'))

@student.route('/dashboard')
@login_required
@student_required
def dashboard():
    student, response = current_student_or_redirect()
    if response:
        return response
    
    # Attendance stats
    today = date.today()
    month_ago = today - timedelta(days=30)
    total_att = Attendance.query.filter(Attendance.student_id == student.id, Attendance.date >= month_ago).count()
    present_att = Attendance.query.filter(Attendance.student_id == student.id, Attendance.date >= month_ago, Attendance.status == 'Present').count()
    att_percentage = round((present_att / total_att * 100), 1) if total_att > 0 else 0
    
    # Fee status
    pending_fees = Fee.query.filter_by(student_id=student.id, status='Pending').count()
    
    # Recent marks
    recent_marks = Mark.query.filter_by(student_id=student.id).order_by(Mark.id.desc()).limit(5).all()
    
    # Upcoming homework
    upcoming_hw = Homework.query.filter(Homework.class_id == student.class_id, Homework.due_date >= today).order_by(Homework.due_date).limit(5).all()
    
    # Announcements
    announcements = Announcement.query.filter_by(is_active=True).order_by(Announcement.created_at.desc()).limit(3).all()
    
    return render_template('student/dashboard.html', 
                           student=student,
                           att_percentage=att_percentage,
                           pending_fees=pending_fees,
                           recent_marks=recent_marks,
                           upcoming_hw=upcoming_hw,
                           announcements=announcements)

@student.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    student, response = current_student_or_redirect()
    if response:
        return response

    if request.method == 'POST':
        student.first_name = request.form.get('first_name', '').strip() or student.first_name
        student.last_name = request.form.get('last_name', '').strip() or student.last_name
        student.gender = request.form.get('gender') or None
        student.blood_group = request.form.get('blood_group') or None
        student.phone = request.form.get('phone') or None
        student.parent_name = request.form.get('parent_name') or None
        student.parent_phone = request.form.get('parent_phone') or None
        student.address = request.form.get('address') or None

        dob_value = request.form.get('dob')
        try:
            student.dob = datetime.strptime(dob_value, '%Y-%m-%d').date() if dob_value else None
        except ValueError:
            flash('Date of birth must be a valid date.', 'danger')
            return render_template('student/profile.html', student=student)

        try:
            save_student_photo(student, request.files.get('photo'))
        except ValueError as error:
            flash(str(error), 'danger')
            return render_template('student/profile.html', student=student)

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html', student=student)

@student.route('/attendance')
@login_required
@student_required
def attendance():
    student, response = current_student_or_redirect()
    if response:
        return response
    attendance = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).limit(60).all()
    
    # Calculate stats
    total = len(attendance)
    present = sum(1 for a in attendance if a.status == 'Present')
    absent = sum(1 for a in attendance if a.status == 'Absent')
    late = sum(1 for a in attendance if a.status == 'Late')
    
    return render_template('student/attendance.html', 
                           student=student,
                           attendance=attendance,
                           stats={'total': total, 'present': present, 'absent': absent, 'late': late})

@student.route('/marks')
@login_required
@student_required
def marks():
    student, response = current_student_or_redirect()
    if response:
        return response
    marks = Mark.query.filter_by(student_id=student.id).order_by(Mark.id.desc()).all()
    
    # Group by exam
    exams = {}
    for m in marks:
        if m.exam_id not in exams:
            exams[m.exam_id] = {'exam': m.exam, 'marks': []}
        exams[m.exam_id]['marks'].append(m)
    
    return render_template('student/marks.html', student=student, exams=exams)

@student.route('/fees')
@login_required
@student_required
def fees():
    student, response = current_student_or_redirect()
    if response:
        return response
    fees = Fee.query.filter_by(student_id=student.id).order_by(Fee.due_date.desc()).all()
    
    total_due = sum(f.amount for f in fees if f.status == 'Pending')
    total_paid = sum(f.amount for f in fees if f.status == 'Paid')
    
    return render_template('student/fees.html', student=student, fees=fees, total_due=total_due, total_paid=total_paid)

@student.route('/timetable')
@login_required
@student_required
def timetable():
    student, response = current_student_or_redirect()
    if response:
        return response
    timetable = TimeTable.query.filter_by(class_id=student.class_id).order_by(TimeTable.day_of_week, TimeTable.start_time).all()
    
    # Group by day
    days = {}
    for t in timetable:
        if t.day_of_week not in days:
            days[t.day_of_week] = []
        days[t.day_of_week].append(t)
    
    return render_template('student/timetable.html', student=student, days=days)

@student.route('/homework')
@login_required
@student_required
def homework():
    student, response = current_student_or_redirect()
    if response:
        return response
    homework = Homework.query.filter_by(class_id=student.class_id).order_by(Homework.due_date.desc()).limit(20).all()
    return render_template('student/homework.html', student=student, homework=homework)
