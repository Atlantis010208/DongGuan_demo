from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models.house import HousePrice
from app.models.user import User, Role
from app import db
import pandas as pd
import os
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('您没有权限访问该页面', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def index():
    return render_template('admin/index.html')

@admin_bp.route('/users')
@login_required
@admin_required
def user_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # 获取搜索参数
    username = request.args.get('username', '')
    
    # 构建查询
    query = User.query
    
    # 如果有用户名搜索条件，添加模糊匹配
    if username:
        query = query.filter(User.username.like(f'%{username}%'))
    
    # 获取分页数据
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return render_template('admin/user_list.html', 
                         users=users, 
                         pagination=pagination,
                         username=username)  # 传递搜索条件到模板

@admin_bp.route('/users/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')
    
    if action == 'delete':
        if user.id == current_user.id:
            flash('不能删除当前登录用户', 'danger')
        else:
            db.session.delete(user)
            db.session.commit()
            flash('用户删除成功', 'success')
    elif action == 'change_role':
        new_role_id = request.form.get('role_id', type=int)
        if new_role_id in [1, 2]:  # 1: admin, 2: user
            user.role_id = new_role_id
            db.session.commit()
            flash('用户角色更新成功', 'success')
    
    return redirect(url_for('admin.user_list'))

@admin_bp.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    phone = request.form.get('phone')
    role_id = request.form.get('role_id', type=int)
    
    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        flash('用户名已存在', 'danger')
        return redirect(url_for('admin.user_list'))
    
    # 检查邮箱是否已被注册
    if User.query.filter_by(email=email).first():
        flash('邮箱已被注册', 'danger')
        return redirect(url_for('admin.user_list'))
    
    # 创建新用户
    user = User(
        username=username,
        email=email,
        phone=phone,
        role_id=role_id
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    flash('用户添加成功', 'success')
    return redirect(url_for('admin.user_list'))

@admin_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('没有选择文件', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('没有选择文件', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join('app', 'static', 'uploads', filename)
            file.save(filepath)
            
            try:
                # 读取文件并导入数据
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)
                
                # 数据清洗和导入
                import_data(df)
                
                flash('数据导入成功', 'success')
                return redirect(url_for('admin.index'))
            except Exception as e:
                flash(f'数据导入失败：{str(e)}', 'danger')
                return redirect(request.url)
    
    return render_template('admin/upload.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'csv', 'xlsx', 'xls'}

def import_data(df):
    # 清理数据
    df = df.dropna()  # 删除空值
    df = df.drop_duplicates()  # 删除重复值
    
    # 导入数据
    for _, row in df.iterrows():
        house = HousePrice(
            标题=row.get('标题'),
            房屋名称=row.get('房屋名称'),
            地区=row.get('地区'),
            价格=float(row.get('价格', 0)),  # 这里的价格是单价（元/平米）
            户型=row.get('户型'),
            面积=float(row.get('面积', 0)),
            朝向=row.get('朝向'),
            装修情况=row.get('装修情况'),
            所在楼层=row.get('所在楼层'),
            建筑类型=row.get('建筑类型')
        )
        db.session.add(house)
    
    db.session.commit()

@admin_bp.route('/house/edit/<int:house_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_house(house_id):
    house = HousePrice.query.get_or_404(house_id)
    
    if request.method == 'POST':
        try:
            house.标题 = request.form.get('标题')
            house.房屋名称 = request.form.get('房屋名称')
            house.地区 = request.form.get('地区')
            house.价格 = float(request.form.get('价格', 0))  # 直接存储单价（元/平米）
            house.户型 = request.form.get('户型')
            house.面积 = float(request.form.get('面积', 0))
            house.朝向 = request.form.get('朝向')
            house.装修情况 = request.form.get('装修情况')
            house.所在楼层 = request.form.get('所在楼层')
            house.建筑类型 = request.form.get('建筑类型')
            
            db.session.commit()
            flash('房源信息更新成功', 'success')
            return redirect(url_for('main.house_list'))
        except ValueError as e:
            flash('请输入有效的数值', 'danger')
            return render_template('admin/edit_house.html', house=house)
    
    return render_template('admin/edit_house.html', house=house)

@admin_bp.route('/house/delete/<int:house_id>', methods=['POST'])
@login_required
@admin_required
def delete_house(house_id):
    house = HousePrice.query.get_or_404(house_id)
    db.session.delete(house)
    db.session.commit()
    flash('房源信息删除成功', 'success')
    return redirect(url_for('main.house_list'))

@admin_bp.route('/api/user_stats')
@login_required
@admin_required
def get_user_stats():
    try:
        total_users = User.query.count()
        total_houses = HousePrice.query.count()
        
        # 计算价格统计（元/平米）
        price_stats = db.session.query(
            db.func.avg(HousePrice.价格).label('avg_price'),
            db.func.max(HousePrice.价格).label('max_price'),
            db.func.min(HousePrice.价格).label('min_price')
        ).first()
        
        # 获取最新更新时间
        last_house = HousePrice.query.order_by(HousePrice.id.desc()).first()
        last_update = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # 打印调试信息
        print("统计数据：")
        print(f"总用户数: {total_users}")
        print(f"总房源数: {total_houses}")
        if price_stats:
            print(f"平均单价: {price_stats.avg_price}")
            print(f"最高单价: {price_stats.max_price}")
            print(f"最低单价: {price_stats.min_price}")
        else:
            print("没有找到价格统计数据")
        
        # 确保数据不为None
        avg_price = price_stats.avg_price if price_stats and price_stats.avg_price else 0
        max_price = price_stats.max_price if price_stats and price_stats.max_price else 0
        min_price = price_stats.min_price if price_stats and price_stats.min_price else 0
        
        response_data = {
            'total_users': total_users,
            'total_houses': total_houses,
            'avg_price': round(float(avg_price), 2),  # 平均单价（元/平米）
            'max_price': round(float(max_price), 2),  # 最高单价（元/平米）
            'min_price': round(float(min_price), 2),  # 最低单价（元/平米）
            'last_update': last_update
        }
        
        print("返回数据：", response_data)
        return jsonify(response_data)
        
    except Exception as e:
        print(f"获取统计数据时出错：{str(e)}")
        return jsonify({
            'total_users': 0,
            'total_houses': 0,
            'avg_price': 0,
            'max_price': 0,
            'min_price': 0,
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M')
        })

@admin_bp.route('/api/stats/district')
@login_required
def get_district_stats():
    try:
        districts = db.session.query(
            HousePrice.地区,
            func.count(HousePrice.id).label('count'),
            func.avg(HousePrice.价格).label('avg_price'),
            func.avg(HousePrice.价格 * HousePrice.面积).label('avg_total_price')
        ).group_by(HousePrice.地区).all()
        
        return jsonify({
            'districts': [d.地区 for d in districts],
            'avg_prices': [round(float(d.avg_total_price) / 10000, 2) if d.avg_total_price else 0 for d in districts],
            'avg_unit_prices': [round(float(d.avg_price), 2) if d.avg_price else 0 for d in districts],
            'counts': [d.count for d in districts]
        })
    except Exception as e:
        print(f"获取区域统计数据时出错：{str(e)}")
        return jsonify({
            'districts': [],
            'avg_prices': [],
            'avg_unit_prices': [],
            'counts': []
        })

@admin_bp.route('/api/stats/house_type')
@login_required
def get_house_type_stats():
    try:
        types = db.session.query(
            HousePrice.户型,
            func.count(HousePrice.id).label('count'),
            func.avg(HousePrice.价格 * HousePrice.面积).label('avg_price')
        ).group_by(HousePrice.户型).all()
        
        return jsonify({
            'types': [t.户型 for t in types],
            'counts': [t.count for t in types],
            'avg_prices': [round(float(t.avg_price) / 10000, 2) if t.avg_price else 0 for t in types]  # 转换为万元
        })
    except Exception as e:
        print(f"获取户型统计数据时出错：{str(e)}")
        return jsonify({
            'types': [],
            'counts': [],
            'avg_prices': []
        })

@admin_bp.route('/api/stats/price_distribution')
@login_required
def get_price_distribution():
    try:
        # 获取所有总价（单价×面积）
        prices = [float(h.价格 * h.面积) / 10000 for h in HousePrice.query.all()]  # 转换为万元
        if not prices:
            return jsonify({'ranges': [], 'counts': []})
        
        # 创建价格区间
        min_price = min(prices)
        max_price = max(prices)
        step = (max_price - min_price) / 10
        ranges = [min_price + step * i for i in range(11)]
        
        # 统计每个区间的数量
        counts = [0] * 10
        for price in prices:
            for i in range(10):
                if ranges[i] <= price < ranges[i + 1]:
                    counts[i] += 1
                    break
        
        return jsonify({
            'ranges': [f"{round(ranges[i], 0)}-{round(ranges[i+1], 0)}" for i in range(10)],
            'counts': counts
        })
    except Exception as e:
        print(f"获取价格分布数据时出错：{str(e)}")
        return jsonify({
            'ranges': [],
            'counts': []
        })

@admin_bp.route('/api/stats/area_price_correlation')
@login_required
def get_area_price_correlation():
    try:
        houses = HousePrice.query.all()
        areas = [h.面积 for h in houses]
        prices = [float(h.价格 * h.面积) / 10000 for h in houses]  # 转换为万元
        
        return jsonify({
            'areas': areas,
            'prices': prices
        })
    except Exception as e:
        print(f"获取面积价格相关性数据时出错：{str(e)}")
        return jsonify({
            'areas': [],
            'prices': []
        })

@admin_bp.route('/api/recent_activities')
@login_required
@admin_required
def get_recent_activities():
    # 由于我们没有活动记录表，返回空数据
    return jsonify({
        'activities': []
    })

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('不能删除当前登录用户', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('用户删除成功', 'success')
    return redirect(url_for('admin.user_list'))

@admin_bp.route('/preview', methods=['POST'])
@login_required
@admin_required
def preview_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if file and allowed_file(file.filename):
        try:
            # 读取文件
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            
            # 只返回前10行数据
            preview_data = []
            for _, row in df.head(10).iterrows():
                price = float(row.get('价格', 0))  # 单价（元/平米）
                area = float(row.get('面积', 0))
                total_price = price * area  # 计算总价
                
                preview_data.append({
                    '标题': row.get('标题', ''),
                    '房屋名称': row.get('房屋名称', ''),
                    '地区': row.get('地区', ''),
                    '价格': price,  # 单价
                    '总价': total_price,  # 总价
                    '户型': row.get('户型', ''),
                    '面积': area,
                    '朝向': row.get('朝向', ''),
                    '装修情况': row.get('装修情况', ''),
                    '所在楼层': row.get('所在楼层', ''),
                    '建筑类型': row.get('建筑类型', '')
                })
            
            return jsonify({
                'success': True,
                'data': preview_data
            })
        except Exception as e:
            return jsonify({'error': f'文件读取失败：{str(e)}'}), 400
    
    return jsonify({'error': '不支持的文件格式'}), 400

@admin_bp.route('/test_db')
@login_required
@admin_required
def test_db():
    try:
        # 测试数据库连接
        total_users = User.query.count()
        total_houses = HousePrice.query.count()
        
        # 获取一些示例数据
        sample_houses = HousePrice.query.limit(5).all()
        house_data = []
        for house in sample_houses:
            house_data.append({
                '标题': house.标题,
                '价格': house.价格,
                '面积': house.面积
            })
        
        return jsonify({
            'status': 'success',
            'message': '数据库连接正常',
            'data': {
                'total_users': total_users,
                'total_houses': total_houses,
                'sample_houses': house_data
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'数据库连接错误：{str(e)}'
        }), 500

@admin_bp.route('/api/stats/yearly')
@login_required
def get_yearly_stats():
    try:
        # 获取房源总数
        total_houses = HousePrice.query.count()
        
        # 计算价格统计（元/平米）
        price_stats = db.session.query(
            db.func.count(HousePrice.id).label('count'),
            db.func.avg(HousePrice.价格).label('avg'),
            db.func.max(HousePrice.价格).label('max'),
            db.func.min(HousePrice.价格).label('min')
        ).first()
        
        # 计算总价值统计（价格 * 面积）
        total_value_stats = db.session.query(
            db.func.avg(HousePrice.价格 * HousePrice.面积).label('avg'),
            db.func.max(HousePrice.价格 * HousePrice.面积).label('max'),
            db.func.min(HousePrice.价格 * HousePrice.面积).label('min')
        ).first()
        
        response_data = {
            'price_stats': {
                'count': total_houses,
                'avg': round(float(price_stats.avg) if price_stats.avg else 0, 2),
                'max': round(float(price_stats.max) if price_stats.max else 0, 2),
                'min': round(float(price_stats.min) if price_stats.min else 0, 2)
            },
            'total_value_stats': {
                'avg': round(float(total_value_stats.avg) if total_value_stats.avg else 0, 2),
                'max': round(float(total_value_stats.max) if total_value_stats.max else 0, 2),
                'min': round(float(total_value_stats.min) if total_value_stats.min else 0, 2)
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"获取年度统计数据时出错：{str(e)}")
        return jsonify({
            'price_stats': {'count': 0, 'avg': 0, 'max': 0, 'min': 0},
            'total_value_stats': {'avg': 0, 'max': 0, 'min': 0}
        })

@admin_bp.route('/api/stats/decoration')
@login_required
def get_decoration_stats():
    try:
        # 按装修情况分组统计
        stats = db.session.query(
            HousePrice.装修情况,
            func.count(HousePrice.id).label('count'),
            func.avg(HousePrice.价格).label('avg_unit_price'),
            func.avg(HousePrice.价格 * HousePrice.面积).label('avg_total_price')
        ).group_by(HousePrice.装修情况).all()
        
        return jsonify({
            'decorations': [s.装修情况 for s in stats],
            'counts': [s.count for s in stats],
            'avg_unit_prices': [round(float(s.avg_unit_price), 2) if s.avg_unit_price else 0 for s in stats],
            'avg_prices': [round(float(s.avg_total_price) / 10000, 2) if s.avg_total_price else 0 for s in stats]  # 转换为万元
        })
    except Exception as e:
        print(f"获取装修情况统计数据时出错：{str(e)}")
        return jsonify({
            'decorations': [],
            'counts': [],
            'avg_unit_prices': [],
            'avg_prices': []
        })