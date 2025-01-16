#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import json
import math


def convert_json_to_srt(src: str):
    """ convert json to srt"""
    file_content = ''
    i = 1
    datas = json.loads(src)
    for data in datas['body']:
        start = data['from']
        stop = data['to']
        content = data['content']

        file_content += '{}\n'.format(i)

        hour = math.floor(start) // 3600
        minute = (math.floor(start) - hour * 3600) // 60
        sec = math.floor(start) - hour * 3600 - minute * 60
        minisec = int(math.modf(start)[0] * 100)

        file_content += str(hour).zfill(2) + ':' + str(minute).zfill(2) + \
            ':' + str(sec).zfill(2) + ',' + str(minisec).zfill(2)
        file_content += ' --> '

        hour = math.floor(stop) // 3600
        minute = (math.floor(stop) - hour * 3600) // 60
        sec = math.floor(stop) - hour * 3600 - minute * 60
        minisec = abs(int(math.modf(stop)[0] * 100 - 1))

        file_content += str(hour).zfill(2) + ':' + str(minute).zfill(2) + \
            ':' + str(sec).zfill(2) + ',' + str(minisec).zfill(2)
        file_content += '\n' + content + '\n\n'

        i += 1

    return file_content
