import os
import numpy as np
import random
from PIL import Image

# Color Box
COLORS = [[50, 100, 200], [200, 50, 100], [200, 100, 50], [200, 200, 50], [100, 200, 200]]
MID_FILE_NAME = 'generated_images_2'

# Load bbox and pres
bbox_path = '/data/bf312/3D-Billiard/' + MID_FILE_NAME + '/'
BBOX = np.load(bbox_path + 'bbox.npy') # (F, S, N, 4)
PRES = np.load(bbox_path + 'pres.npy') # (F, S, N)
print(BBOX.shape, PRES.shape)
print(BBOX[0, 40:55])

# Load images
imgs_file_len = 10 # F
imgs_file_index = random.sample([i for i in range(0, imgs_file_len)], 10)
imgs_seq_len = 100 # S
imgs_obj_len = 5 # N

imgs_path = '/data/bf312/3D-Billiard/' + MID_FILE_NAME + '/'
# for file_index in range(imgs_file_len):
for file_index in imgs_file_index:
    for seq_index in range(imgs_seq_len):
        img = Image.open(imgs_path + str(file_index) + '/test_' + str(seq_index + 1) + '.png')
        img_array = np.array(img) # (128, 128, 4)

        for i in range(imgs_obj_len):
            x = int(BBOX[file_index, seq_index, i, 0])
            y = int(BBOX[file_index, seq_index, i, 1])
            h = int(BBOX[file_index, seq_index, i, 2])
            w = int(BBOX[file_index, seq_index, i, 3])

            '''
            if x < 0:
                x = 0
                w = w - abs(x)
            if y < 0:
                y = 0
                h = h - abs(y)
            if x > 127 or y > 127:
                x = 0
                y = 0
                h = 0
                w = 0
            if x + w > 127:
                w = 127 - x
            if y + h > 127:
                h = 127 - y
            for j in range(3):
                print(y, y + h, x, j)
                img_array[y, x: (x + w), j] = COLORS[i][j]
                img_array[y: (y + h), x, j] = COLORS[i][j]
                img_array[(y + h), x: (x + w), j] = COLORS[i][j]
                img_array[y: (y + h), (x + w), j] = COLORS[i][j]
            '''
            if x < 0 and x + h > 0:
                h = h + x
                x = 0
            elif x + h < 0:
                x = 0
                y = 0
                h = 0
                w = 0
            if y < 0 and y + w > 0:
                w = w + y
                y = 0
            elif y + w < 0:
                x = 0
                y = 0
                h = 0
                w = 0
            if x > 127:
                x = 0
                y = 0
                h = 0
                w = 0
            elif x + h > 127:
                h = 127 - x
            if y > 127:
                x = 0
                y = 0
                h = 0
                w = 0
            elif y + w > 127:
                w = 127 - y
            for j in range(3):
                if file_index == 0 and seq_index == 50:
                    print(x, y, h, w)
                img_array[y, x: (x + h), j] = COLORS[i][j]
                img_array[y: (y + w), x, j] = COLORS[i][j]
                img_array[(y + w), x: (x + h), j] = COLORS[i][j]
                img_array[y: (y + w), (x + h), j] = COLORS[i][j]


        img = Image.fromarray(img_array)
        save_path = '/data/bf312/3D-Billiard/' + MID_FILE_NAME + '_bbox/' + str(file_index) + '/'
        folder = os.path.exists(save_path)
        if not folder:
            os.makedirs(save_path)
        
        img.save(save_path + 'test_' + str(seq_index + 1) + '.png')

