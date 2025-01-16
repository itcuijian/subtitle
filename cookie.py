#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
from exception import CustomException


def get_cookie_from_filename(filepath: str):
    if not os.path.exists(filepath):
        raise CustomException('file is not exists')

    content = ''
    with open(filepath, 'r', encoding='UTF-8') as file:
        content = file.read().rstrip('\n')

    return content
