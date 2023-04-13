import sys, os
import argparse
import math
import bpy
import json
import random
import numpy as np
from mathutils import Vector
import pdb


###################
# General utils
###################
def extract_args(input_argv=None):
  """
  Pull out command-line arguments after "--". Blender ignores command-line flags
  after --, so this lets us forward command line arguments from the blender
  invocation to our own script.
  """
  if input_argv is None:
    input_argv = sys.argv
  output_argv = []
  if '--' in input_argv:
    idx = input_argv.index('--')
    output_argv = input_argv[(idx + 1):]
  return output_argv


def clamp(x, minimum, maximum):
    return max(minimum, min(x, maximum))


def read_json(fname):
    with open(fname, "r") as read_file:
        return json.load(read_file)


def write_json(content, fname):
    with open(fname, "w") as write_file:
        json.dump(content, write_file)


def deg2rad(deg):
    return math.pi * (deg / 180.)


def rad2deg(rad):
    return (rad * 180.) / math.pi


##############################
# Blender & Scene utils
##############################
def inital_xy_coordinates():
    coordinates = []

    x_range = round(random.uniform(0.8, 2.0), 2)
    y_range = round(random.uniform(-2.0, -0.8), 2)
    coordinates.append([x_range, y_range])

    x_range = round(random.uniform(-2.0, -0.8), 2)
    y_range = round(random.uniform(0.8, 2.0), 2)
    coordinates.append([x_range, y_range])

    x_range = round(random.uniform(-2.0, -0.8), 2)
    y_range = round(random.uniform(-2.0, -0.8), 2)
    coordinates.append([x_range, y_range])

    x_range = round(random.uniform(0.8, 2.0), 2)
    y_range = round(random.uniform(0.8, 2.0), 2)
    coordinates.append([x_range, y_range])

    return coordinates


def draw_scene(filepath, shape, material, color, scale, coor, index, SHAPES_CONTAINER, MATERIAL_CONTAINER, blender_obj=None):
    # draw shape
    shape_filename = filepath + '/model/shapes/' + shape + '.blend/Object/' + shape
    bpy.ops.wm.append(filename=shape_filename)
    bpy.ops.transform.resize(value=(scale, scale, scale))
    bpy.ops.transform.translate(value=(coor[0], coor[1], scale))

    # Give shape a new name to avoid conflicts
    shape_new_name = '%s_%d' % (shape, index)
    bpy.data.objects[shape].name = shape_new_name
    # Record
    SHAPES_CONTAINER.append(shape_new_name)

    # Set active
    # bpy.context.view_layer.objects.active = bpy.data.objects[shape_new_name]
    bpy.context.scene.objects.active = bpy.data.objects[shape_new_name]

    # Set Physics
    set_physics()

    # load material
    material_filename = filepath + '/model/materials/' + material + '.blend/NodeTree/' + material
    bpy.ops.wm.append(filename=material_filename)

    mat_count = len(bpy.data.materials)
    bpy.ops.material.new()
    mat = bpy.data.materials['Material']
    mat.name = 'Material_%d' % (mat_count + 1)
    # Record
    MATERIAL_CONTAINER.append(mat.name)

    obj = bpy.context.active_object
    # assert len(obj.data.materials) == 0
    obj.data.materials.append(mat)

    output_node = None
    for n in mat.node_tree.nodes:
        if n.name == 'Material Output':
            output_node = n
            break

    group_node = mat.node_tree.nodes.new('ShaderNodeGroup')
    group_node.node_tree = bpy.data.node_groups[material]

    # Find and set the "Color" input of the new group node
    for inp in group_node.inputs:
        print(inp.name)
        if inp.name in ['Color']:
            inp.default_value = color

    # Wire the output of the new group node to the input of
    # the MaterialOutput node
    mat.node_tree.links.new(
        group_node.outputs['Shader'],
        output_node.inputs['Surface'],
    )

    # Link Material and Shape
    bpy.data.objects[shape_new_name].active_material = bpy.data.materials[mat.name]

    if blender_obj is not None:
        blender_obj.append(bpy.context.object)
    
    # Deactivate
    # bpy.context.view_layer.objects.active = None
    bpy.context.scene.objects.active = None
    return blender_obj


def set_physics():
    bpy.ops.rigidbody.object_add()
    bpy.context.object.rigid_body.mass = 100

    bpy.context.object.rigid_body.friction = 0
    bpy.context.object.rigid_body.restitution = 1.0

    bpy.context.object.rigid_body.use_margin = True
    bpy.context.object.rigid_body.collision_margin = 0.01

    bpy.context.object.rigid_body.use_deactivation = True
    bpy.context.object.rigid_body.use_start_deactivated = True


def set_layer(obj, layer_idx):
  """ Move an object to a particular layer """
  # Set the target layer to True first because an object must always be on
  # at least one layer.
  obj.layers[layer_idx] = True
  for i in range(len(obj.layers)):
    obj.layers[i] = (i == layer_idx)


def render_object_masks(blender_objects, pathfix='masks/'):
    """
    Render a version of the scene with shading disabled and unique materials
    assigned to all objects, and return a set of all colors that should be in the
    rendered image. The image itself is written to path. This is used to ensure
    that all objects will be visible in the final rendered scene.

    path = '.../masks/' is a dir
    """
    render_args = bpy.context.scene.render

    # Cache the render args we are about to clobber
    old_filepath = render_args.filepath
    old_engine = render_args.engine
    old_use_antialiasing = render_args.use_antialiasing

    # Move the lights and ground to layer 2 so they don't render
    set_layer(bpy.data.objects['Lamp_Key'], 2)
    set_layer(bpy.data.objects['Lamp_Fill'], 2)
    set_layer(bpy.data.objects['Lamp_Back'], 2)
    set_layer(bpy.data.objects['Ground'], 2)

    # ['Area', 'Camera', 'Empty', 'Ground', 'Lamp_Back',
    # 'Lamp_Fill', 'Lamp_Key', 'OBJECTS_xxxx' ...]
    for obj in blender_objects:
        set_layer(obj, 2)

    # Add random shadeless materials to all objects
    object_colors = set()
    old_materials = []
    for i, obj in enumerate(blender_objects):
        # Override some render settings to have flat shading
        if not os.path.isdir(pathfix):
            os.makedirs(pathfix)
        obj_mk_path = os.path.join(pathfix, '{:02d}.png'.format(i))
        render_args.filepath = obj_mk_path
        render_args.engine = 'BLENDER_RENDER'
        render_args.use_antialiasing = False

        set_layer(obj, 0)
        old_materials.append(obj.data.materials[0])
        bpy.ops.material.new()
        mat = bpy.data.materials['Material']
        mat.name = 'Material_%d' % i
        object_colors.add((255.0, 255.0, 255.0))
        mat.diffuse_color = [255.0, 255.0, 255.0]
        mat.use_shadeless = True
        obj.data.materials[0] = mat

        # Render the scene
        bpy.ops.render.render(write_still=True)
        set_layer(obj, 2)

    for obj in blender_objects:
        set_layer(obj, 0)

    # Undo the above; first restore the materials to objects
    for mat, obj in zip(old_materials, blender_objects):
        obj.data.materials[0] = mat

    # Move the lights and ground back to layer 0
    set_layer(bpy.data.objects['Lamp_Key'], 0)
    set_layer(bpy.data.objects['Lamp_Fill'], 0)
    set_layer(bpy.data.objects['Lamp_Back'], 0)
    set_layer(bpy.data.objects['Ground'], 0)

    # Set the render settings back to what they were
    render_args.filepath = old_filepath
    render_args.engine = old_engine
    render_args.use_antialiasing = old_use_antialiasing

    return object_colors


def make_circle_coor(radius, y_axis):
    x_axis = np.sqrt(radius ** 2 - y_axis ** 2)
    return [x_axis, y_axis]


def get_next_camera_location(p0, v_azi=0., v_ele=0., init_pos=False):
    """
    Camera trajectory control -- with distance to scene centre fixed (i.e. camera is on a dome surface).
    args:
        p0:  (x0,y0,z0) current camera location
        v_azi: (in degs) azimuth angular velocity
        v_ele: (in degs) elevation angular velocity (Note the elevation is in range [15,  55] degrees)
    """
    if isinstance(p0, list):
        p0 = tuple(p0)
    assert isinstance(p0, tuple)

    x0, y0, z0 = p0
    r_xy = math.sqrt(math.pow(x0, 2) + math.pow(y0, 2))
    r = math.sqrt(math.pow(r_xy, 2) + math.pow(z0, 2))

    if init_pos:
        v_azi = random.choice(list(range(180, -180, -30)))

    azimuth = math.atan2(y0, x0) + deg2rad(v_azi)
    # elevation = math.asin(z0/r) + v_ele
    elevation = clamp(math.asin(z0/r) + deg2rad(v_ele),
                      minimum=deg2rad(15), maximum=deg2rad(60))

    r_xy_new = r * np.cos(elevation)
    x_new, y_new, z_new = r_xy_new * np.cos(azimuth), r_xy_new * np.sin(azimuth), r * np.sin(elevation)
    return [x_new, y_new, z_new, azimuth, elevation]


def li_map(x, a, b):
    return a * x + b


def readout_obj_loc(b_objs):
    return [list(bpy.data.objects[obj.name].matrix_world.translation) for obj in b_objs]


def init_parser():
    parser = argparse.ArgumentParser()
    # data config
    parser.add_argument('--episode', default=1, type=int, metavar='N', help="number of data samples")
    parser.add_argument('--num_frames', default=48, type=int, metavar='N', help='number of frames per data sample')
    parser.add_argument('--sim_fps', default=16, type=int, metavar='N', help='simulation frame rate')
    parser.add_argument('--image_size', default=128, type=int, metavar='N', help='number of frames per data sample')
    parser.add_argument('--min_num_objs', default=1, type=int, metavar='N',
                        help="the least number of additional objects")
    parser.add_argument('--max_num_objs', default=4, type=int, metavar='N',
                        help="the least number of additional objects")

    parser.add_argument('--level', default=1, type=int, help="which level of sampler")
    parser.add_argument('--v_azi', default=0., type=float, help="azimuth angular velocity")
    parser.add_argument('--v_ele', default=0., type=float, help="elevation angular velocity")
    parser.add_argument('--force', default=10000., type=float, help="force field to push the initial object")
    parser.add_argument('--v_cam_level', default='slow', type=str, help="v_cam level")
    parser.add_argument('--v_obj_level', default='slow', type=str, help="v_obj level")
    parser.add_argument("--get_mask", help="whether generate masks or not?", action="store_true", default=False)

    # parser.add_argument('--debug_coeff', default=0.0, type=float, help="xxx")

    # device config
    parser.add_argument('--use_gpu', default=1, type=int, help='which gpu to use')

    # path config
    parser.add_argument("-i", '--input_blender', default='./model/base_scene_mv_bg.blend',
                        help="path to the input .blender scene base")
    parser.add_argument("-o", '--output_dir', default='./output',
                        help="save the generated data to")
    return parser


def main(args):
    # --- init global variables --- #
    GET_MASKS = args.get_mask
    SHAPES = ['SmoothCube_v2', 'SmoothCylinder', 'Sphere']
    MATERIAL = ['Rubber', 'MyMetal']
    INDEX_CONTAINER = {'SmoothCube_v2': 0, 'SmoothCylinder': 0, 'Sphere': 0}
    COLORS_NAME = ['Pink', 'Red', 'Blue', 'Green', 'Yellow']
    COLORS = {'Pink': [0.8, 0.3, 0.7, 1.0], 'Red': [0.8, 0.2, 0.2, 1.0], 'Blue': [0.2, 0.2, 0.8, 1.0],
              'Green': [0.2, 0.8, 0.3, 1.0], 'Yellow': [0.7, 0.8, 0.2, 1.0]}
    SCALE = [0.70, 0.75, 0.80]  # [0.6, 0.7, 0.8]
    CAM_VEL_SAMPLER = {
        0: {
         'slow': np.asarray([0.  , 0.  , 0.  , 0.1 , 0.2 , 0.4 , 0.2 , 0.1 , 0.  , 0.  , 0.  ]).astype('float32'),
         'fast': np.asarray([0.  , 0.  , 0.  , 0.1 , 0.2 , 0.4 , 0.2 , 0.1 , 0.  , 0.  , 0.  ]).astype('float32')
        },
        1: {
         'slow': np.asarray([0.05, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095]).astype('float32'),
         'fast': np.asarray([0.05, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095]).astype('float32')
        },
        2: {
         'slow': np.asarray([0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.  , 0.  , 0.  , 0.  , 0.  , 0.   ]).astype('float32'),
         'fast': np.asarray([0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.2 , 0.2 , 0.2 , 0.2 , 0.2  ]).astype('float32')
        },
        3: {
         'slow': np.asarray([0.3 , 0.3 , 0.28, 0.11, 0.01, 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ]).astype('float32'),
         'fast': np.asarray([0.  , 0.  , 0.  , 0.  , 0.  , 0.  , 0.01, 0.11, 0.28, 0.3 , 0.3 ]).astype('float32')
        }
    }
    OBJ_VEL_SAMPLER = {
        0: {
        'slow': np.asarray([0.  , 0.  , 0.  , 0.1 , 0.2 , 0.4 , 0.2 , 0.1 , 0.  , 0.  , 0.  ]).astype('float32'),
        'fast': np.asarray([0.  , 0.  , 0.  , 0.1 , 0.2 , 0.4 , 0.2 , 0.1 , 0.  , 0.  , 0.  ]).astype('float32')
        },
        1: {    
        'slow': np.asarray([0.05, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095]).astype('float32'),
        'fast': np.asarray([0.05, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095, 0.095]).astype('float32')
        },
        2: {
        'slow': np.asarray([0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.  , 0.  , 0.  , 0.  , 0.  , 0.   ]).astype('float32'),
        'fast': np.asarray([0.  , 0.  , 0.  , 0.  , 0.  , 0.2 , 0.2 , 0.2 , 0.2 , 0.2 , 0.   ]).astype('float32')
        },
        3: {
        'slow': np.asarray([0.25, 0.38, 0.33, 0.02, 0.02, 0.  , 0.  , 0.  , 0.  , 0.  , 0.  ]).astype('float32'),
        'fast': np.asarray([0.  , 0.  , 0.  , 0.  , 0.  , 0.02, 0.08, 0.15, 0.35, 0.35, 0.05]).astype('float32')
        }
    }
    filepath = '.'
    DS_pack = {
        'dir': args.output_dir,
        'v_cam_level': args.v_cam_level,
        'v_obj_level': args.v_obj_level,
        'scenes': []
    }

    # --- start rendering --- #
    print(" ==== START GENERATING DATA ==== ")
    for ep in range(args.episode):
        coors = inital_xy_coordinates()
        shape_num = random.randint(args.min_num_objs, args.max_num_objs)
        blender_objects = []

        SHAPES_CONTAINER = []
        MATERIAL_CONTAINER = []
        INDEX_CONTAINER['SmoothCube_v2'] = 0
        INDEX_CONTAINER['SmoothCylinder'] = 0
        INDEX_CONTAINER['Sphere'] = 1

        # Load basic scene
        bpy.ops.wm.open_mainfile(filepath=os.path.abspath(args.input_blender))

        # Make inital ball
        r_initial_ball = 4.5  # was 6.0
        # Set input angle
        y_initial_ball = round(random.uniform((0 - r_initial_ball), -1), 2)
        coor_initial_ball = make_circle_coor(r_initial_ball, y_initial_ball)
        color_initial_ball = COLORS[random.choice(COLORS_NAME)]
        scale_initial_ball = random.choice(SCALE)
        blender_objects = draw_scene(filepath, 'Sphere', 'Rubber', color_initial_ball, scale_initial_ball, coor_initial_ball, 1,
                   SHAPES_CONTAINER, MATERIAL_CONTAINER, blender_obj=blender_objects)

        # Make Force Field
        r_force = 5.  # was 7.0
        x_force = (coor_initial_ball[0] / r_initial_ball) * r_force
        y_force = (coor_initial_ball[1] / r_initial_ball) * r_force
        bpy.ops.object.effector_add(type='FORCE', location=(x_force, y_force, scale_initial_ball))

        # Strength
        ds_dict = {'views':[]}
        strength_coeff = np.random.choice(np.linspace(0., 1.0, 11), p=OBJ_VEL_SAMPLER[args.level][args.v_obj_level])
        ds_dict['v_obj'] = strength_coeff
        bpy.context.object.field.strength = li_map(strength_coeff, args.force, 0.)  # original: 11000
        # bpy.context.object.field.flow = 10.0
        bpy.context.object.field.use_min_distance = True
        bpy.context.object.field.use_max_distance = True
        bpy.context.object.field.distance_min = 3.5
        bpy.context.object.field.distance_max = 3.5
        bpy.context.object.field.seed = 54

        for sam in range(shape_num):
            # Select Shapes
            shape = random.choice(SHAPES)
            # Select Shapes
            material = random.choice(MATERIAL)
            # Select Colors
            color = COLORS[random.choice(COLORS_NAME)]
            # Select Size
            scale = random.choice(SCALE)
            # Coordinates
            coor = coors[sam]
            # Index
            INDEX_CONTAINER[shape] += 1
            index = INDEX_CONTAINER[shape]

            # Draw Scene
            blender_objects = draw_scene(filepath, shape, material, color, scale, coor, index,
                       SHAPES_CONTAINER, MATERIAL_CONTAINER, blender_obj=blender_objects)

        # Render
        frame_start = 1
        bpy.context.scene.frame_start = frame_start
        frame_end = args.num_frames
        bpy.context.scene.frame_end = frame_end
        cam_azi_dir = np.random.choice([-1, 1], p=[0.5, 0.5])
        cam_ele_dir = np.random.choice([-1, 1], p=[0.5, 0.5])


        ds_dict['obj_pos'] = []
        for i in range(frame_start, frame_end + 1):
            path = os.path.join(args.output_dir, str(ep))
            ds_dict['path'] = path

            folder = os.path.exists(path)
            if not folder:
                os.makedirs(path)
            file_path = os.path.join(path, '{:04d}.png'.format(i))

            bpy.context.scene.frame_set(i)
            bpy.context.scene.render.engine = 'CYCLES'
            bpy.context.scene.render.filepath = file_path
            bpy.context.scene.render.image_settings.file_format = 'PNG'
            bpy.context.scene.render.resolution_x = args.image_size  # perhaps set resolution in code
            bpy.context.scene.render.resolution_y = args.image_size
            bpy.context.scene.render.resolution_percentage = 100
            # bpy.context.scene.render.tile_x = 256
            # bpy.context.scene.render.tile_y = 256
            bpy.context.scene.cycles.blur_glossy = 2.0
            bpy.context.scene.cycles.samples = 512
            bpy.context.scene.cycles.min_light_bounces = 8
            bpy.context.scene.cycles.min_transparent_bounces = 8

            # readout all object locations
            ds_dict['obj_pos'].append(readout_obj_loc(blender_objects))

            # Turn on GPU
            if bpy.app.version < (2, 78, 0):
                bpy.context.user_preferences.system.compute_device_type = 'CUDA'
                bpy.context.user_preferences.system.compute_device = 'CUDA_'+str(args.use_gpu)
            else:
                cycles_prefs = bpy.context.user_preferences.addons['cycles'].preferences
                cycles_prefs.compute_device_type = 'CUDA'
                print(cycles_prefs.devices)
                for dev in cycles_prefs.devices:
                    dev.use = False
                if args.use_gpu == 1:
                    cycles_prefs.devices[1].use = True
                if args.use_gpu == 0:
                    cycles_prefs.devices[2].use = True
            bpy.context.scene.cycles.device = 'GPU'

            # set camera location
            init_tag = True if i == 1 else False
            v_azi = np.random.choice(np.linspace(0., 1.0, 11), p=CAM_VEL_SAMPLER[args.level][args.v_cam_level]) * cam_azi_dir
            v_ele = np.random.choice(np.linspace(0., 1.0, 11), p=CAM_VEL_SAMPLER[args.level][args.v_cam_level]) * cam_ele_dir
            # cam_next = GRID_VIEWS[i-1]
            ds_dict['v_cam'] = (v_azi, v_ele)
            cam_next = get_next_camera_location(tuple([p for p in bpy.context.scene.camera.location]),
                                                v_azi=li_map(v_azi, args.v_azi, 0.),
                                                v_ele=li_map(v_ele, args.v_ele, 0.),
                                                init_pos=init_tag)
                                                # v_azi=args.v_azi, v_ele=args.v_ele)
            bpy.context.scene.camera.location = Vector(cam_next[:3])
            bpy.context.scene.render.tile_x = 128
            bpy.context.scene.render.tile_y = 128
            bpy.context.scene.render.use_antialiasing = False

            ds_dict['views'].append(cam_next)

            if GET_MASKS:
                render_object_masks(blender_objects,
                                    pathfix=os.path.join(path, 'mask{:04d}'.format(i)))
                                    # pathfix=output_mask+'_{:02d}'.format(vid))

            # FPS
            bpy.context.scene.render.fps = args.sim_fps

            bpy.ops.render.render(write_still=True, use_viewport=True)

            # update frame (very important)
            bpy.context.scene.update()
            print("Frame %d:" % i)

        DS_pack['scenes'].append(ds_dict)

        # Recycle
        print(MATERIAL_CONTAINER)
        for i in MATERIAL_CONTAINER:
            print(i)
            bpy.data.materials.remove(bpy.data.materials[i])
        for i in SHAPES_CONTAINER:
            bpy.data.objects[i].select = False
        for i in SHAPES_CONTAINER:
            print(i)
            bpy.data.objects[i].select = True
            bpy.ops.object.delete()

        # Delete Force Field
        bpy.ops.object.select_all(action='DESELECT')
        try:
            bpy.data.objects['Field'].select = True
            bpy.ops.object.delete()
        except:
            bpy.ops.object.delete()

    write_json(
        DS_pack, os.path.join(args.output_dir, 'meta_info.json')
    )
    print(" ==== Generation FINISHED ==== \n")
    ##########################################################


# ------------ main body ------------ #
if __name__ == '__main__':
    parser = init_parser()
    argv = extract_args()
    args = parser.parse_args(argv)
    main(args)

