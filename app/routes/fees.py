from flask import Blueprint, abort, current_app, render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from app.models import Fee
from app import db
from app.school import get_school_details
from fpdf import FPDF
from datetime import date
import io

fees_bp = Blueprint('fees', __name__, url_prefix='/fees')

def ensure_fee_access(fee):
    if current_user.role == 'admin':
        return
    if current_user.role != 'student' or not fee.student or fee.student.user_id != current_user.id:
        abort(403)

def fee_return_endpoint():
    return 'admin.fees_management' if current_user.role == 'admin' else 'student.fees'

@fees_bp.route('/pay/<int:fee_id>', methods=['POST'])
@login_required
def pay_fee(fee_id):
    fee = Fee.query.get_or_404(fee_id)
    ensure_fee_access(fee)
    if fee.status == 'Paid':
        flash('Fee is already marked as paid.', 'info')
    else:
        # Payment capture is currently simulated; keep persisted data consistent.
        fee.status = 'Paid'
        fee.paid_date = date.today()
        db.session.commit()
        flash('Fee paid successfully.', 'success')
    return redirect(url_for(fee_return_endpoint()))

@fees_bp.route('/receipt/<int:fee_id>')
@login_required
def download_receipt(fee_id):
    fee = Fee.query.get_or_404(fee_id)
    ensure_fee_access(fee)
    if fee.status != 'Paid':
        flash('Fee not paid yet', 'warning')
        return redirect(url_for(fee_return_endpoint()))
        
    # Generate PDF
    school = get_school_details()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt=school['name'], ln=1, align="C")
    if school['address']:
        pdf.cell(200, 10, txt=school['address'], ln=1, align="C")
    pdf.cell(200, 10, txt="Fee Receipt", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Student: {fee.student.first_name}", ln=1)
    pdf.cell(200, 10, txt=f"Description: {fee.title}", ln=1)
    pdf.cell(200, 10, txt=f"Amount: {current_app.config['RAZORPAY_CURRENCY']} {fee.amount}", ln=1)
    pdf.cell(200, 10, txt=f"Date: {fee.paid_date}", ln=1)
    
    # Save to buffer
    buffer = io.BytesIO()
    pdf_output = pdf.output(dest='S')
    buffer.write(pdf_output.encode('latin-1') if isinstance(pdf_output, str) else bytes(pdf_output))
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f'receipt_{fee.id}.pdf', mimetype='application/pdf')
