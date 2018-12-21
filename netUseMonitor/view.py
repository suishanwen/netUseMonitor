from django.http import HttpResponse
from django.shortcuts import render
from telecom.models import Card
from login.Login import login
import requests
import time
import os
from bs4 import BeautifulSoup

headers = {
    'Host': 'login.189.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'http://login.189.cn/login',
    'Cookie': ''
}


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
    encryptPassword = ''
    icc_id = ''
    user = ''
    sort = None
    remark = ''
    if 'phone' in request.POST:
        phone = request.POST['phone']
    if 'password' in request.POST:
        password = request.POST['password']
    if 'encryptPassword' in request.POST:
        encryptPassword = request.POST['encryptPassword']
    if 'icc_id' in request.POST:
        icc_id = request.POST['icc_id']
    if 'user' in request.POST:
        user = request.POST['user']
    if 'sort' in request.POST and request.POST['sort'] != '':
        sort = int(request.POST['sort'])
    if 'remark' in request.POST:
        remark = request.POST['remark']
    card = Card(phone=phone, password=password, encryptPassword=encryptPassword, icc_id=icc_id,
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
    if sort == '':
        card.sort = None
    else:
        card.sort = int(sort)
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
    card.net = login(card)
    card.save()
    return HttpResponse("%s" % card.net)


# 数据库操作
def loadInfo(request):
    pk = request.GET['pk']
    card = Card.objects.get(pk=pk)
    return HttpResponse("%s" % card.net)


# 数据库操作
def emptyNetAll(request):
    user = request.POST['user']
    Card.objects.filter(user=user).update(net='')
    return HttpResponse("%s已清空" % user)


def find_last(string, str):
    last_position = -1
    while True:
        position = string.find(str, last_position + 1)
        if position == -1:
            return last_position
        last_position = position


class VoteProject(object):
    def __init__(self):
        self.projectName = ""
        self.price = 0
        self.totalRequire = 0
        self.finishQuantity = 0
        self.remains = 0
        self.backgroundNo = ""
        self.backgroundAddress = ""
        self.downloadAddress = ""
        self.idType = ""
        self.hot = 0
        self.refreshDate = ""


# 投票数据获取
def voteInfo(request):
    req = requests.session()
    req.cookies.clear()
    try:
        html = req.get("http://butingzhuan.com/tasks.php?t=" + str(time.time()), allow_redirects=False,
                       timeout=10).content
    except requests.Timeout:
        return HttpResponse("%s" % "timeout")
    result = str(html, 'gbk')
    result = result[result.index("时间</td>"):]
    result = result[0:result.index("qzd_yj")]
    result = result[result.index("<tr class='blank'>"):]
    result = result[0:find_last(result, "<tr class='blank'>")]
    soup = BeautifulSoup(result, 'html.parser')
    trs = soup.find_all("tr")
    vote_projects = []
    for tr in trs:
        if str(tr).find("不换") != -1:
            continue
        vote_project = VoteProject()
        tds = tr.find_all("td")
        vote_project.projectName = tds[2].find("a").string
        vote_project.hot = tds[3].text.replace("(", "").replace(")", "")
        vote_project.price = tds[5].string
        vote_project.finishQuantity = tds[7]["title"].split("/")[0]
        total_str = tds[7]["title"].split("/")[1]
        vote_project.totalRequire = total_str[0:total_str.find(" ")]
        vote_project.remains = tds[7].string
        vote_project.backgroundAddress = tds[8].find("a")["href"]
        vote_project.downloadAddress = tds[9].find("a")["href"]
        vote_project.idType = tds[10].find("input")["value"].split("-")[0]
        vote_project.backgroundNo = tds[12].string
        vote_project.refreshDate = tds[13].string
        vote_projects.append(vote_project.__dict__)
    return HttpResponse("%s" % vote_projects)


# 投票数据获取
def download(request):
    req = requests.session()
    req.cookies.clear()
    url = request.GET['url']
    file_name = url[find_last(url, "/") + 1:]
    path_name = "./dl/" + file_name
    if not os.path.exists(path_name):
        print("dl from url")
        resp = req.get(url)
        with open(path_name, 'wb') as f:
            f.write(resp.content)
    return HttpResponse("ok")
