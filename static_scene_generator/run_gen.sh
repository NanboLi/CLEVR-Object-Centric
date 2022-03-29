#!/bin/bash

start_idx=0
num_scenes_per_iter=2   # Set this to 200 to avoid overflow issues and use the while loop to generate more data
num_views=10
counter=0
repeat=3    # number of generated scenes = (repeat-counter) * num_scenes_per_iter
while [ $counter -lt $repeat ]
do
  ${BLENDER}/blender --background --python render_images_mv.py -- --use_gpu 1 \
  --start_idx $(($start_idx+$counter * $num_scenes_per_iter)) --num_scenes $num_scenes_per_iter --num_views $num_views \
  --width 64 --height 64 --min_pixels_per_object 48 --min_objects 3 --max_objects 6 \
  --properties_json data/properties_customised.json
  ((counter++))
  sleep 2
done

sleep 2
python postproc_masks.py --num_views $num_views
