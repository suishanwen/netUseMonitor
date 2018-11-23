from django.http import HttpResponse
from django.shortcuts import render

from telecom.models import Card
from login.Login import login, dxPwdEncrypt


def hello(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'hello.html', context)


def index(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'index.html', context)


# 数据库操作
def add(request):
    user = ""
    # 获取单个对象
    if 'user' in request.GET:
        user = request.GET['user']
    context = {}
    context['user'] = user
    return render(request, 'add.html', context)


def addCard(request):
    request.encoding = 'utf-8'
    phone = ''
    password = ''
    icc_id = ''
    user = ''
    sort = None
    remark = ''
    if 'phone' in request.POST:
        phone = request.POST['phone']
    if 'password' in request.POST:
        password = request.POST['password']
    if 'icc_id' in request.POST:
        icc_id = request.POST['icc_id']
    if 'user' in request.POST:
        user = request.POST['user']
    if 'sort' in request.POST:
        sort = request.POST['sort']
    if 'remark' in request.POST and request.POST['remark'] != '':
        remark = int(request.POST['remark'])
    card = Card(phone=phone, password=password, encryptPassword=dxPwdEncrypt(password).strip(), icc_id=icc_id,
                user=user, remark=remark,
                sort=sort)
    card.save()
    return HttpResponse("添加成功！")


def update(request):
    # 修改其中一个id=1的name字段，再save，相当于SQL中的UPDATE
    pk = request.POST['pk']
    phone = request.POST['phone']
    # password = request.POST['password']
    sort = request.POST['sort']
    icc_id = request.POST['icc_id']
    remark = request.POST['remark']

    card = Card.objects.get(pk=pk)
    card.phone = phone
    # card.password = password
    card.sort = sort
    card.icc_id = icc_id
    card.remark = remark
    card.save()

    # 另外一种方式
    # Card.objects.filter(pk=pk).update(sort=sort)

    # 修改所有的列
    # Test.objects.all().update(name='Google')
    return HttpResponse("保存成功！")


def delete(request):
    # 删除id=1的数据
    pk = request.POST['pk']
    card = Card.objects.get(pk=pk)
    card.delete()

    # 另外一种方式
    # Card.objects.filter(pk=pk).delete()

    # 删除所有数据
    # Test.objects.all().delete()

    return HttpResponse("删除成功")


# 数据库操作
def query(request):
    user = ''
    if 'user' in request.GET:
        user = request.GET['user']
    list = Card.objects.filter(user=user).order_by("sort")
    context = {
        "data": list
    }
    return render(request, 'list.html', context)


# 数据库操作
def queryNet(request):
    pk = request.POST['pk']
    card = Card.objects.get(pk=pk)
    card.net = login(card.phone, card.password)
    card.save()
    return HttpResponse("查询成功:%s" % card.net)


# 数据库操作
def emptyNetAll(request):
    user = request.POST['user']
    Card.objects.filter(user=user).update(net='')
    return HttpResponse("%s已清空" % user)
