#!/bin/bash


# ----- generate the fast-cam-slow-obj partition -----
vel_cam_level=fast
vel_obj_level=slow
for level in 4 5
do 
  save_dir=./output/test_${level}/fc_so
  sleep 1
  ${BLENDER}/blender --background --python dm_data_generator.py -- --episode 8 --num_frames 40 --use_gpu 1 \
  -o ${save_dir} --image_size 64 --sim_fps 10 --min_num_objs 2 --max_num_objs 4 --v_cam_level ${vel_cam_level} \
  --v_obj_level ${vel_obj_level} --level $level --v_azi 6.0 --v_ele 1. --force 8500.
  sleep 1
  python utils/make_npy.py --data_dir ${save_dir}
  sleep 1
done
sleep 1


# ----- generate slow-cam-fast-obj partition -----
vel_cam_level=slow
vel_obj_level=fast
for level in 4 5
do 
  save_dir=./output/test_${level}/sc_fo
  sleep 1
  ${BLENDER}/blender --background --python dm_data_generator.py -- --episode 8 --num_frames 40 --use_gpu 1 \
  -o ${save_dir} --image_size 64 --sim_fps 10 --min_num_objs 2 --max_num_objs 4 --v_cam_level ${vel_cam_level} \
  --v_obj_level ${vel_obj_level} --level $level --v_azi 3.6 --v_ele 0.5 --force 9000.
  python utils/make_npy.py --data_dir ${save_dir}
  sleep 1
done
