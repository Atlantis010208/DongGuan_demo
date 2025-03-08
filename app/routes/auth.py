from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, Role
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请输入用户名和密码', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None:
            flash('用户名不存在', 'danger')
            return render_template('auth/login.html')
        
        if not user.check_password(password):
            flash('密码错误', 'danger')
            return render_template('auth/login.html')
        
        login_user(user)
        flash('登录成功', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'danger')
            return redirect(url_for('auth.register'))
        
        user = User(
            username=username,
            email=email,
            phone=phone,
            role_id=2  # 默认为普通用户
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('邮箱已被使用', 'danger')
            return redirect(url_for('auth.profile'))
        
        current_user.email = email
        current_user.phone = phone
        
        if password:
            current_user.set_password(password)
        
        db.session.commit()
        flash('个人信息更新成功', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html') 