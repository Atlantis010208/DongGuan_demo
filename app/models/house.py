from app import db

class HousePrice(db.Model):
    __tablename__ = 'dongguan_housing_prices'
    
    id = db.Column(db.BigInteger, primary_key=True)
    标题 = db.Column(db.Text)
    房屋名称 = db.Column(db.Text)
    地区 = db.Column(db.Text)
    价格 = db.Column(db.BigInteger)
    户型 = db.Column(db.Text)
    面积 = db.Column(db.Float)
    朝向 = db.Column(db.Text)
    装修情况 = db.Column(db.Text)
    所在楼层 = db.Column(db.Text)
    建筑类型 = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.标题,
            'community': self.房屋名称,
            'district': self.地区,
            'price': self.价格,
            'house_type': self.户型,
            'area': self.面积,
            'orientation': self.朝向,
            'decoration': self.装修情况,
            'floor': self.所在楼层,
            'building_type': self.建筑类型
        } 