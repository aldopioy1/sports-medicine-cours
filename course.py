from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from src.models.user import db, Course, Registration, User

course_bp = Blueprint('course', __name__)

@course_bp.route('/')
def all_courses():
    courses = Course.query.filter_by(is_active=True).all()
    return render_template('courses.html', courses=courses)

@course_bp.route('/<int:course_id>')
def course_details(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_details.html', course=course)
