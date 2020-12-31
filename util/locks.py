import threading

locks = {}


def get(url):
    lock = locks.get(url)
    if lock is not None:
        lock.acquire()
    else:
        locks[url] = threading.Lock()
        get(url)


def release(url):
    lock = locks.get(url)
    if lock is not None:
        lock.release()
