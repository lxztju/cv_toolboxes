import argparse
import glob
import os
import os.path as osp
from multiprocessing import Pool
import librosa # 读取音频wav文件
import numpy as np

def extract_audio_wav(video_path):
    """Extract the audio wave from video streams using FFMPEG."""
    print('video_path', video_path)
    video_id = osp.basename(video_path).split('.')[0]
    try:
        if osp.exists(f'{dst_dir}/{video_id}.wav'):
            return
        # -loglevel quiet 不打印控制台参数
        cmd = f'ffmpeg -i {video_path} -ar 32000 -vn {dst_dir}/{video_id}.wav -loglevel quiet'
        os.popen(cmd)
        os.popen('stty echo')
    except BaseException:
        with open('extract_wav_err_file.txt', 'a+') as f:
            f.write(f'{video_path}\n')

# 取中间的音频
def pad_truncate_sequence(x, max_len):
    if len(x) < max_len:
        return np.concatenate((x, np.zeros(max_len - len(x))))
    else:
        start = int((len(x) - max_len) / 2)
        return x[start: max_len + start]

def wav2numpy(wav_path):
    audio_name = wav_path.split('/')[-1]
    print("audio_name:{}".format(audio_name))

    save_path = osp.join(dst_dir, audio_name.replace('.wav', '.npy'))  # 中间
    if os.path.exists(save_path):
        return
    try:
        # 采样频率设置为32k 单声道
        (audio, fs) = librosa.core.load(dst_dir, sr=32000, mono=True)
        # 取前30s
        audio = pad_truncate_sequence(audio, 32000 * 30)  # 截断或补长
        np.save(save_path, audio)
    except:
        pass


if __name__ == '__main__':
    src_dir = '../demo/videos'
    dst_dir = '../demo/wavs'
    os.popen(f'mkdir -p {dst_dir}')

    ext = 'mp4'
    num_worker = 3
    print('Reading videos from folder: ', src_dir)
    print('Extension of videos: ', ext)
    fullpath_list = glob.glob(src_dir + '/*' + '.' +ext)

    print('Total number of videos found: ', len(fullpath_list * 10))

    pool = Pool(num_worker)
    pool.map(extract_audio_wav, fullpath_list)
