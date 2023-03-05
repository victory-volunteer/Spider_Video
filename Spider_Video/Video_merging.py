import os

# 合并ts视频为mp4(前提:有m3u8文件,且其中的ts视频已经下载成功)
# 注意:若下载好的ts视频名是以m3u8中的内容命名的,则可以直接读取m3u8文件来拼接字符串(避免了重新读取video文件夹带来的速度问题)

# 合并视频
with open("file.txt", mode="a", encoding="utf-8") as f2:
    for i in range(1, 16):
        f2.write("file 'E:\\爬虫\\video\\" + str(i) + ".ts'\n")
os.system("ffmpeg.exe -f concat -safe 0 -i file.txt -c copy E:\\爬虫\\video\\video.mp4")