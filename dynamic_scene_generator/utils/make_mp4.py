import os
import argparse
import imageio
from natsort import natsorted


def make_video(args):
    file_list = []
    for file in natsorted(os.listdir(args.source_dir)):
        if file.startswith(args.prefix) and 'png' in file:
            complete_path = os.path.join(args.source_dir, file)
            file_list.append(complete_path)

    if args.save_as[-4:] == '.mp4':
        v_fname = args.save_as
    else:
        v_fname = args.save_as + '.mp4'
    writer = imageio.get_writer(v_fname, fps=args.fps)
    for im in file_list:
        writer.append_data(imageio.imread(im))
    writer.close()

def config_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--prefix', type=str, default='', help="source image prefix")
    parser.add_argument('--fps', type=int, default=16, help="frame rate")
    parser.add_argument("-i", '--source_dir', required=True, help="dir where the source images are")
    parser.add_argument("-o", '--save_as', required=True, help="save the generated video as")

    args = parser.parse_args()
    return args


# ------------ main body ------------ #
if __name__ == '__main__':
    args = config_args()
    make_video(args)
