import os
import json
import imageio
import shutil
import glob
import argparse
import numpy as np
from natsort import natsorted
import pdb


GRID_VIEWS = [
    [-7.455825740412839, 6.485628262696672, 3.8863830222735407, 2.425673314125832, 0.3747011274137433],
    [-3.214120366039106, 9.34463170520407, 3.8863830222735407, 1.9020745385275335, 0.3747011274137433],
    [1.8888059647912339, 9.699748628735776, 3.8863830222735407, 1.3784757629292343, 0.3747011274137433],
    [6.48562826269667, 7.45582574041284, 3.8863830222735407, 0.8548769873309358, 0.3747011274137433],
    [9.34463170520407, 3.2141203660391056, 3.8863830222735407, 0.33127821173263683, 0.3747011274137433],
    [9.699748628735776, -1.8888059647912312, 3.8863830222735407, -0.192320563865662, 0.3747011274137433],
    [7.45582574041284, -6.48562826269667, 3.8863830222735407, -0.7159193394639608, 0.3747011274137433],
    [3.2141203660391073, -9.34463170520407, 3.8863830222735407, -1.2395181150622596, 0.3747011274137433],
    [-1.8888059647912283, -9.699748628735776, 3.8863830222735407, -1.7631168906605583, 0.3747011274137433],
    [-6.48562826269667, -7.45582574041284, 3.8863830222735407, -2.2867156662588575, 0.3747011274137433],
    [-9.34463170520407, -3.214120366039108, 3.8863830222735407, -2.810314441857156, 0.3747011274137433],
    [-9.699748628735776, 1.8888059647912319, 3.8863830222735407, -3.3339132174554553, 0.3747011274137433]
]



def ensure_dir(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname, exist_ok=True)
    return dirname


def read_json(fname):
    with open(fname, "r") as read_file:
        return json.load(read_file)


def write_json(content, fname):
    with open(fname, "w") as write_file:
        json.dump(content, write_file)


def get_args():
    parser = argparse.ArgumentParser()
    # path config
    parser.add_argument('--data_dir', default='../output', help="dir where data are saved")
    parser.add_argument("--load_mask", help="load gt masks", action="store_true", default=False)
    parser.add_argument("--load_grid", help="load tv image grid", action="store_true", default=False)
    return parser.parse_args()


def shape_masks(scn_mdirs, d_ord):
    mask_clr = []
    masks = []
    for fid, fmd in enumerate(scn_mdirs):
        mfiles = natsorted(glob.glob(os.path.join(fmd, '*.png')))
        m_sorted = [np.float32(np.all(imageio.imread(mfiles[mo])[...,:3]==255, axis=-1)) for mo in d_ord[fid]]
        mask_clr.append(m_sorted)

        # get occluded masks
        m_occ = [(i+1)+1000*(1.0-m) for i, m in enumerate(m_sorted)]
        m_occ = np.min(np.stack(m_occ, axis=-1), axis=-1, keepdims=False)
        m_occ *= np.float32(m_occ<1000)
        masks.append(m_occ)

        shutil.rmtree(fmd)
    return np.asarray(mask_clr), np.asarray(masks)


def grid_observations(grid_dirs, obj_pos):
    tv_grid = []
    tm_grid = []
    
    for gi, fgd in enumerate(grid_dirs):
        # handling grid observations
        gfiles = natsorted(glob.glob(os.path.join(fgd, '*.png')))
        gimgs = np.stack([imageio.imread(g) for g in gfiles], axis=0)
        tv_grid.append(gimgs)

        # handling grid masks
        mdirs = natsorted(glob.glob(os.path.join(fgd, 'mask*')))
        grid_vpt = np.asarray(GRID_VIEWS).astype('float32')[..., :3]   # [12, 3]
        d_orders = np.argsort(np.einsum('ij, kj->ki', obj_pos[gi], grid_vpt), axis=-1)[:, ::-1]  
        _, gmsks = shape_masks(mdirs, d_orders)  # 12 m, 12 dorders
        tm_grid.append(gmsks)
        
        shutil.rmtree(fgd)
    return np.stack(tv_grid, axis=0), np.stack(tm_grid, axis=0)


def main(args):
    save_dir = ensure_dir(os.path.join(args.data_dir, 'data'))
    J = read_json(os.path.join(args.data_dir, 'meta_info.json'))

    for i, scn in enumerate(J['scenes']):
        dpath = scn['path']
        dfiles = natsorted([p for p in os.listdir(dpath) if '.png' in p])
        imgs = []
        masks = []
        for df in dfiles:
            imgs.append(imageio.imread(os.path.join(dpath, df)))
        imgs = np.stack(imgs, axis=0)
        views = np.asarray(scn['views']).astype('float32')

        data_file = os.path.join(save_dir, str(i))
        if args.load_mask:
            mdirs = natsorted([os.path.join(dpath, p) for p in os.listdir(dpath) if 'mask' in p])
            obj_pos = np.asarray(scn['obj_pos']).astype('float32')
            depth_orders = np.argsort(np.einsum('bij, bj->bi', obj_pos, views[..., :3]), axis=-1)[:, ::-1]
            masks_clr, masks = shape_masks(mdirs, depth_orders)
            np.savez(data_file,
                     imgs = imgs,
                     views = views,
                     # masks_clr=masks_clr,
                     masks = masks)
        if args.load_grid:
            grid_dirs = natsorted([os.path.join(dpath, p) for p in os.listdir(dpath) if 'grid' in p])
            obj_pos = np.asarray(scn['obj_pos']).astype('float32')  # [T, K, 3]
            grid_imgs, grid_msks = grid_observations(grid_dirs, obj_pos)
            np.savez(data_file,
                     imgs = imgs,
                     views = views,
                     masks = masks,
                     grid_imgs = grid_imgs,
                     grid_msks = grid_msks)
        if (not args.load_grid) and (not args.load_mask):
            np.savez(data_file,
                     imgs = imgs,
                     views = views)
        print('  -- {} scene npz generated'.format(i))


if __name__ == "__main__":
    args = get_args()
    main(args)
