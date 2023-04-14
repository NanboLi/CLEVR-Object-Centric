#!/bin/bash

save_dir=output
scn_id=0

python3 utils/make_mp4.py -i ./${save_dir}/${scn_id} -o ./${save_dir}/${scn_id}.mp4
