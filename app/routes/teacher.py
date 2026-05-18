from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from datetime import date, datetime, timedelta
from app import db
from app.models import Teacher, Class, Student, Subject, TimeTable, Attendance, Mark, Exam, Homework

teacher = Blueprint('teacher', __name__, url_prefix='/teacher')

def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'teacher':
            flash('Access denied.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def current_teacher_or_redirect():
    teacher_profile = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher_profile:
        flash('Teacher profile not found.', 'warning')
        return None, redirect(url_for('main.index'))
    return teacher_profile, None

def assigned_class_and_subject_ids(teacher_profile):
    timetable_entries = TimeTable.query.filter_by(teacher_id=teacher_profile.id).all()
    class_ids = {entry.class_id for entry in timetable_entries}
    subject_ids = {entry.subject_id for entry in timetable_entries}
    return class_ids, subject_ids

def parse_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def parse_date_value(value, label='Date'):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date(), None
    except (TypeError, ValueError):
        return None, f'{label} must be a valid date.'

def parse_float(value, label):
    try:
        return float(value), None
    except (TypeError, ValueError):
        return None, f'{label} must be a valid number.'

@teacher.route('')
@teacher.route('/')
@login_required
@teacher_required
def index():
    return redirect(url_for('teacher.dashboard'))

@teacher.route('/dashboard')
@login_required
@teacher_required
def dashboard():
    teacher_profile, response = current_teacher_or_redirect()
    if response:
        return response
    
    today = date.today()
    day_name = today.strftime('%A')
    
    # Today's classes from timetable
    today_classes = TimeTable.query.filter_by(teacher_id=teacher_profile.id, day_of_week=day_name).order_by(TimeTable.start_time).all()
    
    # Classes taught (from timetable)
    all_timetable = TimeTable.query.filter_by(teacher_id=teacher_profile.id).all()
    class_ids = list(set([t.class_id for t in all_timetable]))
    classes_taught = Class.query.filter(Class.id.in_(class_ids)).all() if class_ids else []
    
    # Homework assigned
    pending_hw = Homework.query.filter_by(teacher_id=teacher_profile.id).filter(Homework.due_date >= today).count()
    
    return render_template('teacher/dashboard.html',
                           teacher=teacher_profile,
                           today_classes=today_classes,
                           classes_taught=classes_taught,
                           pending_hw=pending_hw,
                           today=today)

@teacher.route('/schedule')
@login_required
@teacher_required
def schedule():
    teacher_profile, response = current_teacher_or_redirect()
    if response:
        return response
    timetable = TimeTable.query.filter_by(teacher_id=teacher_profile.id).order_by(TimeTable.day_of_week, TimeTable.start_time).all()
    
    # Group by day
    days = {}
    for t in timetable:
        if t.day_of_week not in days:
            days[t.day_of_week] = []
        days[t.day_of_week].append(t)
    
    return render_template('teacher/schedule.html', teacher=teacher_profile, days=days)

@teacher.route('/attendance/mark', methods=['GET', 'POST'])
@login_required
@teacher_required
def mark_attendance():
    teacher_profile, response = current_teacher_or_redirect()
    if response:
        return response
    
    # Get classes this teacher is assigned to
    class_ids, _ = assigned_class_and_subject_ids(teacher_profile)
    classes = Class.query.filter(Class.id.in_(class_ids)).all() if class_ids else []
    
    selected_class = request.args.get('class_id')
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    students = []
    existing_attendance = {}
    
    if selected_class:
        selected_class_id = parse_int(selected_class)
        if selected_class_id not in class_ids:
            flash('You are not assigned to that class.', 'danger')
            return redirect(url_for('teacher.mark_attendance'))
        students = Student.query.filter_by(class_id=selected_class).order_by(Student.roll_no).all()
        date_obj, error = parse_date_value(selected_date, 'Attendance date')
        if error:
            flash(error, 'danger')
            return redirect(url_for('teacher.mark_attendance'))
        for s in students:
            att = Attendance.query.filter_by(student_id=s.id, date=date_obj).first()
            if att:
                existing_attendance[s.id] = att.status
    
    if request.method == 'POST':
        date_obj, error = parse_date_value(request.form.get('date'), 'Attendance date')
        if error:
            flash(error, 'danger')
            return redirect(url_for('teacher.mark_attendance'))
        class_id = request.form['class_id']
        class_id_int = parse_int(class_id)
        if class_id_int not in class_ids:
            flash('You are not assigned to that class.', 'danger')
            return redirect(url_for('teacher.mark_attendance'))
        students = Student.query.filter_by(class_id=class_id).all()
        
        for student in students:
            status = request.form.get(f'status_{student.id}', 'Absent')
            existing = Attendance.query.filter_by(student_id=student.id, date=date_obj).first()
            if existing:
                existing.status = status
            else:
                att = Attendance(student_id=student.id, date=date_obj, status=status)
                db.session.add(att)
        
        db.session.commit()
        flash(f'Attendance marked for {len(students)} students!', 'success')
        return redirect(url_for('teacher.mark_attendance', class_id=class_id, date=request.form['date']))
    
    return render_template('teacher/mark_attendance.html',
                           teacher=teacher_profile,
                           classes=classes,
                           students=students,
                           selected_class=selected_class,
                           selected_date=selected_date,
                           existing_attendance=existing_attendance)

@teacher.route('/marks/entry', methods=['GET', 'POST'])
@login_required
@teacher_required
def enter_marks():
    teacher_profile, response = current_teacher_or_redirect()
    if response:
        return response
    
    # Get classes and subjects
    class_ids, subject_ids = assigned_class_and_subject_ids(teacher_profile)
    
    classes = Class.query.filter(Class.id.in_(class_ids)).all() if class_ids else []
    subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all() if subject_ids else []
    exams = Exam.query.order_by(Exam.date.desc()).all()
    
    selected_class = request.args.get('class_id')
    selected_subject = request.args.get('subject_id')
    selected_exam = request.args.get('exam_id')
    students = []
    existing_marks = {}
    
    if selected_class and selected_subject and selected_exam:
        selected_class_id = parse_int(selected_class)
        selected_subject_id = parse_int(selected_subject)
        if selected_class_id not in class_ids or selected_subject_id not in subject_ids:
            flash('You are not assigned to that class or subject.', 'danger')
            return redirect(url_for('teacher.enter_marks'))
        students = Student.query.filter_by(class_id=selected_class).order_by(Student.roll_no).all()
        for s in students:
            mark = Mark.query.filter_by(student_id=s.id, subject_id=selected_subject, exam_id=selected_exam).first()
            if mark:
                existing_marks[s.id] = mark.score_obtained
    
    if request.method == 'POST':
        class_id = request.form['class_id']
        subject_id = request.form['subject_id']
        exam_id = request.form['exam_id']
        max_score, error = parse_float(request.form.get('max_score', 100), 'Max score')
        if error or max_score <= 0:
            flash(error or 'Max score must be greater than zero.', 'danger')
            return redirect(url_for('teacher.enter_marks', class_id=class_id, subject_id=subject_id, exam_id=exam_id))
        class_id_int = parse_int(class_id)
        subject_id_int = parse_int(subject_id)
        if class_id_int not in class_ids or subject_id_int not in subject_ids:
            flash('You are not assigned to that class or subject.', 'danger')
            return redirect(url_for('teacher.enter_marks'))
        
        students = Student.query.filter_by(class_id=class_id).all()
        
        for student in students:
            score = request.form.get(f'score_{student.id}')
            if score:
                score, error = parse_float(score, f'Score for {student.first_name} {student.last_name}')
                if error:
                    flash(error, 'danger')
                    return redirect(url_for('teacher.enter_marks', class_id=class_id, subject_id=subject_id, exam_id=exam_id))
                if score < 0 or score > max_score:
                    flash(f'Score for {student.first_name} {student.last_name} must be between 0 and {max_score}.', 'danger')
                    return redirect(url_for('teacher.enter_marks', class_id=class_id, subject_id=subject_id, exam_id=exam_id))
                existing = Mark.query.filter_by(student_id=student.id, subject_id=subject_id, exam_id=exam_id).first()
                if existing:
                    existing.score_obtained = score
                    existing.max_score = max_score
                else:
                    mark = Mark(student_id=student.id, subject_id=subject_id, exam_id=exam_id, score_obtained=score, max_score=max_score)
                    db.session.add(mark)
        
        db.session.commit()
        flash('Marks saved successfully!', 'success')
        return redirect(url_for('teacher.enter_marks', class_id=class_id, subject_id=subject_id, exam_id=exam_id))
    
    return render_template('teacher/enter_marks.html',
                           teacher=teacher_profile,
                           classes=classes,
                           subjects=subjects,
                           exams=exams,
                           students=students,
                           selected_class=selected_class,
                           selected_subject=selected_subject,
                           selected_exam=selected_exam,
                           existing_marks=existing_marks)
