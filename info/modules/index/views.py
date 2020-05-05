import logging
from flask import render_template, current_app, jsonify, request, g
from flask import session

from . import index_bp
from info import redis_store
from info.models import User
from info.models import News
from info.models import Category
from info.utils.response_code import RET
from info.utils.commons import user_login_data


# 首页新闻列表
# 请求路径: /newslist
# 请求方式: GET
# 请求参数: cid,page,per_page
# 返回值: data数据
@index_bp.route('/newslist')
def newslist():
    # 1.获取参数
    cid = request.args.get('cid', '1')  # 默认为最新分类
    page = request.args.get('page', '1')  # 默认第一页
    per_page = request.args.get('per_page', '10')

    # 2.参数类型转换
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        page = 1
        per_page = 10

    # 3.分页查询
    try:
        filters = []
        if cid != '1':
            filters.append(News.category_id == cid)

        paginate = News.query.filter(*filters).order_by(
            News.create_time.desc()
        ).paginate(page, per_page, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    # 4.获取分页对象中的属性，总页数，当前页，当前页的对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表转换成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6.携带数据，返回响应
    return jsonify(
        errno=RET.OK,
        errmsg='获取新闻成功',
        totalPage=totalPage,
        currentPage=currentPage,
        newsList=news_list
    )


@index_bp.route('/')
@user_login_data
def show_index():
    # 3.获取热点新闻
    try:
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    # 4.将新闻对象转成字典列表
    news_list = []
    for item in news:
        news_list.append(item.to_dict())

    # 5.查询所有分类的数据
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取分类失败')

    # 6.将分类对象转换成字典列表
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 5.拼接用户数据，渲染页面
    data = {
        # 如果user有值就返回左边的内容，否则返回右边内容
        "user_info": g.user.to_dict() if g.user else "",
        "news_list": news_list,
        "category_list": category_list,
    }

    # 渲染首页
    return render_template('news/index.html', data=data)


# 处理网站logo
@index_bp.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('news/favicon.ico')



# 统一返回404页面
@index_bp.route('/404')
@user_login_data
def page_not_found():
    data = {
        "user_info": g.user.to_dict() if g.user else ""
    }
    return render_template('news/404.html', data=data)
