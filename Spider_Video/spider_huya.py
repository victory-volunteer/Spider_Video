import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.192 Safari/537.36"
}

# 下载m3u8文件(此链接从二次请求中找到)
m3u8_url = "https://videobd-platform.cdn.huya.com/1048585/1199595959542/42434169/ab32fbf4661295ff6ecc9941d31e0bfd.m3u8?hyvid=743023053&hyauid=1199595959542&hyroomid=1199595959542&hyratio=1300&hyscence=vod&appid=66&domainid=25&srckey=NjZfMjVfNzQzMDIzMDUz&bitrate=2107&client=106&definition=1300&pid=1199595959542&scene=vod&vid=743023053&u=0&t=100&sv=2207211255"
resp2 = requests.get(m3u8_url, headers=headers)
with open("虎牙.m3u8", mode="wb") as f:
    f.write(resp2.content)
resp2.close()
print("m3u8下载完毕")

# 解析m3u8文件
n = 1
with open("虎牙.m3u8", mode="r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()  # 先去掉空格, 空白, 换行符
        if line.startswith("#"):  # 如果以#开头. 就不要
            continue
        line = "https://videohw-platform.cdn.huya.com/1048585/1199595959542/42434169/" + line  # 拼接ts链接地址
        # 下载视频片段
        resp3 = requests.get(line, headers=headers)  # 这里会读不到数据，估计是网站的问题，导致ts文件为空
        f = open(f"video/{n}.ts", mode="wb")
        f.write(resp3.content)
        f.close()
        resp3.close()
        print("完成了{}个".format(n))
        n += 1