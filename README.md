# 115视频预览图生成器
## 功能
从115在线视频生成视频的预览图，需要115会员。

能够读取一个目录下的所有视频，并生成每个视频的缩略图，不支持目录递归。

## requirements
- python + requests
- ffmpeg

## 使用姿势
在浏览器中登录115，从中复制出cookie。

基本使用方式如下
``` shell
python 115_video_thumbnail.py -t "D:/临时目录" -o "D:/输入目录" "电视剧/请回答1988" "D:/ffmpeg/bin/ffmpeg.exe" "USERSESSIONID=XXX; UID=XXX; CID=XXX; SEID=XXX; acw_tc=XXX"
```

