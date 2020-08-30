import json
import os
import argparse
import requests


def list_dir(cid):
    url = "http://aps.115.com/natsort/files.php?aid=1&cid={}&o=file_name&asc=1&offset=0&show_dir=1&limit=1150&code=&scid" \
          "=&snap=0&natsort=1&record_open_time=1&source=&format=json&fc_mix=0&type=&star=&is_q=&is_share= ".format(cid)
    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    data = json.loads(response.text)
    return data['data']


def change_dir(curr_dir, path):
    if len(path) > 0:
        destination = path[0]
        for directory in curr_dir:
            if directory['n'] == destination:
                cid = directory['cid']
                new_dir = list_dir(cid)
                return change_dir(new_dir, path[1:])
        else:
            print("{} not found".format(destination))
            exit(-1)
    else:
        return curr_dir


def load_video_m3u8(video_pid):
    url = "http://115.com/api/video/m3u8/{}.m3u8".format(video_pid)
    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    data = response.text.split("\r\n")[1:-1]
    names = data[0::2]
    names = names[::-1]
    urls = data[1::2]
    urls = urls[::-1]
    return list(zip(names, urls))


def make_thumbnail_images(m3u8):
    url = m3u8[1]
    domain_name = url.split("/")[2]
    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    data = response.text.split("\n")

    def m3u8_filter(m3u8_str):
        if len(m3u8_str) > 0:
            return m3u8_str[0] != '#'
        return False

    data = list(filter(m3u8_filter, data))
    print("m3u8 length", len(data))
    step_len = int(len(data) / frames)
    data = data[::step_len]
    data = data[:frames]

    def m3u8_map(m3u8_str):
        if "http" in m3u8_str:
            return m3u8_str
        else:
            return "http://" + domain_name + m3u8_str

    data = list(map(m3u8_map, data))

    for index, d in enumerate(data):
        print(index, d)
        os.system("{} -v fatal -i \"{}\" -ss 0 -vframes 1 {}\output{:0>4d}.png".format(ffmpeg_path, d, tmp_dir, index))


def make_thumbnail(video):
    print(video['n'])
    # clean thumbnail images
    file_list = os.listdir(tmp_dir)
    for file in file_list:
        os.remove(tmp_dir + os.sep + file)
    # make thumbnail images
    m3u8 = load_video_m3u8(video['pc'])
    if len(m3u8) == 0:
        print("video error {}".format(video['n']))
        exit(-1)
    else:
        if quality > len(m3u8):
            des_m3u8 = m3u8[-1]
        else:
            des_m3u8 = m3u8[quality - 1]
        make_thumbnail_images(des_m3u8)
    # make thumbnail
    height = int(frames / 4)
    if frames % 4 != 0:
        height += 1

    file_list = "-i {}/output%04d.png".format(tmp_dir)
    os.system(
        "{} -v fatal {} -filter_complex tile=4x{}:margin=40:padding=100 {}/{}.png".format(ffmpeg_path, file_list,
                                                                                          height, output_dir,
                                                                                          video['n']))

    # clean thumbnail images
    file_list = os.listdir(tmp_dir)
    for file in file_list:
        os.remove(tmp_dir + os.sep + file)


def main():
    try:
        os.mkdir(output_dir)
    except:
        pass
    try:
        os.mkdir(tmp_dir)
    except:
        pass

    dir_list = list_dir(0)
    des_dir_list = change_dir(dir_list, path)
    for video in des_dir_list:
        make_thumbnail(video)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tmp', type=str, default='./tmp', help="临时中间文件目录")
    parser.add_argument('-o', '--out', type=str, default='./output', help="输出目录")
    parser.add_argument('-q', '--quality', type=int, default=1, help="视频质量，默认1，1为最高质量，越大视频质量越低")
    parser.add_argument('path', type=str, help="115 文件路径，/分隔，开头不需要/，示例 movie/titanic")
    parser.add_argument('-f', '--frames', type=int, default=20, help="需要采集的帧数")
    parser.add_argument('ffmpeg', type=str, help="ffmpeg的路径，示例 D:/ffmpeg/ffmpeg.exe")
    parser.add_argument('cookie', type=str, help="115的cookie")

    args = parser.parse_args()

    output_dir = args.out
    tmp_dir = args.tmp
    ffmpeg_path = args.ffmpeg
    frames = args.frames
    path = args.path.split("/")
    quality = args.quality

    payload = {}
    files = {}
    headers = {
        'Cookie': args.cookie
    }
    main()
