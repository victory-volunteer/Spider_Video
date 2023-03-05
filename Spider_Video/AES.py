from Crypto.Cipher import AES  # 或安装模块 pycryptodome

key_url = 'https://boba.52kuyun.com/20170906/Moh2l9zV/hls/key.key'
key = requests.get(key_url).text  # 访问秘钥拿到秘钥
decode_AES(key) # 解密(把已经下载好的ts文件, 再经过解密处理)

def decode_AES(key):
	# 若直接读已经下载好的ts文件会比较慢; 所以选择先从m3u8文件中读取ts文件名,继而通过ts文件名再读具体的ts文件
    with open("m3u8.txt", mode="r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                continue
            name = line.strip()
			# IV代表偏移量,默认放0就可以。但必须是字节,也就是多放几个0（即根据key有多少位,就放多少个0）
            # 因为METHOD=AES-128中没有具体写什么模式, 这里实测写MODE_CBC就可以
            aes = AES.new(key=key, IV=b"0000000000000000", mode=AES.MODE_CBC)
            # 从video/name中读ts文件, 通过aes去解密, 解密完后再存到video/temp_name文件中
            with open(f"video/{name}", mode="rb") as f1, open(f"video/temp_{name}", mode="wb") as f2:
                bs = f1.read()  # 从源文件读取内容
                f2.write(aes.decrypt(bs))  # 把解密好的内容写入文件