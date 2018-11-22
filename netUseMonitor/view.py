from django.http import HttpResponse
from django.shortcuts import render

from telecom.models import Card


def hello(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'hello.html', context)


def search(request):
    return render(request, 'search.html')


# 数据库操作
def add(request):
    return render(request, 'add.html')


def addCard(request):
    request.encoding = 'utf-8'
    phone = ''
    password = ''
    icc_id = ''
    user = ''
    if 'phone' in request.GET:
        phone = request.GET['phone']
    if 'password' in request.GET:
        password = request.GET['password']
    if 'icc_id' in request.GET:
        icc_id = request.GET['icc_id']
    if 'user' in request.GET:
        user = request.GET['user']
    card = Card(phone=phone, password=password, icc_id=icc_id, user=user)
    card.save()
    return query(request)


def update(request):
    # 修改其中一个id=1的name字段，再save，相当于SQL中的UPDATE
    card = Card.objects.get(id=1)
    card.password = card.password + "-"
    card.save()

    # 另外一种方式
    # Test.objects.filter(id=1).update(name='Google')

    # 修改所有的列
    # Test.objects.all().update(name='Google')

    return HttpResponse("<p>修改成功</p>")


def delete(request):
    # 删除id=1的数据
    list = Card.objects.all()
    list.delete()

    # 另外一种方式
    # Test.objects.filter(id=1).delete()

    # 删除所有数据
    # Test.objects.all().delete()

    return HttpResponse("<p>删除成功</p>")


# 数据库操作
def query(request):
    # 初始化
    response = ""
    response1 = ""

    # 通过objects这个模型管理器的all()获得所有数据行，相当于SQL中的SELECT * FROM
    list = Card.objects.all()

    # filter相当于SQL中的WHERE，可设置条件过滤结果
    # response2 = Card.objects.filter(id=1)

    # 获取单个对象
    # response3 = Card.objects.get(id=1)

    # 限制返回的数据 相当于 SQL 中的 OFFSET 0 LIMIT 2;
    # Card.objects.order_by('name')[0:2]

    # 数据排序
    # Card.objects.order_by("id")

    # 上面的方法可以连锁使用
    # Card.objects.filter(name="runoob").order_by("id")

    # 输出所有数据
    for var in list:
        response1 += str(var.pk) + " " + var.phone + " " + var.password + " " + var.net + "<br/>"
    response = response1
    return HttpResponse("<p>" + response + "</p>")
