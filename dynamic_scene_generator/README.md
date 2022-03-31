# CLROC-DynamicScenes  
Data generator used to generate **Moving-Observer-Dynamic-Scene** CLEVR images as described in:  
[Object-Centric Representation Learning with Generative Spatial-Temporal Factorization](https://arxiv.org/abs/2111.05393)  
[**Li Nanbo**](http://homepages.inf.ed.ac.uk/s1601283/), **Muhammad Ahmed Raza**, **Hu Wenbin**, **Sun Zhaole**, [**Robert B. Fisher**](https://homepages.inf.ed.ac.uk/rbf/)  
NeurIPS 2021  



## Usage  

**Pre:** Open a terminal and navigate it to the root of the repo (i.e. `<YOUR-PATH>/CLEVR-Object-Centric`). Then you will need to add the generator path to Blender python path, this is done by executing:  

``````
echo $PWD/static_scene_generator >> $BLENDER/2.79/python/lib/python3.5/site-packages/clevr.pth && cd ./static_scene_generator
``````
Do leave the terminal OPEN!
  
## (TO FINISH...)
  

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
