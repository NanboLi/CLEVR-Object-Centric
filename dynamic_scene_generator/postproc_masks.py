# -*- coding: utf-8 -*-
"""
Multi-view CLEVR data generator for static scenes.

@author: Nanbo Li


Run this file everytime after running 'render_images.py' as ordinary python:
    python postproc_masks.py --num_views xx
"""


import os, argparse
import numpy as np
import shutil, json, imageio, glob
from natsort import natsorted

import pdb

OP_DIR = os.path.abspath('./output/')

# ------------ helper utilities ------------ #
def read_json(fname):
    with open(fname, "r") as read_file:
        return json.load(read_file)


def write_json(content, fname):
    with open(fname, "w") as write_file:
        json.dump(content, write_file, indent=2)


def clean_masks(mask_dir, json_file):
    J = read_json(json_file)
    OBJS = J['objects']
    mfiles = natsorted(glob.glob(os.path.join(mask_dir, '*.png')))
    M = [np.float32(np.all(imageio.imread(mf)[...,:3]==255, axis=-1)) for mf in mfiles]
    z_measure = list(np.asarray([obj['pixel_coords'][-1] for obj in OBJS]))
    depth_orders = sorted(range(len(z_measure)), key=lambda k: z_measure[k])

    # sort original object masks with depth_orders
    M_sorted = [M[o] for o in depth_orders]
    # get occluded masks
    M_occ = []
    for i, m in enumerate(M_sorted):
        M_occ.append((i+1)+1000*(1.0-m))
    M_occ = np.min(np.stack(M_occ, axis=-1), axis=-1, keepdims=False)
    M_occ *= np.float32(M_occ<1000)

    # [M_occ, mask_bg, mask_obj1, mask_obj2, mask_obj3, ...]
    masks = np.stack([M_occ]+M, axis=-1)
    np.save(mask_dir + '.npy', masks)

    # add depth orders to the data description
    J['depth_orders'] = depth_orders
    write_json(J, json_file)

    shutil.rmtree(mask_dir)
    return masks


def clean_masks_mv(mask_dir, json_file, vid=0):
    J = read_json(json_file)
    OBJS = J['objects']
    if vid==0:
        J['depth_orders']=[]
    mfiles = natsorted(glob.glob(os.path.join(mask_dir, '*.png')))
    M = [np.float32(np.all(imageio.imread(mf)[...,:3]==255, axis=-1)) for mf in mfiles]
    z_measure = list(np.asarray([obj['pixel_coords'][vid][-1] for obj in OBJS]))
    depth_orders = sorted(range(len(z_measure)), key=lambda k: z_measure[k])

    # sort original object masks with depth_orders
    M_sorted = [M[o] for o in depth_orders]
    # get occluded masks
    M_occ = []
    for i, m in enumerate(M_sorted):
        M_occ.append((i+1)+1000*(1.0-m))
    M_occ = np.min(np.stack(M_occ, axis=-1), axis=-1, keepdims=False)
    M_occ *= np.float32(M_occ<1000)

    # [M_occ, mask_bg, mask_obj1, mask_obj2, mask_obj3, ...]
    masks = np.stack([M_occ]+M, axis=-1)
    np.save(mask_dir + '.npy', masks)

    # add depth orders to the data description
    J['depth_orders'].append(depth_orders)
    write_json(J, json_file)

    shutil.rmtree(mask_dir)
    return masks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_views', default=10, type=int, metavar='N')
    args = parser.parse_args()

    json_FILES_ori = natsorted(glob.glob(os.path.join(OP_DIR, 'scenes/CLEVR_new_*')))
    mask_DIRs = natsorted(glob.glob(os.path.join(OP_DIR, 'masks/CLEVR_new_*')))

    if args.num_views>1:
        json_FILES = []
        for js in json_FILES_ori:
            json_FILES += args.num_views * [js]
    else:
        json_FILES = json_FILES_ori

    print(" ==== START POST PROCESSING OBJECT MASKS ==== ")
    for i, (md, jf) in enumerate(zip(mask_DIRs, json_FILES)):
        if args.num_views>1:
            clean_masks_mv(md, jf, i % args.num_views)
        else:
            clean_masks(md, jf)
        print("  {:6d} scenes cleaned".format(i))
    print(" ==== CLEANING FINISHED ==== \n")


# ------------ main body ------------ #
if __name__ == '__main__':
    main()
