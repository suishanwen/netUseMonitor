import requests


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
            'Content-Type': 'application/x-www-form-urlencoded',
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
            instance_id = self.get_id()
            if instance_id and self.console(instance_id):
                return self.restart(instance_id)
        return 0


