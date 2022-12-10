import argparse
import glob
import os
import os.path as osp
import sys
from multiprocessing import Pool


def encode_video(frame_dir_path):
    """Encode frames to video using ffmpeg.
    """
    vcodec = 'mpeg4'
    fps = 30
    start_idx = 0
    filename_tmpl = '%06d'
    in_format = 'png'


    img_name_tmpl = filename_tmpl + '.' + in_format
    img_path = osp.join(frame_dir_path, img_name_tmpl)
    print(img_path)
    video_id = osp.basename(frame_dir_path)
    out_vid_name = video_id + '.' + ext
    out_vid_path = osp.join(dst_dir, out_vid_name)

    cmd = osp.join(
        f"ffmpeg -start_number {start_idx} -r {fps} -i '{img_path}' "
        f"-vcodec {vcodec} '{out_vid_path}' -loglevel quiet")
    os.system(cmd)

    sys.stdout.flush()
    return True




if __name__ == '__main__':
    src_dir = '../demo/frames'
    dst_dir = '../demo/frames2video'
    os.makedirs(dst_dir, exist_ok=True)

    ext = 'mp4'
    num_worker = 2
    print('Reading videos from folder: ', src_dir)
    print('Extension of videos: ', ext)
    fullpath_list = glob.glob(src_dir + '/*')
    print(fullpath_list)
    print('Total number of videos found: ', len(fullpath_list))

    pool = Pool(num_worker)

    pool.map(encode_video, fullpath_list)
