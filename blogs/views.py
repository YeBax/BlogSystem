import json
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.db.models import Count
from django.db import transaction
from django.contrib.auth.decorators import login_required
# Create your views here.

from BlogSystem import settings
from django.contrib import auth
from .blog_form import UserForm
from .models import *


def index(request):
    article_list = Article.objects.all()
    return render(request, "index.html", locals())


def login(request):
    if request.method == "POST":
        response = {"user": None, "msg": None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code")
        valid_code_str = request.session.get("valid_code_str")  # 从session中 取出随机字符串

        if valid_code.upper() == valid_code_str.upper():
            username = auth.authenticate(username=user, password=pwd)
            if username:
                # 注意 这不能写跳转页面， 因为用ajax，只能接收数据，ajax.success:function(){}
                auth.login(request, username)  # request.user == 当前登录对象
                response["user"] = username.username
            else:
                response["msg"] = "username or password error!"
        else:
            response["msg"] = "验证码错误！"

        return JsonResponse(response)

    return render(request, "login.html")


def get_validCode_img(request):
    """
    基于PIL模块 动态生成响应状态码图片
    :param request:
    :return:
    """
    from blogs.utils.validCode import get_valid_code_img
    data = get_valid_code_img(request)
    return HttpResponse(data)


def register(request):
    if request.is_ajax():
        print(request.POST)
        form = UserForm(request.POST)

        response = {"user": None, "msg": None}
        if form.is_valid():
            response["user"] = form.cleaned_data.get("user")

            # 生成一条用户记录
            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar_obj = request.FILES.get("avatar")

            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj

            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)

        else:
            print(form.cleaned_data)
            print(form.errors)
            response["msg"] = form.errors

        return JsonResponse(response)

    form = UserForm()

    return render(request, "register.html", locals())


def logout(request):
    auth.logout(request)  # request.session.flush
    return redirect("/login")


def get_classification_data(username):
    user = UserInfo.objects.filter(username=username).first()

    # 查询当前站点对象
    blog = user.blog

    cate_list = Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title",
                                                                                                                "c")
    tag_list = Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title", "c")

    date_list = Article.objects.filter(user=user).extra(
        select={"y_m_date": "date_format(create_time, '%%Y-%%m')"}).values("y_m_date").annotate(
        c=Count("nid")).values_list("y_m_date", "c")
    return {"user": user, "blog": blog, "cate_list": cate_list, "tag_list": tag_list, "date_list": date_list}


def home_site(request, username, **kwargs):
    """
    个人站点 视图函数
    :param request:
    :return:
    """
    print("kwargs", kwargs)

    print(username)
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, "not_found.html")

    # 查询当前站点对象
    blog = user.blog

    # 当前用户 或者 当前站点 对应的所有文章
    # 基于对象查询
    # article_list = user.article_set.all()
    # 基于 __

    article_list = Article.objects.filter(user=user)

    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")

        if condition == "category":
            article_list = article_list.filter(category__title=param)
        elif condition == "tag":
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split("-")
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    # 查询每一个分类的名称以及对应的文章数
    # ret = Category.objects.values("pk").annotate(c=Count("article__title")).values("title", "c")
    # print(ret)

    # 查询当前站点的每一个分类名称以及对应的文章数
    # cate_list = Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values_list("title", "c")
    # print(ret)

    # 查询当前站点的每一个标签名称以及对应的文章数
    # tag_list = Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title","c")
    # print(tag_list)

    # 查询当前站点每一个年月的名称以及对应的文章数
    # ret = Article.objects.extra(select={"is_recent": "create_time > '2017-09-05'"}).values("title", "is_recent")
    # print(ret)

    # ret = Article.objects.extra(select={"y_m_date": "date_format(create_time, '%%Y-%%m-%%d')"}).values("title", "y_m_date")
    # 方式1：
    # date_list = Article.objects.filter(user=user).extra(select={"y_m_date": "date_format(create_time, '%%Y-%%m')"}).values("y_m_date").annotate(c=Count("nid")).values_list("y_m_date","c")
    # print(date_list)

    # 方式2：
    from django.db.models.functions import TruncMonth, TruncDay
    # date_list = Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values_list("month").annotate(c=Count("month")).values_list("month", "c")

    return render(request, "home_site.html", locals())


def article_detail(request, username, article_id):
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog

    article_obj = Article.objects.filter(pk=article_id).first()
    comment_list = Comment.objects.filter(article_id=article_id)
    return render(request, "article_detail.html", locals())


from django.db.models import F
from django.http import JsonResponse


def digg(request):
    # 点赞视图参数
    print(request.POST)
    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))
    # 点赞人及当前登录人
    user_id = request.user.pk

    obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()

    response = {"state": True}
    if not obj:
        ard = ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
        queryset = Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F("up_count") + 1)
        else:
            queryset.update(down_count=F("down_count") + 1)
    else:
        response["state"] = False
        response["handled"] = obj.is_up

    return JsonResponse(response)


def comment(request):
    response = {}

    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    pid = request.POST.get("pid")
    user_id = request.user.pk

    with transaction.atomic():
        # 事务操作
        comment_obj = Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                             parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

    article_title = comment_obj.article.title
    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %X")
    response["username"] = request.user.username
    response["content"] = content

    if pid:
        response["parent_comment_username"] = comment_obj.parent_comment.user.username
        response["parent_comment_content"] = comment_obj.parent_comment.content

    # 发送邮件
    from django.core.mail import send_mail
    from BlogSystem import settings
    mail = (
        "你的文章%s新增了一条文章内容" % article_title,
        content,
        settings.EMAIL_HOST_USER,
        [""]
    )
    import threading
    t = threading.Thread(target=send_mail, args=mail)
    t.start()

    return JsonResponse(response)


def get_comment_tree(request):
    article_id = request.GET.get("article_id")
    ret = Comment.objects.filter(article_id=article_id).order_by("pk").values("pk", "content", "parent_comment_id",
                                                                              "create_time", "user__username")
    ret = list(ret)
    print(ret)
    return JsonResponse(ret, safe=False)  # 可以传非字典格式


@login_required
def cn_backend(request):
    """
    后台管理的首页
    :param request:
    :return:
    """
    article_list = Article.objects.filter(user=request.user)

    return render(request, "backend/backend.html", locals())


from bs4 import BeautifulSoup


@login_required
def add_article(request):
    """
        后台管理的添加书籍视图函数
        :param request:
        :return:
        """
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # 防止xss攻击,过滤script标签
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all():
            if tag.name == "script":
                tag.decompose()

        # 构建摘要数据,获取标签字符串的文本前150个符号

        desc = soup.text[0:150] + "..."

        Article.objects.create(title=title, desc=desc, content=str(soup), user=request.user)
        return redirect("/cn_backend/")

    return render(request, "backend/add_article.html")


def upload(request):
    import os
    import json
    print(request.FILES)
    img = request.FILES.get("upload_img")
    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", img.name)
    with open(path, "wb") as f:
        for line in img:
            f.write(line)
            f.flush()
    response = {
        "error": 0,
        "url": "/media/add_article_img/%s" % img.name
    }
    return HttpResponse(json.dumps(response))
