import os
import numpy as np

'''
filepath = '/data/bf312/3D-Billiard/training/'
filename= os.listdir(filepath)

global_count = 0
for name in filename:
    new_name = str(global_count) # + '_test'
    os.rename(filepath + name, filepath + new_name)
    global_count += 1

for name in filename:
    data_name = os.listdir(filepath + name + '/')
    # print(len(data_name))
    if len(data_name) != 100:
        print(name)
'''

# 1_hinton, hinton

'''
filepath = '/data/bf312/3D-Billiard/validation/generated_test_images_bengio/'
for i in range(0, 100):
    new_name = i + 100
    os.rename(filepath + str(i), filepath + str(new_name))
'''


filepath = '/data/bf312/3D-Billiard/testing/'
hinton_1_data_bbox = np.load(filepath + 'generated_test_images_1_hinton/bbox.npy')
hinton_1_data_pres = np.load(filepath + 'generated_test_images_1_hinton/pres.npy')
print(hinton_1_data_bbox.shape, hinton_1_data_pres.shape)
hinton_data_bbox = np.load(filepath + 'generated_test_images_hinton/bbox.npy')
hinton_data_pres = np.load(filepath + 'generated_test_images_hinton/pres.npy')
print(hinton_data_bbox.shape, hinton_data_pres.shape)


bbox = np.concatenate((hinton_1_data_bbox, hinton_data_bbox), axis=0)
print(bbox.shape)
pres = np.concatenate((hinton_1_data_pres, hinton_data_pres), axis=0)
print(pres.shape)

np.save('/data/bf312/3D-Billiard/testing/bbox.npy', bbox)
np.save('/data/bf312/3D-Billiard/testing/pres.npy', pres)
