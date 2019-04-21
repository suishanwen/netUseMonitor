[![HitCount](http://hits.dwyl.io/suishanwen/netUseMonitor.svg)](http://hits.dwyl.io/suishanwen/netUseMonitor)


使用Python3+django构建web服务。

基于tensorflow训练模型自动识别验证码。

文件服务中转，提升下载速度。

通过websocket实时输出日志。




resolve dependencies:

pip3 install requests

pip3 install bs4

pip3 install pillow

pip3 install demjson

--pip3 install pytesseract

--brew install pytesseract or apt install pytesseract-ocr

pip3 install mysql-connector

pip3 install pymysql

pip3 install django

pip3 install django-crontab

[add PyV8 to python3 /site-packages/PyV8]:

python3>import os>os.path.dirname(os.__file__)




get started:

python3 manage.py crontab add

python3 manage.py crontab show

python3 manage.py crontab remove

python3 manage.py migrate

python3 manage.py makemigrations telecom

python3 manage.py migrate telecom

python3 manage.py createsuperuser

python3 manage.py runserver 0.0.0.0:8000


online application:

https://tl.bitcoinrobot.cn

