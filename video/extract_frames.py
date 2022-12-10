import os
import os.path as osp
import cv2
import time
import numpy as np
import glob
from multiprocessing import Pool
from decord import VideoReader
import tqdm

import math
def convert_time(time):
    hour, minute, second = '00','00','00'
    if time > 3600:
        hour = str(int(time / 3600))
        time  = time - 3600 * int(time / 3600)
        if len(hour)< 2:
            hour = '0' + hour
    if time > 59.9999:
        minute = str(int(time / 60))
        time  = time - 60 * int(time / 60)
        if len(minute)< 2:
            minute = '0' + minute
    decimal_data, integer_data = math.modf(time)
    if decimal_data > 0.99:
        time = time - decimal_data + 0.99
    second = str(round(time))
    if time < 10:
        second = '0' + second
    return hour + ":" + minute + ':' + second



def _get_indices(num_frames, num_segments):
    tick = (num_frames) / float(num_segments)
    offsets = np.array([int(tick / 2.0 + tick * x) for x in range(num_segments)])
    return offsets + 1


def get_frames_indices(video_path):
    if not os.path.exists(video_path):
        print("video not exists")
        return None

    capture = cv2.VideoCapture(video_path)
    video_frames_num = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(capture.get(cv2.CAP_PROP_FPS))

    if not capture.isOpened():
        print("not opened")
        return None

    if video_frames_num < 2:
        capture.release()
        return None

    if extract_config['fix_interval'] is not None:
        num_segment = video_frames_num // (extract_config['fix_interval'] * fps)

    elif extract_config['fix_frame_num'] and extract_config['fix_frame_num'] < video_frames_num:
        num_segment = extract_config['fix_frame_num']
    elif extract_config['fix_frame_num']:
        num_segment = video_frames_num // fps
    else:
        print('please set correct fix_interval and fix_frame_num in extract_config')

    indices = _get_indices(video_frames_num, num_segment)
    return indices, capture


def extract_frames_opencv(video_path):
    print('extracting video_path: ', video_path)
    indices, capture = get_frames_indices(video_path)
    if indices is None:
        return
    # capture = cv2.VideoCapture(video_path)
    video_name = osp.basename(video_path).split('.')[0]
    target_dir = osp.join(dst_dir, video_name)
    os.makedirs(target_dir, exist_ok=True)

    if not capture.isOpened():
        print("not opened")
        return None

    for i, seg_ind in enumerate(indices):
        idx = int(seg_ind)
        capture.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = capture.read()
        if (ret == False or frame is None):
            continue
        cv2.imwrite(osp.join(target_dir, '{:06}.png'.format(i)), frame)

    capture.release()
    return None


def extract_frames_decord(video_path):
    print('extracting video_path: ', video_path)

    indices, cap = get_frames_indices(video_path)
    if indices is None:
        return
    # cap = cv2.VideoCapture(video_path)
    video_name = osp.basename(video_path).split('.')[0]
    target_dir = osp.join(dst_dir, video_name)
    os.makedirs(target_dir, exist_ok=True)

    vr_result = VideoReader(video_path, num_threads=3).get_batch(indices).asnumpy()

    for i in range(0, len(vr_result)):
        img = cv2.cvtColor(vr_result[i], cv2.COLOR_RGB2BGR)
        cv2.imwrite(osp.join(target_dir, '{:06}.png'.format(i)), img)

    return None


def extract_one_frame(video_path, time, target_path):
    cmd = "ffmpeg -ss "+time+" -i "+video_path+" -vframes 1 "+target_path+" -loglevel quiet"
    # print(cmd)
    os.system(cmd)
    return None


def extract_frames_ffmpeg(video_path):
    print('extracting video_path: ', video_path)

    indices, cap = get_frames_indices(video_path)
    if indices is None:
        return
    video_name = osp.basename(video_path).split('.')[0]
    target_dir = osp.join(dst_dir, video_name)
    os.makedirs(target_dir, exist_ok=True)

    video_duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    time_offset = cap.get(cv2.CAP_PROP_FRAME_COUNT) / video_duration
    times = []
    for idx in indices:
        times.append(convert_time(idx//time_offset))
    for i in range(len(indices)):

        target_path = osp.join(target_dir, '{:06}.png'.format(i))
        extract_one_frame(video_path, times[i], target_path)
    return None


extract_config = {
    'module': 'opencv', # choice: [opencv, decord, ffmpeg]
    'fix_frame_num':  10, # 每个视频提取N帧, fix_frame_num 和fix_interval必须一个为None，另一个设定为一个指定的值
    'fix_interval': None # 每个1s提取一帧

}

if __name__ == "__main__":
    src_dir = '../demo/videos'
    dst_dir = '../demo/frames_' + extract_config['module']
    os.makedirs(dst_dir, exist_ok=True)

    ext = 'mp4'
    num_worker = 5
    print('Reading videos from folder: ', src_dir)
    print('Extension of videos: ', ext)
    fullpath_list = glob.glob(src_dir + '/*' + '.' +ext)

    print('Total number of videos found: ', len(fullpath_list))

    pool = Pool(num_worker)
    if extract_config['module'] == 'opencv':
        pool.map(extract_frames_opencv, fullpath_list)
    elif extract_config['module'] == 'ffmpeg':
        pool.map(extract_frames_ffmpeg, fullpath_list)
    else:
        pool.map(extract_frames_decord, fullpath_list)




