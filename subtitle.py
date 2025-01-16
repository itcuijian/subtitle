#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import argparse
import os
import re
import pysrt
from moviepy import VideoFileClip, CompositeVideoClip, TextClip
from exception import CustomException

output_dir = './output'


def parse_args():
    """Get command argvs"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--videos_dir", type=str,
                        help="The dir of videos to add subtitle")
    parser.add_argument("--subtitles_dir", type=str,
                        help="The dir of subtitles")
    parser.add_argument("--output", type=str,
                        help="The dir for output videos")
    return parser.parse_args()


def add_subtitle_to_video(video: str, subtitle: str, output: str):
    """add subtitles to video"""
    if video == '':
        raise CustomException("video should not be empty")
    if subtitle == '':
        raise CustomException("video should not be empty")
    if output == '':
        raise CustomException("video should not be empty")

    video_clips = VideoFileClip(video)
    subtitle_clips = parse_srt_file(subtitle)
    final_clips = CompositeVideoClip([video_clips, *subtitle_clips])
    final_clips.write_videofile(output)


def parse_srt_file(file: str):
    subtitles = pysrt.open(file, encoding="UTF-8")
    clips = []
    for subtitle in subtitles:
        start = subtitle.start.ordinal / 1000
        end = subtitle.end.ordinal / 1000
        duration = end - start

        clip = TextClip(
            font="./fonts/simsun.ttc",
            font_size=35,
            text=subtitle.text,
            color="white"
        ).with_start(start).with_duration(duration).with_position(("center", 660))
        clips.append(clip)
    return clips


def get_filenames_from_dir(dirname: str):
    filenames = os.listdir(dirname)
    return filenames


def process(video_dir: str, subtitle_dir: str):
    videos = get_filenames_from_dir(video_dir)
    subtitles = get_filenames_from_dir(subtitle_dir)
    # TODO 多进程
    for subtitle in subtitles:
        subtitle_name = get_subtitle_filename(subtitle)
        if subtitle_name == '':
            continue
        for video in videos:
            if video.find(subtitle_name) != -1:
                add_subtitle_to_video(
                    video_dir + video, subtitle_dir + subtitle,
                    output_dir + video)


def get_subtitle_filename(subtitle_filename: str):
    pattern = r'(.*)\.srt'
    match = re.findall(pattern, subtitle_filename)
    if len(match) != 0:
        return match[0]
    return ""


def add_subtitles_to_videos(videos_dir: str, subtitles_dir: str):
    """add subtitles to the videos"""
    if videos_dir == '':
        raise CustomException("the dir of videos should not be empty")

    if subtitles_dir == '':
        raise CustomException("the dir of subtitles should not be empty")

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    process(videos_dir, subtitles_dir)


if __name__ == '__main__':
    args = parse_args()

    if args.videos_dir == '':
        raise CustomException("the dir of videos should not be empty")

    if args.subtitles_dir == '':
        raise CustomException("the dir of subtitles should not be empty")

    if args.output != '':
        output_dir = args.output

    add_subtitles_to_videos(args.videos_dir, args.subtitles_dir)
