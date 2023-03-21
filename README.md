# 3 Flavors of Path Tracer

This image is rendered from the CPP-Tracer via Photon Mapping.

- SPP:25 

- Total number of photon emissions from light sources: 100 000 000

- Photon maps and numbers of stored photons:

- Global photons: 8 123 058
  
- Caustic photons: 120 653 488

<img src="media/water_bunny_caustics.png" alt="drawing" width="1000"/>


## 


Rendering Equation Surface Form | Rendering Equation Directional Form
:-------------------------:|:-------------------------:
 <img width="845" alt="Screenshot 2023-03-21 at 01 34 25" src="https://user-images.githubusercontent.com/25319668/226526544-ab4080d5-700f-45bf-bf6b-4de10413e8b1.png"> | <img width="846" alt="Screenshot 2023-03-21 at 01 34 16" src="https://user-images.githubusercontent.com/25319668/226526545-a1406a7a-b4f1-49cb-bde4-cd7de97ff400.png">


## Monte-Carlo Integration with Important Sampling in Action


<img width="704" alt="Screenshot 2023-02-28 at 10 39 31" src="https://user-images.githubusercontent.com/25319668/221903302-53c34f1a-f285-4fde-ae84-7f98d5dcea33.png">

## C++ Refined Path Tracer

### About
This Path-Tracer gives the full path tracing capacity. 

The project includes:
Multithreading, Monte Carlo Integration, Multiple Importance Sampling, 
VNDF-GGX Microfacet model, Uber BSDF(mixing reflection and transmission), Photon Mapping, Tonemapping and more.

<img width="564" alt="Screenshot 2023-02-27 at 14 42 30" src="https://user-images.githubusercontent.com/25319668/221666604-5d8ca269-8635-446d-8f05-e91a9d948f24.png">
<img width="515" alt="Screenshot 2023-02-27 at 14 45 03" src="https://user-images.githubusercontent.com/25319668/221666889-767a7436-4e92-4450-b99e-745e2f577e4e.png">


### Installation

This project is built with C++20, the dependencies are self-contained:

* glm
* json_parser

```
cd CPP-Tracer
rm -rf build/
mkdir build
cd build 
cmake ../
make
```
### Run 
```
build/CPP-Path-Tracer
```

## PyTorch Differential Path Tracer

### About
This PyTorch Path Tracer aims to integrate future deep learning models 
with global illumination path tracers. 

We can experiment with Inverse Rendering to reconstruct potential BSDFs. 
The most feasible reconstruction is the diffuse BRDF for now.

### Installation

Setup a [Conda environment](https://docs.conda.io/en/latest/miniconda.html) and install packages below:

* PyTorch
* OpenEXR
* hydra-core
pillow
* opencv-python
* open3d
* tqdm
* plotly

### Run

Render a scene using a specific integrator:

```
python render.py integrator=xx scene=cbox spp=256
```

Inverse Rendering:
```
Training:
python train.py --config-name train_render \
    scene=cbox_train_diffuse \
    gt=./scripts/cbox-diffuse.exr
    
To check progress:
tensorboard --logdir tensorboard

Rendering:
python render.py scene=cbox_train_diffuse \
    integrator=path_mis \
    spp=128 \
    checkpoint=./scripts/cbox-diffuse-walls-step4000.ckpt
```



## Processing Path Tracer(Coursework Adapted)

### About

This Ray-Tracer is adapted from my coursework CS-6491, Grad Computer Graphics, 
taught by Prof. Greg Turk. 

Everything is pure Java from scratch without any 3rd-party libraries, 
including all the linear-algebra math.

The project includes: KD-BVH, Instancing, Distribution Ray Tracing(soft shadow, depth of field, motion blur, glossy reflection, anti-aliasing), and more to be added.

### Installation

You need to download Processing first:
https://processing.org/download

Then, double-click:
```
p3_ray_tracer_acc_dist.pde
```
to open the software and click Run.



## Acknowledgement
1. https://faculty.cc.gatech.edu/~turk/bunny/bunny.html
2. http://simonstechblog.blogspot.com/2020/01/note-on-sampling-ggx-distribution-of.html
3. https://schuttejoe.github.io/post/ggximportancesamplingpart1/
4. https://agraphicsguynotes.com/posts/sample_microfacet_brdf/
5. http://filmicworlds.com/blog/filmic-tonemapping-operators/
6. https://tavianator.com/2011/ray_box.html
7. https://graphics.pixar.com/library/OrthonormalB/paper.pdf
8. https://github.com/skarupke/heap
9. https://seblagarde.wordpress.com/2013/04/29/memo-on-fresnel-equations/
10. http://jcgt.org/published/0007/04/01/
11. http://jcgt.org/published/0003/02/03/
12. https://www.gdcvault.com/play/1024478/PBR-Diffuse-Lighting-for-GGX
13. https://www.cs.cornell.edu/~srm/publications/EGSR07-btdf.html
14. https://jcgt.org/published/0009/04/01/
15. https://psychopath.io/post/2021_01_30_building_a_better_lk_hash
16. https://github.com/skeeto/hash-prospector
17. https://web.maths.unsw.edu.au/~fkuo/sobol/
