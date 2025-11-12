from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from src.models.user import db, User, Course, Registration

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('غير مصرح لك بالوصول إلى لوحة التحكم', 'danger')
        return redirect(url_for('home'))
        
    users_count = User.query.count()
    courses_count = Course.query.count()
    registrations_count = Registration.query.count()
    pending_payments = Registration.query.filter_by(payment_status='pending').count()
    
    return render_template('admin/dashboard.html', 
                          users_count=users_count,
                          courses_count=courses_count,
                          registrations_count=registrations_count,
                          pending_payments=pending_payments)

@admin_bp.route('/users')
def users():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
        
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/courses')
def courses():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
        
    courses = Course.query.all()
    return render_template('admin/courses.html', courses=courses)

@admin_bp.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        price = request.form.get('price')
        capacity = request.form.get('capacity')
        location = request.form.get('location')
        
        if not title or not description or not start_date or not end_date or not price or not capacity or not location:
            flash('جميع الحقول مطلوبة', 'danger')
            return render_template('admin/add_course.html')
            
        new_course = Course(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            price=float(price),
            capacity=int(capacity),
            location=location
        )
        
        try:
            db.session.add(new_course)
            db.session.commit()
            flash('تم إضافة الدورة بنجاح', 'success')
            return redirect(url_for('admin.courses'))
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء إضافة الدورة', 'danger')
            
    return render_template('admin/add_course.html')

@admin_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
def edit_course(course_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
        
    course = Course.query.get_or_404(course_id)
    
    if request.method == 'POST':
        course.title = request.form.get('title')
        course.description = request.form.get('description')
        course.start_date = request.form.get('start_date')
        course.end_date = request.form.get('end_date')
        course.price = float(request.form.get('price'))
        course.capacity = int(request.form.get('capacity'))
        course.location = request.form.get('location')
        course.is_active = 'is_active' in request.form
        
        try:
            db.session.commit()
            flash('تم تحديث الدورة بنجاح', 'success')
            return redirect(url_for('admin.courses'))
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء تحديث الدورة', 'danger')
            
    return render_template('admin/edit_course.html', course=course)

@admin_bp.route('/registrations')
def registrations():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
        
    registrations = Registration.query.all()
    
    users = {}
    courses = {}
    for registration in registrations:
        users[registration.user_id] = User.query.get(registration.user_id)
        courses[registration.course_id] = Course.query.get(registration.course_id)
        
    return render_template('admin/registrations.html', 
                          registrations=registrations,
                          users=users,
                          courses=courses)

@admin_bp.route('/registrations/update/<int:registration_id>', methods=['POST'])
def update_registration(registration_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
        
    registration = Registration.query.get_or_404(registration_id)
    payment_status = request.form.get('payment_status')
    
    if payment_status:
        registration.payment_status = payment_status
        
        try:
            db.session.commit()
            flash('تم تحديث حالة الدفع بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء تحديث حالة الدفع', 'danger')
            
    return redirect(url_for('admin.registrations'))
