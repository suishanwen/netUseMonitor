import requests
import traceback
import os
import PyV8
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract

basePath = "./login/"


class Login:
    def __init__(self, phoneNo, password):
        self.req = requests.session()
        self.phoneNo = phoneNo
        self.password = password
        self.provinceID = ''
        self.EcsLoginToken = ''
        self.png = ''
        self.headers = {
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

    def getCaptcha(self):
        self.req.cookies.clear()
        url = 'http://login.189.cn/web/login/ajax'

        data_1 = {
            'm': 'checkphone',
            'phone': self.phoneNo
        }

        data_2 = {
            'm': "loadlogincaptcha",
            'Account': self.phoneNo,
            'UType': "201",
            'ProvinceID': "01",
            'AreaCode': "",
            'CityNo': ""
        }

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': 'login.189.cn',
            'Origin': 'http://login.189.cn',
            'Referer': 'http://login.189.cn/login',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }

        try:
            ret = self.req.post(url, headers=headers, data=data_1).json()
            data_2 = {
                'm': 'captcha',
                'account': self.phoneNo,
                'uType': '201',
                'ProvinceID': ret['provinceId'],
                'areaCode': '',
                'cityNo': ''
            }
            self.provinceID = ret['provinceId']
            ret = self.req.post(url, headers=headers, data=data_2).json()

            need_image = False
            if ret.get('CaptchaFlag'):
                need_image = True
            elif ret.get('captchaFlag'):
                need_image = True
            if need_image:
                headers = {
                    'Accept': 'image/png,image/*;q=0.8,*/*;q=0.5',
                    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Host": "login.189.cn",
                    "Upgrade-Insecure-Requests": "1",
                    "Referer": "http://login.189.cn/login",
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"
                }

                url = "http://login.189.cn/captcha?419b8486264447ae8680cb8298af8de6&source=login&width=100&height=37&0.39513306694910844"

                resp = self.req.post(url, headers=headers, timeout=10)
                self.EcsCaptchaKey = resp.cookies.get('EcsCaptchaKey')
                filename = self.phoneNo + '.png'
                self.png = basePath + "" + filename
                save_file(basePath, filename, resp.content)

                return {"errorCode": "0", "imgName": filename}
            else:
                return {"errorCode": "0"}

        except:
            print('电信获取验证码失败！ | [%s] | %s' % (self.phoneNo, traceback.format_exc()))
        finally:
            self.req.close()

    def login(self, captcha, callback):
        params = {
            'Account': self.phoneNo,
            'UType': '201',
            'ProvinceID': '25',
            'AreaCode': '',
            'CityNo': '',
            'RandomFlag': '0',
            'Password': self.password,
            'Captcha': captcha
        }
        try:
            loginRet = self.dxCommLogin(params)
            if loginRet['errorCode'] != '0':
                return loginRet
            return {"errorCode": "0", "token": self.EcsLoginToken}

        except:
            print('登录失败! | [%s] %s' % (self.phoneNo, traceback.format_exc()))
            return {"errorCode": "10001", "errorMsg": "系统错误！请联系客服或稍候再试！"}
        finally:
            self.req.close()

    def getTaocan(self):
        url = 'http://www.189.cn/dqmh/order/getTaoCan.do'
        ret = self.req.post(url).json()
        info = ret["obj"]['userresourcequeryfor189home']['commonFlow']
        total = info["total"]
        surplus = info["Surplus"]
        used = info["used"]
        net = '套餐流量：%s %s，剩余流量：%s %s, 已使用：%s %s' % (
            total["value"], total["unit"],
            surplus["value"], surplus["unit"],
            used["value"], used["unit"]
        )
        print(net)
        return net

    def dxCommLogin(self, params):
        url = 'http://login.189.cn/web/login'
        resp = self.req.post(url, data=params, allow_redirects=False, timeout=10)
        if resp.status_code == 200:

            soup = BeautifulSoup(resp.text, 'html.parser')
            errorMsg = soup.find(id='loginForm').attrs['data-errmsg']
            if errorMsg:
                if u'密码错误' in errorMsg:
                    return {"errorCode": "20008", "errorMsg": "你输入的密码和账户名不匹配"}
                elif u'验证码' in errorMsg:
                    return {"errorCode": "20014", "errorMsg": "验证码输入不正确"}
                elif u'密码过于简单' in errorMsg:
                    return {"errorCode": "20078", "errorMsg": "密码过于简单，请修改密码后重试！"}
                elif u'账号锁定' in errorMsg:
                    return {'errorCode': '20057', 'errorMsg': '登录失败过多，帐号已被锁定'}
            else:
                return {"errorCode": "10001", "errorMsg": "运营商系统繁忙，请稍后再试！"}

        redirecrUrl = resp.headers['Location']
        if 'http://www.189.cn/500.html' in redirecrUrl:
            return {"errorCode": "10001", "errorMsg": "运营商系统繁忙，请稍后再试！"}
        self.req.get(redirecrUrl, timeout=10, allow_redirects=False)
        return {"errorCode": "0"}

    def image_to_string(self):
        image = Image.open(self.png)
        return pytesseract.image_to_string(image)


def dxPwdEncrypt(pwd):
    with PyV8.JSLocker():
        with PyV8.JSContext() as ctxt:
            with open(basePath + "dx_encrypt.js", 'r') as f:
                js = f.read()
            js += '\n'

            ctxt.eval(js)
            #
            encryptPwd = ctxt.eval("valAesEncryptSet('%s')" % pwd)
            #
            return encryptPwd


def mkdir(path):
    # 去除左右两边的空格
    path = path.strip()
    # 去除尾部 \符号
    path = path.rstrip("\\")

    if not os.path.exists(path):
        os.makedirs(path)

    return path


def save_file(path, file_name, data):
    if data == None:
        return

    mkdir(path)
    if (not path.endswith("/")):
        path = path + "/"
    file = open(path + file_name, "wb")
    file.write(data)
    file.flush()
    file.close()


def login(phone, password):
    # dx = login('19948715071', '915275')
    dx = Login(phone, password)
    errorCode = ""
    count = 0
    while errorCode != '0':
        dx.getCaptcha()
        captcha = dx.image_to_string().replace(" ", "")
        print("识别验证码为：%s" % captcha)
        if len(captcha) != 4 or not captcha.isalnum():
            print("验证码不规范，重新获取")
            continue
        # captcha = input("请输入验证码：")
        count += 1
        print("尝试第%d次登陆" % count)
        res = dx.login(captcha, '')
        errorCode = res['errorCode']
        if errorCode != '0':
            errorMsg = res['errorMsg']
            print(errorMsg)
    print("%s登陆成功" % dx.phoneNo)
    return dx.getTaocan()
