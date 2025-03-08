from app import db
from app.models.house import HousePrice
from sqlalchemy import func
import numpy as np

class HousePriceAnalyzer:
    @staticmethod
    def get_summary_stats():
        """获取总体统计数据"""
        try:
            # 获取房源总数
            total_count = HousePrice.query.count()
            
            # 获取价格统计
            price_stats = db.session.query(
                func.avg(HousePrice.价格).label('avg'),
                func.min(HousePrice.价格).label('min'),
                func.max(HousePrice.价格).label('max')
            ).first()
            
            # 获取面积统计
            area_stats = db.session.query(
                func.avg(HousePrice.面积).label('avg'),
                func.min(HousePrice.面积).label('min'),
                func.max(HousePrice.面积).label('max')
            ).first()
            
            return {
                'total_count': total_count,
                'price_stats': {
                    'avg': float(price_stats.avg) if price_stats.avg else 0,
                    'min': float(price_stats.min) if price_stats.min else 0,
                    'max': float(price_stats.max) if price_stats.max else 0
                },
                'area_stats': {
                    'avg': float(area_stats.avg) if area_stats.avg else 0,
                    'min': float(area_stats.min) if area_stats.min else 0,
                    'max': float(area_stats.max) if area_stats.max else 0
                }
            }
        except Exception as e:
            print(f"获取总体统计数据时出错：{str(e)}")
            return {
                'total_count': 0,
                'price_stats': {'avg': 0, 'min': 0, 'max': 0},
                'area_stats': {'avg': 0, 'min': 0, 'max': 0}
            }
    
    @staticmethod
    def get_district_stats():
        """获取区域统计数据"""
        districts = db.session.query(
            HousePrice.地区,
            func.count(HousePrice.id).label('count'),
            func.avg(HousePrice.价格).label('avg_price'),
            func.min(HousePrice.价格).label('min_price'),
            func.max(HousePrice.价格).label('max_price')
        ).group_by(HousePrice.地区).all()
        
        return {
            'districts': [d.地区 for d in districts],
            'counts': [d.count for d in districts],
            'avg_prices': [round(float(d.avg_price), 2) if d.avg_price else 0 for d in districts],
            'min_prices': [round(float(d.min_price), 2) if d.min_price else 0 for d in districts],
            'max_prices': [round(float(d.max_price), 2) if d.max_price else 0 for d in districts]
        }
    
    @staticmethod
    def get_house_type_stats():
        """获取户型统计数据"""
        types = db.session.query(
            HousePrice.户型,
            func.count(HousePrice.id).label('count'),
            func.avg(HousePrice.价格).label('avg_price')
        ).group_by(HousePrice.户型).all()
        
        return {
            'types': [t.户型 for t in types],
            'counts': [t.count for t in types],
            'avg_prices': [round(float(t.avg_price), 2) if t.avg_price else 0 for t in types]
        }
    
    @staticmethod
    def get_price_distribution():
        """获取价格分布数据"""
        prices = [p.价格 for p in HousePrice.query.with_entities(HousePrice.价格).all()]
        if not prices:
            return {'ranges': [], 'counts': []}
            
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
        
        return {
            'ranges': [f"{round(ranges[i], 2)}-{round(ranges[i+1], 2)}" for i in range(10)],
            'counts': counts
        }
    
    @staticmethod
    def get_area_price_correlation():
        """获取面积价格相关性数据"""
        data = HousePrice.query.with_entities(HousePrice.面积, HousePrice.价格).all()
        areas = [d.面积 for d in data]
        prices = [d.价格 for d in data]
        
        return {
            'areas': areas,
            'prices': prices
        }
    
    @staticmethod
    def get_yearly_stats():
        """获取年度统计数据"""
        try:
            # 获取房源总数
            total_houses = HousePrice.query.count()
            
            # 计算价格统计（单价，元/平米）
            price_stats = db.session.query(
                func.count(HousePrice.id).label('count'),
                func.avg(HousePrice.价格).label('avg'),
                func.max(HousePrice.价格).label('max'),
                func.min(HousePrice.价格).label('min')
            ).first()
            
            # 计算总价值统计（单价×面积，转换为万元）
            total_value_stats = db.session.query(
                func.avg(HousePrice.价格 * HousePrice.面积).label('avg'),
                func.max(HousePrice.价格 * HousePrice.面积).label('max'),
                func.min(HousePrice.价格 * HousePrice.面积).label('min')
            ).first()
            
            return {
                'price_stats': {
                    'count': total_houses,
                    'avg': round(float(price_stats.avg), 2) if price_stats.avg else 0,
                    'max': round(float(price_stats.max), 2) if price_stats.max else 0,
                    'min': round(float(price_stats.min), 2) if price_stats.min else 0
                },
                'total_value_stats': {
                    'avg': round(float(total_value_stats.avg) / 10000, 2) if total_value_stats.avg else 0,  # 转换为万元
                    'max': round(float(total_value_stats.max) / 10000, 2) if total_value_stats.max else 0,  # 转换为万元
                    'min': round(float(total_value_stats.min) / 10000, 2) if total_value_stats.min else 0   # 转换为万元
                }
            }
        except Exception as e:
            print(f"获取年度统计数据时出错：{str(e)}")
            return {
                'price_stats': {'count': 0, 'avg': 0, 'max': 0, 'min': 0},
                'total_value_stats': {'avg': 0, 'max': 0, 'min': 0}
            }
    
    @staticmethod
    def get_decoration_stats():
        """获取装修情况统计数据"""
        try:
            # 按装修情况分组统计
            stats = db.session.query(
                HousePrice.装修情况,
                func.count(HousePrice.id).label('count'),
                func.avg(HousePrice.价格 * HousePrice.面积).label('avg_total_price'),
                func.avg(HousePrice.价格).label('avg_unit_price'),
                func.min(HousePrice.价格 * HousePrice.面积).label('min_total_price'),
                func.max(HousePrice.价格 * HousePrice.面积).label('max_total_price')
            ).group_by(HousePrice.装修情况).all()
            
            return {
                'decoration_types': [s.装修情况 for s in stats],
                'counts': [s.count for s in stats],
                'avg_total_prices': [round(float(s.avg_total_price) / 10000, 2) if s.avg_total_price else 0 for s in stats],  # 转换为万元
                'avg_unit_prices': [round(float(s.avg_unit_price), 2) if s.avg_unit_price else 0 for s in stats],  # 元/平方米
                'min_total_prices': [round(float(s.min_total_price) / 10000, 2) if s.min_total_price else 0 for s in stats],  # 转换为万元
                'max_total_prices': [round(float(s.max_total_price) / 10000, 2) if s.max_total_price else 0 for s in stats]   # 转换为万元
            }
        except Exception as e:
            print(f"获取装修情况统计数据时出错：{str(e)}")
            return {
                'decoration_types': [],
                'counts': [],
                'avg_total_prices': [],
                'avg_unit_prices': [],
                'min_total_prices': [],
                'max_total_prices': []
            }