#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import argparse
import subtitle
from exception import CustomException


def parse_args():
    """Get command argvs"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", type=str,
                        help="The video filepath")
    parser.add_argument("--subtitle", type=str,
                        help="The subtitle filepath")
    return parser.parse_args()


def gen_output_filename_from_path(filepath: str):
    filename = os.path.basename(filepath)
    filename = os.path.dirname(filepath) + "/with_sub_" + filename
    return filename


if __name__ == '__main__':
    args = parse_args()
    if args.video is None:
        raise CustomException("video filepath should not be empty")
    if args.subtitle is None:
        raise CustomException("subtitle filepath should not be empty")
    output = gen_output_filename_from_path(args.video)
    subtitle.add_subtitle_to_video(
        args.video, args.subtitle, output)
