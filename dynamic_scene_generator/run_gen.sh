#!/bin/bash

dataset=CLORC    # name your own dataset, e.g. CLORC
partition=train    # train/test/validation

# ----- generate the fast-cam-slow-obj partition -----
vel_cam_level=fast
vel_obj_level=slow
for level in 3 4
do 
  save_dir=./${dataset}/${partition}_${level}/fc_so
  sleep 1
  ${BLENDER}/blender --background --python dm_data_generator.py -- --episode 2 --num_frames 20 --use_gpu 1 \
  -o ${save_dir} --image_size 64 --sim_fps 10 --min_num_objs 2 --max_num_objs 4 --v_cam_level ${vel_cam_level} \
  --v_obj_level ${vel_obj_level} --level $level --v_azi 6.0 --v_ele 1. --force 8500. --render_mask #--render_grid
  sleep 1
  python utils/make_npy.py --data_dir ${save_dir} --load_mask #--load_grid
  sleep 1
done
sleep 1


# ----- generate slow-cam-fast-obj partition -----
vel_cam_level=slow
vel_obj_level=fast
for level in 3 4
do 
  save_dir=./${dataset}/${partition}_${level}/sc_fo
  sleep 1
  ${BLENDER}/blender --background --python dm_data_generator.py -- --episode 2 --num_frames 20 --use_gpu 1 \
  -o ${save_dir} --image_size 64 --sim_fps 10 --min_num_objs 2 --max_num_objs 4 --v_cam_level ${vel_cam_level} \
  --v_obj_level ${vel_obj_level} --level $level --v_azi 3.6 --v_ele 0.5 --force 9000. --render_mask #--render_grid
  python utils/make_npy.py --data_dir ${save_dir} --load_mask #--load_grid
  sleep 1
done
