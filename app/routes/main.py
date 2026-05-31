from flask import Blueprint, jsonify, redirect, url_for
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('auth.login'))


@main.route('/healthz')
def healthz():
    try:
        db.session.execute(text('SELECT 1'))
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'status': 'error', 'database': 'unavailable'}), 503
    return jsonify({'status': 'ok', 'database': 'ok'})
