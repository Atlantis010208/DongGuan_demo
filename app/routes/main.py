from flask import Blueprint, render_template, jsonify, request, send_file
from flask_login import login_required, current_user
from app.models.house import HousePrice
from app.utils.analysis import HousePriceAnalyzer
from app import db
import pandas as pd
import json
import os
from datetime import datetime
from sqlalchemy import func

main_bp = Blueprint('main', __name__)

class Pagination:
    def __init__(self, query, page, per_page):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = query.count()
        self.pages = (self.total + per_page - 1) // per_page
        
        self.items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1
        self.next_num = page + 1
    
    def iter_pages(self):
        left_edge = 2
        left_current = 2
        right_current = 3
        right_edge = 2
        
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

@main_bp.route('/')
@login_required
def index():
    return render_template('main/index.html')

@main_bp.route('/house/list')
@login_required
def house_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = HousePrice.query
    
    # 筛选条件
    district = request.args.get('地区')
    if district:
        query = query.filter(HousePrice.地区 == district)
    
    # 添加房屋名称搜索
    house_name = request.args.get('房屋名称')
    if house_name:
        query = query.filter(HousePrice.房屋名称.like(f'%{house_name}%'))
    
    # 添加户型搜索
    house_type = request.args.get('户型')
    if house_type:
        if house_type == '5室及以上':
            # 对于5室及以上的情况，使用正则表达式匹配
            query = query.filter(HousePrice.户型.like('5%') | 
                               HousePrice.户型.like('6%') |
                               HousePrice.户型.like('7%') |
                               HousePrice.户型.like('8%') |
                               HousePrice.户型.like('9%'))
        else:
            # 对于1-4室的情况，使用模糊匹配
            query = query.filter(HousePrice.户型.like(f'{house_type}%'))
    
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    if price_min is not None:
        query = query.filter(HousePrice.价格 >= price_min)
    if price_max is not None:
        query = query.filter(HousePrice.价格 <= price_max)
    
    # 排序
    sort_by = request.args.get('sort_by', '价格')
    sort_order = request.args.get('sort_order', 'desc')
    if sort_order == 'desc':
        query = query.order_by(getattr(HousePrice, sort_by).desc())
    else:
        query = query.order_by(getattr(HousePrice, sort_by).asc())
    
    pagination = Pagination(query, page, per_page)
    
    # 获取所有地区列表用于筛选
    districts = db.session.query(HousePrice.地区.distinct()).all()
    districts = [d[0] for d in districts]
    
    return render_template('main/house_list.html',
                         houses=pagination.items,
                         pagination=pagination,
                         districts=districts,
                         current_filters={
                             '地区': district,
                             '房屋名称': house_name,
                             '户型': house_type,
                             'price_min': price_min,
                             'price_max': price_max,
                             'sort_by': sort_by,
                             'sort_order': sort_order
                         })

@main_bp.route('/visualization')
@login_required
def visualization():
    return render_template('main/visualization.html')

@main_bp.route('/api/stats/summary')
@login_required
def get_summary_stats():
    """获取总体统计数据"""
    return jsonify(HousePriceAnalyzer.get_summary_stats())

@main_bp.route('/api/stats/district')
@login_required
def get_district_stats():
    """获取区域统计数据"""
    try:
        stats = db.session.query(
            HousePrice.地区,
            func.count(HousePrice.id).label('count'),
            func.avg(HousePrice.价格).label('avg_price'),
            func.avg(HousePrice.价格 * HousePrice.面积).label('avg_total')
        ).group_by(HousePrice.地区).all()

        result = {
            'districts': [s.地区 for s in stats],
            'counts': [s.count for s in stats],
            'avg_prices': [float(s.avg_price) for s in stats],
            'avg_totals': [float(s.avg_total) for s in stats]
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/stats/house_type')
@login_required
def get_house_type_stats():
    """获取户型统计数据"""
    try:
        stats = db.session.query(
            HousePrice.户型,
            func.count(HousePrice.id).label('count')
        ).group_by(HousePrice.户型).all()

        result = {
            'house_types': [s.户型 for s in stats],
            'counts': [s.count for s in stats]
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/stats/price_distribution')
@login_required
def get_price_distribution():
    """获取价格分布统计数据"""
    try:
        # 计算总价（万元）
        total_prices = db.session.query(
            (HousePrice.价格 * HousePrice.面积 / 10000).label('total_price')
        ).all()
        
        # 创建价格区间
        price_ranges = ['0-100', '100-200', '200-300', '300-500', 
                       '500-800', '800-1000', '1000以上']
        counts = [0] * len(price_ranges)
        
        # 统计各区间数量
        for price in total_prices:
            total = float(price.total_price)
            if total <= 100:
                counts[0] += 1
            elif total <= 200:
                counts[1] += 1
            elif total <= 300:
                counts[2] += 1
            elif total <= 500:
                counts[3] += 1
            elif total <= 800:
                counts[4] += 1
            elif total <= 1000:
                counts[5] += 1
            else:
                counts[6] += 1

        result = {
            'price_ranges': price_ranges,
            'counts': counts
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/stats/area_price_correlation')
@login_required
def get_area_price_correlation():
    """获取面积价格相关性数据"""
    try:
        data = db.session.query(
            HousePrice.面积,
            (HousePrice.价格 * HousePrice.面积 / 10000).label('total_price')
        ).all()

        result = {
            'areas': [float(d.面积) for d in data],
            'prices': [float(d.total_price) for d in data]
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/stats/yearly')
@login_required
def get_yearly_stats():
    """获取年度统计数据"""
    try:
        price_stats = db.session.query(
            func.count(HousePrice.价格).label('count'),
            func.avg(HousePrice.价格).label('avg'),
            func.min(HousePrice.价格).label('min'),
            func.max(HousePrice.价格).label('max')
        ).first()

        total_value_stats = db.session.query(
            func.avg(HousePrice.价格 * HousePrice.面积).label('avg'),
            func.min(HousePrice.价格 * HousePrice.面积).label('min'),
            func.max(HousePrice.价格 * HousePrice.面积).label('max')
        ).first()

        result = {
            'price_stats': {
                'count': price_stats.count,
                'avg': float(price_stats.avg),
                'min': float(price_stats.min),
                'max': float(price_stats.max)
            },
            'total_value_stats': {
                'avg': float(total_value_stats.avg),
                'min': float(total_value_stats.min),
                'max': float(total_value_stats.max)
            }
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/api/stats/decoration')
@login_required
def get_decoration_stats():
    """获取装修情况统计数据"""
    try:
        stats = db.session.query(
            HousePrice.装修情况,
            func.count(HousePrice.id).label('count'),
            func.avg(HousePrice.价格).label('avg_unit_price'),
            func.avg(HousePrice.价格 * HousePrice.面积 / 10000).label('avg_total_price')
        ).group_by(HousePrice.装修情况).all()

        result = {
            'decoration_types': [s.装修情况 for s in stats],
            'counts': [s.count for s in stats],
            'avg_unit_prices': [float(s.avg_unit_price) for s in stats],
            'avg_total_prices': [float(s.avg_total_price) for s in stats]
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main_bp.route('/download/report')
@login_required
def download_report():
    """下载数据报告"""
    try:
        # 获取分析数据
        summary_stats = HousePriceAnalyzer.get_summary_stats()
        district_stats = HousePriceAnalyzer.get_district_stats()
        house_type_stats = HousePriceAnalyzer.get_house_type_stats()
        
        # 使用绝对路径
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        download_dir = os.path.join(current_dir, 'static', 'downloads')
        print(f"下载目录路径: {download_dir}")  # 调试信息
        
        # 确保下载目录存在
        os.makedirs(download_dir, exist_ok=True)
        
        # 创建文件名和路径
        filename = f'house_price_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        filepath = os.path.join(download_dir, filename)
        print(f"文件完整路径: {filepath}")  # 调试信息
        
        # 验证数据
        print("统计数据验证:")  # 调试信息
        print(f"summary_stats: {summary_stats}")
        print(f"district_stats: {district_stats}")
        print(f"house_type_stats: {house_type_stats}")
        
        # 创建Excel文件
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # 总体统计sheet
            summary_df = pd.DataFrame({
                '指标': ['总房源数', '平均总价(万元)', '最高总价(万元)', '最低总价(万元)',
                        '平均面积(㎡)', '最大面积(㎡)', '最小面积(㎡)'],
                '数值': [
                    summary_stats['total_count'],
                    summary_stats['price_stats']['avg'],
                    summary_stats['price_stats']['max'],
                    summary_stats['price_stats']['min'],
                    summary_stats['area_stats']['avg'],
                    summary_stats['area_stats']['max'],
                    summary_stats['area_stats']['min']
                ]
            })
            summary_df.to_excel(writer, sheet_name='总体统计', index=False)
            print("已写入总体统计sheet")  # 调试信息
            
            # 区域统计sheet
            district_df = pd.DataFrame({
                '区域': district_stats['districts'],
                '房源数量': district_stats['counts'],
                '平均总价(万元)': district_stats['avg_prices'],
                '最低总价(万元)': district_stats['min_prices'],
                '最高总价(万元)': district_stats['max_prices']
            })
            district_df.to_excel(writer, sheet_name='区域统计', index=False)
            print("已写入区域统计sheet")  # 调试信息
            
            # 户型统计sheet
            house_type_df = pd.DataFrame({
                '户型': house_type_stats['types'],
                '数量': house_type_stats['counts'],
                '平均总价(万元)': house_type_stats['avg_prices']
            })
            house_type_df.to_excel(writer, sheet_name='户型统计', index=False)
            print("已写入户型统计sheet")  # 调试信息
        
        print(f"Excel文件已保存到: {filepath}")  # 调试信息
        
        # 验证文件是否存在
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件未能成功创建: {filepath}")
        
        # 返回文件
        return send_file(
            filepath,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        import traceback
        error_msg = f"生成报告时出错：{str(e)}\n{traceback.format_exc()}"
        print(error_msg)  # 打印详细错误信息
        return jsonify({
            'error': '生成报告失败',
            'detail': str(e),
            'traceback': traceback.format_exc()
        }), 500