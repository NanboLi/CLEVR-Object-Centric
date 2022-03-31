# CLROC-MultiView   
Data generator used to generate **Multi-View-Static-Scene** CLEVR images as described in:  
[**Learning Object-Centric Representations of Multi-object Scenes from Multiple Views**](https://papers.nips.cc/paper/2020/hash/3d9dabe52805a1ea21864b09f3397593-Abstract.html)  
[**Li Nanbo**](http://homepages.inf.ed.ac.uk/s1601283/), [**Cian Eastwood**](http://homepages.inf.ed.ac.uk/s1668298/), [**Robert B. Fisher**](https://homepages.inf.ed.ac.uk/rbf/)  
NeurIPS 2020 (**<font style="color:red">Spotlight</font>**)      

  

## Usage  

**Pre: ** Open a terminal and navigate it to the root of the repo (i.e. `<YOUR-PATH>/CLEVR-Object-Centric`). Then you will need to add the generator path to Blender python path, this is done by executing:  

``````
echo $PWD/static_scene_generator >> $BLENDER/2.79/python/lib/python3.5/site-packages/clevr.pth && cd ./static_scene_generator
``````

Do leave the terminal OPEN!



**Data Generation:**

1. Specify scene properties by editing `./properties_customised.json`. 

   * You can add new "shapes" and "materials" but need to make sure that the corresponding objects are placed in the `./data/shapes` and `./data/materials` folders. 

      (*Note: make sure to use objects names that are shown in Blender for the dictionary "values", e.g. use "SmoothCube_v2" for entry "cube". One can check these names by opening the shape blender files.*)

   * *You can add your own meshes into the `./data/shapes` as well, just make sure to set appropriate initial scales and poses for the shapes in Blender.   

     

2. Configure the `./run_gen.sh` file:

   * `num_scenes_per_batch`: number of scenes created per batch. Here we do batched generation to avoid subtle run time errors (*max: 200*). 
   * `num_batches`: number of batches. (Total number of scenes generated = (num_batches - counter) * num_scenes_per_batch)
   * `num_views`: how many observations taken for one scene. (Total number of images = Total number of scenes generated * num_views)
   * Python arguments (e.g. image `width` and `height`): cf. the `ArgumentParser` definition in `render_images_mv.py` (*line 59-178*)  

   

3. In the opened terminal, run:

   ``````
   . ./run_gen.sh
   ``````
   to generate data. The data will be saved to `./static_scene_generator/output/` as: 
   
   ``````
     static_scene_generator/output/
         ├── images (scene#_view#.png)
         ├── masks  (scene#_view#.npy)
         └── scenes (meta info for disentanglement evaluations, scene#.json where one ".json" corresponds to multiple ".png" and 					".npy"---one scene charges multiple observations)
   ``````



## Cite

Cite the paper if you found this repo useful.

```latex
@inproceedings{nanbo2020mulmon,
  title={Learning Object-Centric Representations of Multi-Object Scenes from Multiple Views},
  author={Nanbo, Li and Eastwood, Cian and Fisher, Robert B},
  booktitle={Advances in Neural Information Processing Systems},
  year={2020}
}
```
