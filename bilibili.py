#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import time
from urllib.parse import urlparse
import json
import re
import argparse
import requests
import srt
import subtitle
import cookie
from exception import CustomException

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'cookie': '',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}


def parse_args():
    """Get command argvs"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, help="The url of Bilibili video")
    parser.add_argument("--dir", type=str,
                        help="The dir of videos to add subtitle")
    parser.add_argument("--cookies", type=str,
                        help="The cookies file path", default="./cookies.txt")
    parser.add_argument("--first", type=int,
                        help="The first index", default=0)
    return parser.parse_args()


def get_info_from_url(url: str):
    """Get infofmation from video url"""
    parse_str = urlparse(url)
    # params = parse_qs(parse_str.query)
    bvid = get_bvid_from_path(parse_str.path)
    result = {
        'bvid': bvid,
    }
    return result


def get_bvid_from_path(path: str):
    """Get BVID of video"""
    pattern = r'\/video\/([^\/]*)[\/]?'
    match = re.findall(pattern, path)
    if len(match) != 0:
        return match[0]
    return ""


def download_subtitle_title(url: str, index: int):
    infos = get_info_from_url(url)
    bvid = infos['bvid']

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise CustomException("can not get response from this url")

    text = resp.text
    aid = text[text.find('"aid"')+6:]
    aid = aid[:aid.find(',')]
    cid_back = requests.get(
        "http://api.bilibili.com/x/player/pagelist?bvid={}".format(bvid),
        headers=headers)
    if cid_back.status_code != 200:
        raise CustomException("request playlist fail")

    # add the dir
    sub_dir = mkdir_subtitle_dir(bvid)

    cid_json = json.loads(cid_back.content)
    items = cid_json['data']

    if index != 0:
        items = items[index:]

    # TODO 多进程
    for item in items:
        cid = item['cid']
        title = sub_dir + '/' + item['part'] + '.srt'
        links = get_subtitle_download_link(aid, cid)

        if len(links) == 0:
            continue

        subtitle_link = "https:" + links[0]['subtitle_url']
        print("url: " + subtitle_link)
        print(item['part'] + " downloading......")
        subtitle_resp = requests.get(subtitle_link, headers=headers)

        if subtitle_resp.status_code != 200:
            print(title + " download fail")
            continue

        content = srt.convert_json_to_srt(subtitle_resp.text)
        with open(title, 'w', encoding='UTF-8') as file:
            file.write(content)
            file.close()


def get_subtitle_download_link(aid, cid):
    """request the subtitle download link"""
    params = {
        'aid': aid,
        'cid': cid,
        'isGaiaAvoided': 'false',
        'web_location': '1315873',
        'w_rid': '364cdf378b75ef6a0cee77484ce29dbb',
        'wts': int(time.time())
    }

    wbi_resp = requests.get(
        'https://api.bilibili.com/x/player/wbi/v2',
        params=params, headers=headers)
    if wbi_resp.status_code != 200:
        return []

    wbi_resp_json = wbi_resp.json()
    return wbi_resp_json['data']['subtitle']['subtitles']


def mkdir_subtitle_dir(bvid: str):
    """make dir"""
    sub_dir = f'./{bvid}/subtitles'
    if not os.path.isdir(sub_dir):
        os.makedirs(sub_dir)
    return sub_dir


if __name__ == '__main__':
    args = parse_args()

    if args.url is None:
        raise CustomException("the url should not be empty")

    cookie_content = cookie.get_cookie_from_filename(args.cookies)
    headers['cookie'] = cookie_content

    download_subtitle_title(args.url, args.first)

    if args.dir is not None:
        print("dir not null")
        info = get_info_from_url(args.url)
        sd = mkdir_subtitle_dir(info['bvid'])
        subtitle.add_subtitles_to_videos(args.dir, sd)
