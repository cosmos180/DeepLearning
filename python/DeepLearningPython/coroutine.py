'''
Author       : bughero jinxinhou@tuputech.com
Date         : 2023-11-07 16:00:15
LastEditors  : bughero jinxinhou@tuputech.com
LastEditTime : 2023-11-20 16:57:12
FilePath     : /DeepLearning/python/DeepLearningPython/coroutine.py
Description  : 

Copyright (c) 2023 by Antyme, All Rights Reserved. 
'''
import asyncio
from collections.abc import Callable, Iterable, Mapping
from threading import Thread
import time
from typing import Any

# 消费者


def customer():
    a = 0
    while True:
        a = yield a
        print("a = %s" % a)

# 生产者


def producer(c):
    c.send(None)  # 启动生成器
    for i in range(5):
        b = c.send(i)
        print("b = %s" % b)
    c.close()

# A generator function


def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('[CONSUMER] Consuming %s...' % n)
        time.sleep(10)
        r = '200 OK'


def produce(c):
    c.send(None)
    n = 0
    while n < 5:
        n = n + 1
        print('[PRODUCER] Producing %s...' % n)
        r = c.send(n)
        print('[PRODUCER] Consumer return: %s' % r)
    c.close()


# c = consumer()
# produce(c)


def factorize(number):
    for i in range(1, number+1):
        if number % i == 0:
            yield i


numbers = [2132079, 1214579, 1516637, 1852285]


class FactorizeThread(Thread):
    def __init__(self, number):
        super().__init__()
        self.number = number

    def run(self) -> None:
        self.factors = list(factorize((number)))


# start = time.time()

# threads = []
# for number in numbers:
#     # list(factorize((number)))
#     thread = FactorizeThread(number)
#     thread.start()
#     threads.append(thread)

# for thread in threads:
#     thread.join()

# end = time.time()
# delta = end - start
# print(f"Took {delta:.3f} seconds.")


class Counter:
    def __init__(self) -> None:
        self.count = 0

    def increment(self, offset):
        self.count += offset


def woker(sensor_index, how_many, counter: Counter):
    for _ in range(how_many):
        counter.increment(1)


how_many = 10**5
counter = Counter()

threads = []
for i in range(5):
    thread = Thread(target=woker, args=(i, how_many, counter))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

excepted = how_many * 5
found = counter.count
print(f"Counter should be {excepted}, got {found}")
