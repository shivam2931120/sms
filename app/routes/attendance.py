from flask import Blueprint, flash, redirect, url_for
from flask_login import login_required, current_user

attendance_bp = Blueprint('attendance', __name__, url_prefix='/attendance')

@attendance_bp.route('/mark', methods=['GET', 'POST'])
@login_required
def mark_attendance():
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))
    return redirect(url_for('teacher.mark_attendance'))
