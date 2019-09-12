"""BlogSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from django.views.static import serve
from blogs import views
from BlogSystem import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("login/", views.login),
    path("index/", views.index),
    re_path("^$", views.index),
    path("get_validCode_img/", views.get_validCode_img),
    path("register/", views.register),
    path("logout/", views.logout),

    # 点赞
    path("digg/", views.digg),
    # 评论
    path("comment/", views.comment),
    # 获取评论树相关数据
    path("get_comment_tree/", views.get_comment_tree),

    # 文本编辑器上传图片url
    path('upload/', views.upload),

    # 后台管理url
    re_path(r"cn_backend/$", views.cn_backend),
    re_path(r"cn_backend/add_article/$", views.add_article),

    # media配置
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),

    # 个人站点的跳转
    re_path(r"^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$", views.home_site),

    # 个人站点的URL
    re_path(r"^(?P<username>\w+)$", views.home_site),

    re_path(r"^(?P<username>\w+)/articles/(?P<article_id>\d+)$", views.article_detail),

]
