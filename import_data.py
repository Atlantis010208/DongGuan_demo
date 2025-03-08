import pandas as pd
import pymysql
from app import create_app, db
from app.models.house import HousePrice
from app.models.user import Role, User
from sqlalchemy import create_engine

def import_house_data():
    print("开始导入房价数据...")
    app = create_app()
    
    with app.app_context():
        # 清空现有数据
        HousePrice.query.delete()
        db.session.commit()
        
        # 连接MySQL数据库
        engine = create_engine('mysql+pymysql://root:123456@localhost/dg_fangjia')
        
        # 读取MySQL表数据
        query = "SELECT * FROM dongguan_housing_prices"
        df = pd.read_sql(query, engine)
        
        # 导入数据
        total = len(df)
        for index, row in df.iterrows():
            try:
                # 处理面积数据（去除单位并转换为数字）
                area = float(str(row['面积']).replace('㎡', '').strip())
                
                # 处理价格数据（确保是数字）
                price = float(row['价格'])
                
                # 计算单价
                unit_price = price * 10000 / area  # 转换为元/平方米
                
                house = HousePrice(
                    district=row['地区'],
                    community=row['房屋名称'],
                    price=price,  # 价格（万元）
                    unit_price=unit_price,  # 单价（元/平方米）
                    house_type=row['户型'],
                    area=area,  # 面积（平方米）
                    floor=row['所在楼层'],
                    building_age=2024  # 由于原数据没有建筑年代，暂时使用当前年份
                )
                db.session.add(house)
                
                # 每1000条提交一次
                if (index + 1) % 1000 == 0:
                    db.session.commit()
                    print(f"已导入 {index + 1}/{total} 条数据")
            except Exception as e:
                print(f"导入第{index + 1}条数据时出错: {str(e)}")
                continue
        
        # 提交剩余数据
        db.session.commit()
        print("房价数据导入完成！")

def create_admin_user():
    print("创建管理员账户...")
    app = create_app()
    
    with app.app_context():
        # 初始化角色
        Role.init_roles()
        
        # 创建管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role_id=1  # 管理员角色ID为1
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("管理员账户创建成功！")
        else:
            print("管理员账户已存在！")

if __name__ == '__main__':
    create_admin_user()
    import_house_data()