"""
思路:
    1. 拿到主页面的页面源代码, 找到iframe
    2. 从iframe的页面源代码中拿到m3u8文件的地址
    3. 下载第一层m3u8文件(第一层只放了一个地址) -> 下载第二层m3u8文件(视频存放路径，通过请求第一层的地址得到)
    4. 下载视频
    5. 下载秘钥, 进行解密操作（文件m3u8中存在 #EXT-X-KEY:METHOD=AES-128,URI="key.key"说明视频被AES加密，而秘钥地址在URI中）
    6. 合并所有ts文件为一个mp4文件
"""
import requests
from bs4 import BeautifulSoup
import re
import asyncio
import aiohttp
import aiofiles
from Crypto.Cipher import AES  # 安装模块pycryptodome
import os


def get_iframe_src(url):
    resp = requests.get(url)
    main_page = BeautifulSoup(resp.text, "html.parser")
    src = main_page.find("iframe").get("src")
    return src
    # return "https://boba.52kuyun.com/share/xfPs9NPHvYGhNzFp"  # 为了测试而选择直接返回url，实在访问速度太慢


def get_first_m3u8_url(url):
    resp = requests.get(url)
    # print(resp.text)
    obj = re.compile(r'var main = "(?P<m3u8_url>.*?)"', re.S)
    m3u8_url = obj.search(resp.text).group("m3u8_url")
    # print(m3u8_url)
    return m3u8_url


def download_m3u8_file(url, name):
    resp = requests.get(url)
    with open(name, mode="wb") as f:
        f.write(resp.content)


async def download_ts(url, name, session):
    async with session.get(url) as resp:
        async with aiofiles.open(f"video/{name}", mode="wb") as f:
            await f.write(await resp.content.read())  # 把下载到的内容写入到文件中
    print(f"{name}下载完毕")


async def aio_download(up_url):  # 传过来的up_url为: "https://boba.52kuyun.com/20170906/Moh2l9zV/hls/",用来拼接ts链接
    tasks = []
    async with aiohttp.ClientSession() as session:  # 提前准备好session，当参数传递出去，避免每个任务都要创建一次session
        async with aiofiles.open("越狱第一季第一集_second_m3u8.txt", mode="r", encoding='utf-8') as f:  # 异步就需要加async
            async for line in f:
                if line.startswith("#"):
                    continue
                # line就是xxxxx.ts,即ts链接
                line = line.strip()  # 去掉没用的空格和换行
                # 拼接真正的ts路径
                ts_url = up_url + line
                task = asyncio.create_task(download_ts(ts_url, line, session))  # 创建任务
                tasks.append(task)

            await asyncio.wait(tasks)  # 等待任务结束


def get_key(url):
    resp = requests.get(url)
    return resp.text


async def dec_ts(name, key):
    # IV放0就可以，但必须是字节（注意:key有多少位，IV中的0就放多少个）
    aes = AES.new(key=key, IV=b"0000000000000000", mode=AES.MODE_CBC)
    # 读文件,通过aes去解密,解密完后还要存起来
    async with aiofiles.open(f"video/{name}", mode="rb") as f1, \
            aiofiles.open(f"video/temp_{name}", mode="wb") as f2:
        bs = await f1.read()  # 从源文件读取内容
        await f2.write(aes.decrypt(bs))  # 把解密好的内容写入文件
    print(f"{name}处理完毕")


async def aio_dec(key):
    # 解密
    tasks = []
    # 若直接读已经下载好的ts文件名比较困难，可以选择先读m3u8文件，继而读取ts文件
    async with aiofiles.open("越狱第一季第一集_second_m3u8.txt", mode="r", encoding="utf-8") as f:
        async for line in f:
            if line.startswith("#"):
                continue
            line = line.strip()
            # 开始创建异步任务
            task = asyncio.create_task(dec_ts(line, key))
            tasks.append(task)
        await asyncio.wait(tasks)


def merge_ts():  # 不需要异步,其目的是拼接文件名,只需要从头读下来
    # mac: cat 1.ts 2.ts 3.ts > xxx.mp4
    # windows: copy /b 1.ts+2.ts+3.ts xxx.mp4
    lst = []
    with open("越狱第一季第一集_second_m3u8.txt", mode="r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            line = line.strip()
            lst.append(f"video/temp_{line}")

    s = " ".join(lst)  # 1.ts 2.ts 3.ts
    os.system(f"cat {s} > movie.mp4")  # mac用法
    print("搞定!")


def main(url):
    # 1. 拿到主页面的页面源代码, 找到iframe对应的url
    iframe_src = get_iframe_src(url)
    # 2. 拿到第一层的m3u8文件的下载地址，即"/20170906/Moh2l9zV/index.m3u8?sign=548ae366a075f0f9e7c76af215aa18e1"
    first_m3u8_url = get_first_m3u8_url(iframe_src)
    # 拿到iframe的域名，用来拼接真正的m3u8地址。即"https://boba.52kuyun.com/share/xfPs9NPHvYGhNzFp"
    iframe_domain = iframe_src.split("/share")[0]
    # 拼接出真正的m3u8的下载路径,即"https://boba.52kuyun.com/20170906/Moh2l9zV/index.m3u8?sign=548ae366a075f0f9e7c76af215aa18e1"
    first_m3u8_url = iframe_domain + first_m3u8_url
    # print(first_m3u8_url)
    # 3.1 下载第一层m3u8文件
    download_m3u8_file(first_m3u8_url, "越狱第一季第一集_first_m3u8.txt")
    # 3.2 下载第二层m3u8文件
    with open("越狱第一季第一集_first_m3u8.txt", mode="r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):  # 若以#开头就舍弃
                continue
            else:
                line = line.strip()  # 去掉空白或者换行符  得到"hls/index.m3u8"
                # 准备拼接第二层m3u8的下载路径
                # 规律: "https://boba.52kuyun.com/20170906/Moh2l9zV/" + hls/index.m3u8
                # 结果: "https://boba.52kuyun.com/20170906/Moh2l9zV/hls/index.m3u8"
                second_m3u8_url = first_m3u8_url.split("index.m3u8")[0] + line
                download_m3u8_file(second_m3u8_url, "越狱第一季第一集_second_m3u8.txt")
                print("m3u8文件下载完毕")

    # 4. 下载视频
    # 第二层m3u8文件中的ts链接也需要拼接
    # 拼接示例: "https://boba.52kuyun.com/20170906/Moh2l9zV/hls/" + cFN8o3436000.ts
    second_m3u8_url_up = second_m3u8_url.replace("index.m3u8", "")
    # 异步协程(适合处理拥有大量IO的多任务操作)
    asyncio.run(aio_download(second_m3u8_url_up))  # 测试的使用可以注释掉，因为实在太慢了

    # 5.1 拿到秘钥
    key_url = second_m3u8_url_up + "key.key"  # 偷懒写法, 正常应该去m3u8文件里去找（即#EXT-X-KEY:METHOD=AES-128,URI="key,key"）
    key = get_key(key_url)  # 下载秘钥
    # 5.2 解密（有很多文件需要读出来，解密，再存到一个新文件中去。其中涉及大量IO操作，因此需要异步执行）
    asyncio.run(aio_dec(key))

    # 6. 合并ts文件为mp4文件
    merge_ts()


if __name__ == '__main__':
    url = "https://www.91kanju.com/vod-play/541-2-1.html"
    main(url)