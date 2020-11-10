import json
import requests
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger('django')


class Login2:
    def __init__(self, host, username, password, instance):
        self.req = requests.session()
        self.host = host
        self.username = username
        self.password = password
        self.instance = instance
        self.headers = {
            'Host': f'{self.host}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,af;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Origin': f'http://{self.host}',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Referer': f'http://{self.host}/user/login.asp',
        }

    def login(self):
        url = f'http://{self.host}/user/userlogin.asp'
        self.headers['Referer'] = url
        resp = self.req.post(url, data={'username': self.username, 'password': self.password}, allow_redirects=True,
                             timeout=20, headers=self.headers)
        return resp.status_code == 200

    def get_id(self):
        url = f'http://{self.host}/user/vpsadm.asp'
        self.headers['Referer'] = url
        self.headers['Content-Type'] = ''
        resp = self.req.get(url, timeout=20, headers=self.headers)
        if resp.status_code == 200:
            text = resp.text[resp.text.find(self.instance):resp.text.find(self.instance) + 700]
            text = text[text.find('?id=') + 4:text.find('?id=') + 14]
            text = text[0:text.find('&')]
            return text
        else:
            return ""

    def get_vms(self):
        url = f'http://{self.host}/user/vpsadm.asp'
        self.headers['Referer'] = url
        self.headers['Content-Type'] = 'text/html;charset=UTF-8'
        resp = self.req.get(url, timeout=20, headers=self.headers)
        vms = []
        if resp.status_code == 200:
            resp.encoding = "gbk"
            soup = BeautifulSoup(resp.text[resp.text.index("<table"):resp.text.index("/table")], 'html.parser')
            trs = soup.select("tr")
            for tr in trs:
                tds = tr.find_all("td")
                if len(tds) < 2:
                    continue
                remarks = tds[1].find("div").text.strip()
                if remarks:
                    vm = {}
                    user = 1
                    sort = remarks.strip()
                    index1 = remarks.upper().find("2B")
                    if index1 != -1:
                        user = "sw"
                        sort = remarks[index1 + 2:].strip()
                    else:
                        sort = int(sort[1:])
                    vm["userId"] = user
                    vm["sortNo"] = sort
                    vm["area"] = tds[1].contents[0]
                    vm["instance"] = tds[2].find("div").contents[0].strip()
                    text = tds[3].find("div").find("a")['href']
                    text = text[text.find('?id=') + 4:text.find('?id=') + 14]
                    text = text[0:text.find('&')]
                    vm["resetId"] = text
                    vm["remoteIp"] = tds[3].find("div").find("a").contents[0].split("远程IP:")[1].strip()
                    tmp = tds[3].find("div").find("a").contents[6].strip().split("密码")
                    vm["adslUser"] = tmp[0].split("：")[1]
                    vm["adslPwd"] = tmp[1].split("：")[1]
                    vm["openingTime"] = tds[5].find("div").contents[0].strip()
                    vm["expireTime"] = tds[5].find("div").contents[2].strip()
                    vms.append(vm)
        logger.info(f"共抓取到{len(vms)}台机器")
        return vms

    def console(self, id):
        url = f'http://{self.host}/user/vpsadm2.asp?id={id}&go=a'
        self.headers['Referer'] = 'http://263vps.com/user/vpsadm.asp'
        resp = self.req.get(url, timeout=20, headers=self.headers)
        if resp.status_code == 200:
            return 1
        else:
            return 0

    def restart(self, id):
        url = f'http://{self.host}/vpsadm/vpsop.asp?id={id}&op=reset'
        self.headers['Referer'] = f'http://{self.host}/vpsadm/selfvpsmodify.asp?id={id}'
        resp = self.req.get(url, timeout=20, headers=self.headers)
        if resp.status_code == 200:
            return 1
        else:
            return 0

    def reset(self):
        if self.login():
            logger.info(f"{self.username} login success")
            instance_id = self.get_id()
            if instance_id and self.console(instance_id):
                return self.restart(instance_id)
        else:
            logger.info(f"{self.username} login failed")
        return 0

    def track(self):
        if self.login():
            vms = self.get_vms()
            url = 'https://bitcoinrobot.cn/api/direct/updateExt'
            self.headers['Referer'] = url
            self.headers['Content-Type'] = 'application/json;charset=UTF-8'
            resp = self.req.post(url, json.dumps(vms), timeout=30, headers=self.headers)
            logger.info(f"updateExt: {resp.status_code}")
            if resp.status_code == 200:
                return 1
        return 0
