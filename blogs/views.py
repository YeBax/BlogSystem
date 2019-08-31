from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
# Create your views here.

from django.contrib import auth
from .blog_form import UserForm


def index(request):
    return render(request, "index.html")


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
    form = UserForm()

    return render(request, "register.html", locals())
