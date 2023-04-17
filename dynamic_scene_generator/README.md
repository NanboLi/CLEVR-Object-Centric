# CLROC-DynamicScenes  
Data generator used to generate **Moving-Observer-Dynamic-Scene** CLEVR images as described in:  
[Object-Centric Representation Learning with Generative Spatial-Temporal Factorization](https://arxiv.org/abs/2111.05393)  
[**Li Nanbo**](http://homepages.inf.ed.ac.uk/s1601283/), **Muhammad Ahmed Raza**, **Hu Wenbin**, **Sun Zhaole**, [**Robert B. Fisher**](https://homepages.inf.ed.ac.uk/rbf/)  
NeurIPS 2021  


## Usage  

**Pre:** Open a terminal and navigate it to the root of the repo (i.e. `<YOUR-PATH>/CLEVR-Object-Centric`). Then you will need to add the generator path to Blender python path, this is done by executing:  

``````
echo $PWD/dynamic_scene_generator >> $BLENDER/2.79/python/lib/python3.5/site-packages/clevr.pth && cd ./dynamic_scene_generator
``````
Do leave the terminal OPEN!
  

**Data Generation:**

1. Specify scene properties by editing the corresponding lines in `dm_data_generator.py` file (e.g. the code block starting from *line 337*). 

   * You can add new "shapes" and "materials" but need to make sure that the corresponding objects are placed in the `./data/shapes` and `./data/materials` folders. 

      (*Note: make sure to use objects names that are shown in Blender for the dictionary "values", e.g. use "SmoothCube_v2" for entry "cube". One can check these names by opening the shape blender files.*)

   * *You can add your own meshes into the `./data/shapes` as well, just make sure to set appropriate initial scales and poses for the shapes in Blender.   

     

2. Configure the `./run_gen.sh` file. Here are some important high-level control flags:

   * `episode`: number of dynamic scenes to render
   * `level`: specify how significance the velocity gap (between that of the camera and the scene objects) is. The higher the more significant. 
   * `render_mask`: activate this flag to render masks. If activated, do append `--load_mask` to the `python utils/make_npy.py ...` command line. 
   * `render_grid`: activate this flag to render the for the time-view (T-V) counterfactuals grouth truths. This is highly recommended for evaluations. If activated, do append `--load_grid` to the `python utils/make_npy.py ...` command line.


3. In the opened terminal, run the below cmd to generate data:

   ``````
   . ./run_gen.sh
   ``````
   The data will be saved to `./dynamic_scene_generator/<Your-Dataset>/` (specified in the `run_gen.sh` file). 
<!--    ``````
     dynamic_scene_generator/<Your-Dataset>/
         ├── <Your-Partition>-<Level>
         ├── <Your-Partition>-<Level>
         ├── ...
         └── scenes (meta info for disentanglement evaluations, scene#.json where one ".json" corresponds to multiple ".png" and ".npy"---one scene charges multiple observations)
   `````` -->
  

## Cite

Cite the paper if you found this repo useful.

```latex
@inproceedings{nanbo2021dymon,
  title={Object-Centric Representation Learning with Generative Spatial-Temporal Factorization},
  author={Nanbo, Li and Raza, Muhammad Ahmed and Wenbin, Hu and Sun, Zhaole and Fisher, Robert},
  booktitle={Advances in Neural Information Processing Systems},
  year={2021}
}
   
@inproceedings{lin2020improving,
  title={Improving generative imagination in object-centric world models},
  author={Lin, Zhixuan and Wu, Yi-Fu and Peri, Skand and Fu, Bofeng and Jiang, Jindong and Ahn, Sungjin},
  booktitle={International Conference on Machine Learning},
  year={2020}
}
```
