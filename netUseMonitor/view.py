from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q

from login.Login2 import Login2
from telecom.models import Card, Votes, Online, Download
from login.Login import login
import requests
import time
import os
import demjson
import logging
import configparser
import threading
from bs4 import BeautifulSoup
from util.download import py_download, is_downloading, is_downloaded, download_complete

lock = threading.Lock()
config = configparser.ConfigParser()
config.read("./netUseMonitor/cache.ini")
logger = logging.getLogger('django')

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


def query(request):
    user = ''
    if 'user' in request.GET:
        user = request.GET['user']
    list = Card.objects.filter(user=user).order_by("sort")
    context = {
        "data": list
    }
    return render(request, 'list.html', context)


def query_data(request):
    user = ''
    if 'user' in request.GET:
        user = request.GET['user']
    list = Card.objects.filter(user=user).order_by("sort")
    dict_list = []
    for card in list:
        dict = card.__dict__
        del dict["_state"]
        del dict["password"]
        # dict["update"] = time.mktime(dict["update"].timetuple())
        dict_list.append(dict)
    return HttpResponse("%s" % demjson.encode(dict_list))


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
        self.ip = 1


def get_votes():
    logger.info("request from url")
    req = requests.session()
    req.cookies.clear()
    try:
        html = req.get("http://butingzhuan.com/tasks.php?t=" + str(time.time()), allow_redirects=False,
                       timeout=10).content
    except requests.Timeout:
        return "timeout"
    result = str(html, 'gbk')
    result = result[result.index("时间</td>"):]
    result = result[0:result.index("qzd_yj")]
    result = result[result.index("<tr class='blank'>"):]
    result = result[0:find_last(result, "<tr class='blank'>")]
    soup = BeautifulSoup(result, 'html.parser')
    trs = soup.find_all("tr")
    vote_projects = []
    for tr in trs:
        vote_project = VoteProject()
        tds = tr.find_all("td")
        if tds[2].find("a").string.find("挂机") != -1:
            continue
        if str(tr).find("不换") != -1:
            vote_project.ip = 0
        vote_project.projectName = tds[2].find("a").string.replace(" ", "")
        vote_project.hot = tds[3].text.replace("(", "").replace(")", "")
        vote_project.price = tds[5].string
        vote_project.finishQuantity = tds[7]["title"].split("/")[0]
        total_str = tds[7]["title"].split("/")[1]
        vote_project.totalRequire = total_str[0:total_str.find(" ")]
        vote_project.remains = tds[7].string
        vote_project.backgroundAddress = tds[8].find("a")["href"]
        vote_project.downloadAddress = tds[9].find("a")["href"].replace(" ", "")
        vote_project.idType = tds[10].find("input")["value"].split("-")[0]
        vote_project.backgroundNo = tds[12].string
        vote_project.refreshDate = tds[13].string
        vote_projects.append(vote_project.__dict__)
    return demjson.encode(vote_projects)


def identity_online(identity, arr_drop):
    try:
        online = Online.objects.get(identity=identity)
        online.arrDrop = arr_drop
        online.save()
    except Online.DoesNotExist:
        Online(identity=identity, arrDrop=arr_drop).save()


# 投票数据获取
def voteInfo(request):
    is_adsl = ''
    if 'isAdsl' in request.GET:
        is_adsl = request.GET['isAdsl']
    if 'id' in request.GET:
        arr_drop = ''
        if 'arrDrop' in request.GET:
            arr_drop = request.GET['arrDrop']
        identity_online(request.GET['id'], arr_drop)
    votes = Votes.objects.get(pk=1)
    now = int(time.time())
    if now - votes.time > 15 or votes.info == "timeout":
        # 是否正在请求
        count = 0
        requesting = config.get("voteInfo", "requesting")
        while requesting == "1":
            count += 1
            logger.info("waiting requesting *%d!" % count)
            time.sleep(1)
            requesting = config.get("voteInfo", "requesting")
            if count >= 10:
                config.set("voteInfo", "requesting", "0")
                return HttpResponse("timeout")
        if count > 0:
            votes = Votes.objects.get(pk=1)
        else:
            config.set("voteInfo", "requesting", "1")
            votes.info = get_votes()
            votes.time = int(time.time())
            votes.save()
            config.set("voteInfo", "requesting", "0")
    try:
        str = votes.info.replace('None', '')
        vote_projects = demjson.decode(str)
    except Exception as e:
        logger.info(e)
        vote_projects = demjson.decode(get_votes())
    vote_projects_filtered = []
    for project in vote_projects:
        if project["ip"] == 0 and is_adsl != '1':
            continue
        vote_projects_filtered.append(project)
    return HttpResponse("%s" % demjson.encode(vote_projects_filtered))


def list_vote_info(request):
    votes = Votes.objects.get(pk=1)
    now = int(time.time())
    if now - votes.time > 15 or votes.info == "timeout":
        votes.info = get_votes()
        votes.time = int(time.time())
    else:
        try:
            str = votes.info.replace('None', '')
            votes.info = demjson.decode(str)
        except Exception as e:
            logger.info(e)
            votes.info = demjson.decode(get_votes())
    context = {"data": votes.info}
    return render(request, 'voteinfo.html', context)


def list_online_data(request):
    user = ''
    if 'user' in request.POST:
        user = request.POST['user']
    if user == '':
        list = Online.objects.all().order_by("update").reverse()
    elif user == 'sw':
        list = Online.objects.filter(Q(identity__icontains="AQ-239356") | Q(identity__icontains="Q7-21173")).order_by(
            "update").reverse()
    else:
        list = Online.objects.filter(Q(identity__icontains="AQ-14") | Q(identity__icontains="Q7-43")).order_by(
            "update").reverse()
    dict_list = []
    for item in list:
        dict = item.__dict__
        del dict["_state"]
        dict_list.append(dict)
    return HttpResponse('%s' % demjson.encode(dict_list))


def list_online(request):
    user = ''
    if 'user' in request.GET:
        user = request.GET['user']
    if user == '':
        context = {"data": Online.objects.all().order_by("update").reverse()}
    elif user == 'sw':
        context = {
            "data": Online.objects.filter(Q(identity__icontains="AQ-239356") | Q(identity__icontains="Q7-21173"))
                .order_by("update").reverse()
        }
    else:
        context = {
            "data": Online.objects.filter(Q(identity__icontains="AQ-14") | Q(identity__icontains="Q7-43"))
                .order_by("update").reverse()
        }
    return render(request, 'online.html', context)


def log(request):
    return render(request, 'log.html')


#
# def is_downloading(url):
#     try:
#         Download.objects.get(url=url)
#     except Download.DoesNotExist:
#         return False
#     return True


# 投票数据获取
def download(request):
    req = requests.session()
    req.cookies.clear()
    url = request.GET['url']
    file_name = url[find_last(url, "/") + 1:]
    path_name = "/etc/nginx/html/file/vote/" + file_name
    count = 0
    while is_downloading(url):
        count += 1
        logger.info("waiting downloading %s *%d!" % file_name, count)
        time.sleep(1)
        if count > 300:
            download_complete(url)
    if is_downloaded(url):
        return HttpResponse("ok")
    with lock:
        if is_downloading(url):
            return HttpResponse("err")
        try:
            py_download(url, path_name)
        except Exception:
            return HttpResponse("err")
    return HttpResponse("ok")


def list_downloads(request):
    all_files = []
    for root, dirs, files in os.walk("/etc/nginx/html/file/vote/"):
        if len(files) > 0:
            for file in files:
                all_files.append(file)
    context = {
        "data": all_files
    }
    return render(request, 'download.html', context)


def del_download(request):
    file = request.GET['file']
    os.remove("/etc/nginx/html/file/vote/%s" % file)
    return HttpResponse("ok")


def empty_downloads(request):
    path = "/etc/nginx/html/file/vote/"
    for i in os.listdir(path):
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file):
            os.remove(path_file)
    return HttpResponse("ok")


def get_cookies(request):
    req = requests.session()
    req.cookies.clear()
    try:
        resp = req.post("http://10.10.252.58:3000/login",
                        data={"user": "cengkk@163.com", "email": "", "password": "demo@123%^&"}, allow_redirects=False,
                        timeout=10)
        print(resp.status_code)
        response = HttpResponse(demjson.encode({
            "status": 200,
            "host": "10.10.252.58",
            "path": "/",
            "cookies": {
                "grafana_user": resp.cookies.get("grafana_user"),
                "grafana_remember": resp.cookies.get("grafana_remember"),
                "grafana_sess": resp.cookies.get("grafana_sess")
            }
        }))
    except requests.Timeout:
        response = HttpResponse({
            "status": 500,
        })
        print("timeout")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "POST,GET,OPTIONS"
    response["Access-Control-Max-Age"] = 1000
    response["Access-Control-Allow-Headers"] = "*"
    return response


def reset(request):
    host = request.POST['host']
    username = request.POST['username']
    password = request.POST['password']
    reset_id = request.POST['resetId']
    instance = request.POST['instance']
    login2 = Login2(host, username, password, reset_id, instance)
    return HttpResponse(login2.reset())


def track(request):
    host = request.POST['host']
    username = request.POST['username']
    password = request.POST['password']
    login2 = Login2(host, username, password, "", "")
    return HttpResponse(login2.track())
