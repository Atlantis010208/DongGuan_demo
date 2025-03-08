# 东莞房价查询系统

这是一个基于 Flask 开发的房价查询和数据分析系统，用于展示和分析东莞地区的房价数据。

## 功能特点

- 用户认证系统（登录/注册）
- 房源信息查询和筛选
- 数据可视化分析
  - 区域房价分布
  - 户型分布情况
  - 价格区间分布
  - 面积与价格关系
  - 装修情况价格分析
- 管理员后台
  - 用户管理
  - 数据导入导出
  - 房源信息管理

## 技术栈

- 后端：Python Flask
- 数据库：SQLite
- 前端：
  - Bootstrap 5
  - jQuery
  - Plotly.js（数据可视化）
- 其他：
  - SQLAlchemy（ORM）
  - Flask-Login（用户认证）
  - Pandas（数据处理）

## 安装说明

1. 克隆项目
```bash
git clone https://github.com/你的用户名/项目名称.git
cd 项目目录
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 初始化数据库
```bash
flask db upgrade
```

5. 运行项目
```bash
flask run
```

## 项目结构

```
app/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── house.py
├── routes/
│   ├── __init__.py
│   ├── main.py
│   ├── auth.py
│   └── admin.py
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── base.html
│   ├── main/
│   ├── auth/
│   └── admin/
└── utils/
    └── analysis.py
```

## 使用说明

1. 普通用户：
   - 可以浏览房源信息
   - 使用各种筛选条件搜索房源
   - 查看数据分析图表

2. 管理员用户：
   - 具有普通用户的所有权限
   - 可以管理用户账号
   - 可以导入/导出房源数据
   - 可以编辑房源信息

## 贡献指南

1. Fork 本仓库
2. 创建新的分支 `git checkout -b feature/your-feature`
3. 提交更改 `git commit -am 'Add some feature'`
4. 推送到分支 `git push origin feature/your-feature`
5. 创建 Pull Request

## 许可证

MIT License 