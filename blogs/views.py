from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.db.models import Count
# Create your views here.

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


def home_site(request, username):
    """
    个人站点 视图函数
    :param request:
    :return:
    """
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

    # 查询每一个分类的名称以及对应的文章数
    # ret = Category.objects.values("pk").annotate(c=Count("article__title")).values("title", "c")
    # print(ret)


    # 查询当前站点的每一个分类名称以及对应的文章数
    # ret = Category.objects.filter(blog=blog).values("pk").annotate(c=Count("article__title")).values("title", "c")
    # print(ret)

    # 查询当前站点的每一个标签名称以及对应的文章数
    # tag_list = Tag.objects.filter(blog=blog).values("pk").annotate(c=Count("article")).values_list("title","c")
    # print(tag_list)

    # 查询当前站点每一个年月的名称以及对应的文章数
    # ret = Article.objects.extra(select={"is_recent": "create_time > '2017-09-05'"}).values("title", "is_recent")
    # print(ret)

    # ret = Article.objects.extra(select={"y_m_date": "date_format(create_time, '%%Y-%%m-%%d')"}).values("title", "y_m_date")
    # 方式1：
    # date_list = Article.objects.filter(user=user).extra(select={"y_m_date": "date_format(create_time, '%%Y-%%m')"}).values("y_m_date").annotate(c=Count("nid")).values("y_m_date","c")
    # print(date_list)

    # 方式2：
    from django.db.models.functions import TruncMonth, TruncDay
    ret = Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values_list("month").\
        annotate(c=Count("month")).values_list("month")
    print(ret)

    return render(request, "home_site.html", locals())
