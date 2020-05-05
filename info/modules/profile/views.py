from flask import render_template
from flask import redirect, g, request, jsonify, current_app
from . import profile_bp
from info.utils.commons import user_login_data
from info.utils.response_code import RET
from info.utils.image_storage import image_storage
from info.models import db, News, Category
from info import constants


# 取/设置,用户头像上传
# 请求路径: /user/pic_info
# 请求方式:GET,POST
# 请求参数:无, POST有参数,avatar
# 返回值:GET请求: user_pci_info.html页面,data字典数据, POST请求: errno, errmsg,avatar_url
@profile_bp.route('/pic_info', methods=['GET', 'POST'])
@user_login_data
def pic_info():
    # 1.判断请求方式，如果是get请求
    if request.method == 'GET':
        # 2.携带用户数据，渲染页面
        return render_template('news/user_pic_info.html', user_info=g.user.to_dict())

    # 3.如果是post请求
    # 4.获取参数
    avatar = request.files.get('avatar')

    # 5.为空校验
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='图片不能为空')

    # 6.上传图像，判断图片是否上传成功
    try:
        image_name = image_storage(avatar.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='七牛云异常')

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg='图片上传失败')

    # 7.将图片设置到用户对象
    g.user.avatar_url = image_name

    # 8.返回响应
    data = {
        'avatar_url': constants.QINIU_DOMIN_PREFIX + image_name
    }
    return jsonify(errno=RET.OK, errmsg='上传成功', data=data)



# 获取我的关注
# 请求路径: /user/user_follow
# 请求方式: GET
# 请求参数:p
# 返回值: 渲染user_follow.html页面,字典data数据
@profile_bp.route('/user_follow')
@user_login_data
def user_follow():
    # 1.获取参数, p
    page = request.args.get('p', '1')
    # 2.参数类型转换
    try:
        page = int(page)
    except:
        page = 1

    # 3.分页查询用户关注的作者
    try:
        paginate = g.user.followed.paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取作者失败')

    # 4.获取分页对象属性，总页数，当前页，当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转换成字典列表
    author_list = []
    for author in items:
        author_list.append(author.to_dict())

    # 6.拼接数据，渲染页面
    data = {
        'totalPage': totalPage,
        'currentPage': currentPage,
        'author_list': author_list
    }
    return render_template('news/user_follow.html', data=data)


# 修改密码
# 请求路径: /user/pass_info
# 请求方式:GET,POST
# 请求参数:GET无, POST有参数,old_password, new_password
# 返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg
@profile_bp.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    # 1.判断GET请求
    if request.method == 'GET':
        # 2.直接渲染页面
        return render_template('news/user_pass_info.html')

    # 3.如果是POST请求，获取参数
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')

    # 4.为空校验
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 5.判断老密码是否正确
    if not g.user.check_password(old_password):
        return jsonify(errno=RET.DATAERR, errmsg='老密码错误')

    # 6.设置新密码
    g.user.password = new_password

    db.session.add(g.user)
    db.session.commit()

    # 7.返回响应
    return jsonify(errno=RET.OK, errmsg='修改成功')

# 获取新闻收藏列表
# 请求路径: /user/collection
# 请求方式: GET
# 请求参数页: p(页数)
# 返回值: user_collection.html页面
@profile_bp.route('/collection', methods=['GET', 'POST'])
@user_login_data
def collection():
    # 1.获取参数 ，p
    page = request.args.get('p', '1')
    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3.分页查询收藏的新闻
    try:
        paginate = g.user.collection_news.order_by(
            News.create_time.desc()
        ).paginate(page, 2, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    # 4.获取分页对象属性，总页数，当前页， 当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6.拼接数据，渲染页面
    data = {
        'totalPage': totalPage,
        'currentPage': currentPage,
        'news_list': news_list,
    }
    return render_template("news/user_collection.html", data=data)


# 新闻发布
# 获取/设置,新闻发布
# 请求路径: /user/news_release
# 请求方式:GET,POST
# 请求参数:GET无, POST ,title, category_id,digest,index_image,content
# 返回值:GET请求,user_news_release.html, data分类列表字段数据, POST,errno,errmsg
@profile_bp.route('/news_release', methods=['GET', 'POST'])
@user_login_data
def news_release():
    # 1.判断请求方式，如果是GET
    if request.method == 'GET':
        # 2.查询所有分类数据
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取分类失败')

        category_list = []
        for category in categories:
            category_list.append(category.to_dict())
        # 2.1 携带分类数据渲染页面
        return render_template('news/user_news_release.html', categories=categories)

    # 3.如果是POST, 获取参数
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    digest = request.form.get('digest')
    index_image = request.files.get('index_image')
    content = request.form.get('content')

    # 4.为空校验
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 5.上传图片，判断是否上传成功
    try:
        # 读取图片为二进制数据，上传
        image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='七牛云异常')

    if not image_name:
        return jsonify(errno=RET.NODATA, errmsg='图片上传失败')

    # 6.创建新闻对象，设置属性
    news = News()
    news.title = title
    news.source = g.user.nick_name
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1 # 表示审核中

    # 7.保存数据
    try:
        db.session.add(news)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='新闻发布失败')

    # 8.返回响应
    return jsonify(errno=RET.OK, errmsg='发布成功')


# 用户新闻列表
# 请求路径: /user/news_list
# 请求方式:GET
# 请求参数:p
# 返回值:GET渲染user_news_list.html页面
@profile_bp.route('/news_list', methods=['GET', 'POST'])
@user_login_data
def news_list():
    # 1.获取参数, p
    page = request.args.get('p')

    # 2.参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3.分页查询用户发布的新闻
    try:
        paginate = News.query.filter(
            News.user_id == g.user.id
        ).order_by(
            News.create_time.desc()
        ).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')

    # 4.获取分页对象中的属性，总页数，当前页，当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5.将对象列表，转换成字典列表
    news_list = []
    for news in items:
        news_list.append(news.to_dict())

    # 6.拼接数据，渲染页面
    data = {
        'totalPage': totalPage,
        'currentPage': currentPage,
        'news_list': news_list
    }
    # 7.携带数据，返回响应
    return render_template('news/user_news_list.html', data=data)

# 修改用户信息
# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@profile_bp.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    # 1.判断请求方式，如果是get请求
    if request.method == 'GET':
        # 2.携带用户数据，渲染页面
        if not g.user:
            # 如果没有登录，重定向到首页
            redirect('/')
        return render_template('news/user_base_info.html', user_info=g.user.to_dict())
    else:
        # 3.post请求
        # 4.获取参数
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')

        # 5.校验参数，为空校验
        if not all([nick_name, signature, gender]):
            return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

        if not gender in ['MAN', 'WOMAN']:
            return jsonify(errno=RET.DATAERR, errmsg='性别异常')

        # 6.修改用户数据
        g.user.signature = signature
        g.user.nick_name = nick_name
        g.user.gender = gender

        db.session.add(g.user)
        db.session.commit()

        # 7.返回响应
        return jsonify(errno=RET.OK, errmsg='修改成功')

# 用户信息
@profile_bp.route('/info')
@user_login_data
def user_info():
    # 1.判断用户是否登录
    if not g.user:
        return redirect('/')
    # 2.携带数据渲染页面
    data = {
        'user_info': g.user.to_dict()
    }
    return render_template('news/user.html', data=data)



