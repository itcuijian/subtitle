#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import argparse
import os
import re
from multiprocessing import Pool
import pysrt
from moviepy import VideoFileClip, CompositeVideoClip, TextClip, ColorClip
from exception import CustomException

output_dir = './output'
proc = 4


def parse_args():
    """Get command argvs"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--videos_dir", type=str,
                        help="The directory of videos to add subtitle")
    parser.add_argument("--subtitles_dir", type=str,
                        help="The directory of subtitles")
    parser.add_argument("--output", type=str,
                        help="The directory for output videos")
    parser.add_argument("--processes", type=int,
                        help="The number of process")
    return parser.parse_args()


def add_subtitle_to_video(video: str, subtitle: str, output: str):
    """add subtitles to video"""
    if video == '':
        raise CustomException("video should not be empty")
    if subtitle == '':
        raise CustomException("subtitle should not be empty")
    if output == '':
        raise CustomException("output should not be empty")

    video_clips = VideoFileClip(video)
    subtitle_clips = parse_srt_file(subtitle)
    color_clip = gen_color_clips_by_text_clips(subtitle_clips)
    final_clips = CompositeVideoClip(
        [video_clips, *subtitle_clips, *color_clip])
    final_clips.write_videofile(output)


def parse_srt_file(file: str):
    """parse srt file and transformer to test clip"""
    subtitles = pysrt.open(file, encoding="UTF-8")
    clips = []
    for subtitle in subtitles:
        start = subtitle.start.ordinal / 1000
        end = subtitle.end.ordinal / 1000
        duration = end - start

        clip = TextClip(
            font="./fonts/simsun.ttc",
            font_size=30,
            text=subtitle.text,
            color="white",
        )
        clip = clip.with_start(start).with_duration(
            duration).with_position(("center", 0.9), relative=True)
        clips.append(clip)
    return clips


def gen_color_clips_by_text_clips(text_clips):
    result = []
    if len(text_clips) == 0:
        return result
    for text_clip in text_clips:
        width, height = text_clip.size
        color_clip = gen_color_clip(
            width, height, text_clip.start, text_clip.duration)
        result.append(color_clip)
    return result


def gen_color_clip(width: float, height: float, start: float, duration: float):
    """generate color clip"""
    clip = ColorClip(size=(width + 2, height + 2),
                     color=(255, 255, 255), duration=duration)
    clip = clip.with_start(start)
    clip = clip.with_position(("center", 0.9), relative=True)
    clip = clip.with_opacity(.6)
    return clip


def get_filenames_from_dir(dirname: str):
    filenames = os.listdir(dirname)
    return filenames


def process(video_dir: str, subtitle_dir: str):
    videos = get_filenames_from_dir(video_dir)
    subtitles = get_filenames_from_dir(subtitle_dir)
    subtitles_list = [subtitles[i:i + proc]
                      for i in range(0, len(subtitles), proc)]
    # 多进程
    pool = Pool(proc)
    for item in subtitles_list:
        pool.apply_async(multiprocess_subtitle, args=(
            item, videos, video_dir, subtitle_dir, ))
    pool.close()
    pool.join()


def multiprocess_subtitle(subtitles, videos, video_dir, subtitle_dir):
    for subtitle in subtitles:
        subtitle_name = get_subtitle_filename(subtitle)
        if subtitle_name == '':
            continue
        for video in videos:
            if video.find(subtitle_name) != -1:
                add_subtitle_to_video(
                    video_dir + video, subtitle_dir + subtitle,
                    output_dir + '/' + video)


def get_subtitle_filename(subtitle_filename: str):
    pattern = r'(.*)\.srt'
    match = re.findall(pattern, subtitle_filename)
    if len(match) != 0:
        return match[0]
    return ""


def add_subtitles_to_videos(videos_dir: str, subtitles_dir: str):
    """add subtitles to the videos"""
    if videos_dir == '':
        raise CustomException("the directory of videos should not be empty")

    if subtitles_dir == '':
        raise CustomException("the directory of subtitles should not be empty")

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    process(videos_dir, subtitles_dir)


if __name__ == '__main__':
    args = parse_args()

    if args.videos_dir == '':
        raise CustomException("the directory of videos should not be empty")

    if args.subtitles_dir == '':
        raise CustomException("the directory of subtitles should not be empty")

    if args.output != '':
        output_dir = args.output

    if args.processes is not None and args.processes != 0:
        proc = args.processes

    add_subtitles_to_videos(args.videos_dir, args.subtitles_dir)
