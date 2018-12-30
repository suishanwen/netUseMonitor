import sys
import requests
import os
import logging

# 屏蔽warning信息
requests.packages.urllib3.disable_warnings()
logger = logging.getLogger('django')


def py_download(url, file_path):
    # 第一次请求是为了得到文件总大小
    r1 = requests.get(url, stream=True, verify=False)
    total_size = int(r1.headers['Content-Length'])

    # 这重要了，先看看本地文件下载了多少
    if os.path.exists(file_path):
        temp_size = os.path.getsize(file_path)  # 本地已经下载的文件大小
    else:
        temp_size = 0
    if temp_size == total_size:
        logger.info(file_path + "已存在")
        return
    else:
        # 显示一下下载了多少
        logger.info("开始下载: %s, 总共：%d ,当前：%d" % (url, total_size, temp_size))
    # 核心部分，这个是请求下载时，从本地文件已经下载过的后面下载
    headers = {'Range': 'bytes=%d-' % temp_size}
    # 重新请求网址，加入新的请求头的
    r = requests.get(url, stream=True, verify=False, headers=headers)
    # 下面写入文件也要注意，看到"ab"了吗？
    # "ab"表示追加形式写入文件
    with open(file_path, "ab") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                temp_size += len(chunk)
                f.write(chunk)
                f.flush()
                ###这是下载实现进度显示####
                done = int(50 * temp_size / total_size)
                sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
                sys.stdout.flush()
    logger.info(" %s 下载完成, 总共：%d ,当前：%d" % (url, total_size, temp_size))
    print()  # 避免上面\r 回车符
