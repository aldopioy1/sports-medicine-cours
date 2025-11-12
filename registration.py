from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from src.models.user import db, Registration, User, Course

registration_bp = Blueprint('registration', __name__)

@registration_bp.route('/register/<int:course_id>', methods=['GET', 'POST'])
def register_course(course_id):
    if 'user_id' not in session:
        flash('يرجى تسجيل الدخول للتسجيل في الدورة', 'warning')
        return redirect(url_for('user.login'))
        
    course = Course.query.get_or_404(course_id)
    user = User.query.get(session['user_id'])
    
    # التحقق من التسجيل المسبق
    existing_registration = Registration.query.filter_by(
        user_id=user.id, 
        course_id=course.id
    ).first()
    
    if existing_registration:
        flash('أنت مسجل بالفعل في هذه الدورة', 'info')
        return redirect(url_for('registration.my_registrations'))
    
    if request.method == 'POST':
        attendance_type = request.form.get('attendance_type')
        payment_method = request.form.get('payment_method')
        preferred_language = request.form.get('preferred_language')
        special_needs = request.form.get('special_needs')
        how_did_you_hear = request.form.get('how_did_you_hear')
        expectations = request.form.get('expectations')
        
        if not attendance_type or not payment_method:
            flash('يرجى ملء جميع الحقول المطلوبة', 'danger')
            return render_template('register_course.html', course=course, user=user)
        
        new_registration = Registration(
            user_id=user.id,
            course_id=course.id,
            attendance_type=attendance_type,
            payment_method=payment_method,
            preferred_language=preferred_language,
            special_needs=special_needs,
            how_did_you_hear=how_did_you_hear,
            expectations=expectations
        )
        
        try:
            db.session.add(new_registration)
            db.session.commit()
            flash('تم التسجيل في الدورة بنجاح!', 'success')
            return redirect(url_for('registration.payment', registration_id=new_registration.id))
        except Exception as e:
            db.session.rollback()
            flash('حدث خطأ أثناء التسجيل في الدورة', 'danger')
    
    return render_template('register_course.html', course=course, user=user)

@registration_bp.route('/payment/<int:registration_id>')
def payment(registration_id):
    if 'user_id' not in session:
        flash('يرجى تسجيل الدخول للوصول إلى صفحة الدفع', 'warning')
        return redirect(url_for('user.login'))
        
    registration = Registration.query.get_or_404(registration_id)
    
    # التحقق من أن التسجيل ينتمي للمستخدم الحالي
    if registration.user_id != session['user_id']:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'danger')
        return redirect(url_for('home'))
        
    course = Course.query.get(registration.course_id)
    
    return render_template('payment.html', registration=registration, course=course)

@registration_bp.route('/my-registrations')
def my_registrations():
    if 'user_id' not in session:
        flash('يرجى تسجيل الدخول للوصول إلى تسجيلاتك', 'warning')
        return redirect(url_for('user.login'))
        
    user_id = session['user_id']
    registrations = Registration.query.filter_by(user_id=user_id).all()
    
    courses = {}
    for registration in registrations:
        course = Course.query.get(registration.course_id)
        courses[registration.id] = course
        
    return render_template('my_registrations.html', registrations=registrations, courses=courses)

@registration_bp.route('/cancel/<int:registration_id>', methods=['POST'])
def cancel_registration(registration_id):
    if 'user_id' not in session:
        flash('يرجى تسجيل الدخول لإلغاء التسجيل', 'warning')
        return redirect(url_for('user.login'))
        
    registration = Registration.query.get_or_404(registration_id)
    
    # التحقق من أن التسجيل ينتمي للمستخدم الحالي
    if registration.user_id != session['user_id']:
        flash('غير مصرح لك بإلغاء هذا التسجيل', 'danger')
        return redirect(url_for('home'))
        
    registration.payment_status = 'cancelled'
    
    try:
        db.session.commit()
        flash('تم إلغاء التسجيل بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('حدث خطأ أثناء إلغاء التسجيل', 'danger')
        
    return redirect(url_for('registration.my_registrations'))
