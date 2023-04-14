import os
import moviepy.editor as mpy
from PIL import Image
import numpy as np
import random


MID_FILE_NAME = 'generated_images_2'
# Load images
imgs_file_len = 10 # F
imgs_file_index = random.sample([i for i in range(0, imgs_file_len)], 10)
imgs_seq_len = 100 # S

imgs_path = '/data/bf312/3D-Billiard/' + MID_FILE_NAME + '/'
imgs_bbox_path = '/data/bf312/3D-Billiard/' + MID_FILE_NAME + '_bbox/'


# Make GIFs
def make_gif(videos, output_name, path='./gif', num=1, fps=5):
    '''
    Show some gifs.
    
    :param videos: (N, T, H, W, 3)
    :param path: directory
    '''
    os.makedirs(path, exist_ok=True)
    assert num <= videos.shape[0]
    for i in range(num):
        clip = mpy.ImageSequenceClip(list(videos[i]), fps=fps)
        # clip.write_gif(os.path.join(path, f'{i}.gif'), fps=fps)
        clip.write_gif(os.path.join(path, output_name + '.gif'), fps=fps)


# Save File
save_path = '/data/bf312/3D-Billiard/' + MID_FILE_NAME + '_gif/'
folder = os.path.exists(save_path)
if not folder:
    os.makedirs(save_path)

for file_index in imgs_file_index:
    # Load Images
    imgs = []
    for img_index in range(imgs_seq_len):
        img = Image.open(imgs_bbox_path + str(file_index) + '/test_' + str(img_index + 1) + '.png')
        img_array = np.array(img)
        imgs.append(img_array)
    imgs = np.array(imgs)

    imgs_gif = []
    for i in imgs:
        temp = i[:, :, :3]
        imgs_gif.append(temp)

    imgs_gif = np.array([imgs_gif])
    make_gif(imgs_gif, save_path + str(file_index))


'''
# RGBA To RGB
bg = np.zeros((128, 128, 3))
def RGBA_2_RGB(bg, rgba):
    alpha = rgba[:, :, 3]
    r_ch = (1 - alpha) * bg[:, :, 0] + alpha * rgba[:, :, 0]
    g_ch = (1 - alpha) * bg[:, :, 1] + alpha * rgba[:, :, 1]
    b_ch = (1 - alpha) * bg[:, :, 2] + alpha * rgba[:, :, 2]
    return np.array([r_ch, g_ch, b_ch])
'''

