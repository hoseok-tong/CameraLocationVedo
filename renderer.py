import os
import json
import numpy as np
import vedo
from utils import load_obj, save_obj


def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


class Mesh:
    def __init__(self, vertices, faces):
        self.mesh = None
        self.v = vertices
        self.f = faces
        self.initialize(vertices, faces)
    
    def initialize(self, vertices, faces):
        self.mesh = vedo.Mesh([vertices, faces], c=[225, 225, 225])
    
    def add(self, vp):
        vp.add(self.mesh)

    def remove(self, vp):
        vp.remove(self.mesh)
    
    def update(self, vertices):
        self.mesh.points(vertices)

    
class Cameras:
    def __init__(self, camera_params):
        self.camera_params = camera_params
        self.cameras = {'names': [], 'pyramids': [], 'axes': []}
        self.initialize()
    
    def initialize(self):
        rotmats = self.camera_params['R']
        transls = self.camera_params['T']
        for idx, (rotmat, transl) in enumerate(zip(rotmats, transls)):
            nametxt = 'CAM{:02d}'.format(idx + 1)
            
            camera_rotmat = rotmat                  # extrinisic contains translation
            camera_transl = - transl @ rotmat       # extrinisic contains translation

            self.cameras['names'].append(self.get_name(nametxt, camera_transl))
            self.cameras['pyramids'].append(self.get_pyramid(camera_rotmat.T, camera_transl))
            self.cameras['axes'].append(self.get_axes(camera_rotmat.T, camera_transl))
    
    def add(self, vp):
        for key in self.cameras:
            vp.add(self.cameras[key])
    
    def remove(self, vp):
        for key in self.cameras:
            vp.remove(self.cameras[key])
    
    @staticmethod
    def get_name(nametxt, transl, scale=100):  # control scale heuristically, 200(mm scale)
        name = vedo.Text3D(nametxt, pos=transl, s=scale)
        return name
    
    @staticmethod
    def get_pyramid(rotmat, transl, scale=250): # control scale heuristically, 500(mm scale)
        pyramid = vedo.Pyramid(c='w', alpha=0.5, s=scale, axis=(0, 0, -1), height=scale * 1.5).rotate_z(45)
        trfm = np.eye(4)
        trfm[:3, :3] = rotmat
        trfm[:3, 3] = transl
        pyramid.apply_transform(trfm, concatenate=True)
        return pyramid

    @staticmethod
    def get_axes(rotmat, transl, scale=200):        # control scale heuristically, 400(mm scale)
        cam_x_axis = np.matmul([1, 0, 0], rotmat.T) # Red x
        cam_y_axis = np.matmul([0, 1, 0], rotmat.T) # Green y
        cam_z_axis = np.matmul([0, 0, 1], rotmat.T) # Blue z
        x_axis = vedo.Arrow(transl, transl + cam_x_axis * scale, c='r')
        y_axis = vedo.Arrow(transl, transl + cam_y_axis * scale, c='g')
        z_axis = vedo.Arrow(transl, transl + cam_z_axis * scale, c='b')
        return [x_axis, y_axis, z_axis]


class CameraPlotter:
    def __init__(self, qt_widget=None):
        self.vp = vedo.Plotter(
            qt_widget=qt_widget, 
            bg=(30, 30, 30),
            axes=4
            )
        
        # Add origin, axes
        scale=5
        self.vp.add(vedo.Point([0.0, 0.0, 0.0], c='r'))

        self.cameras = None
        self.origin = None
        self.mesh = None
    
    def load_cameras(self, camera_params):
        if self.cameras is not None:
            self.remove_cameras()
        self.cameras = Cameras(camera_params)
    
    def init_mesh(self, mesh_path, calib_path):
        if isinstance(calib_path, list):
            obj_dict = load_obj(mesh_path)              # when .txt format, mm scale
            v = obj_dict['vertices']
            f = obj_dict['faces']
            origin_offset = v.mean(axis=0)*0.0      # when .txt format, ignore origin_offset
        else:
            obj_dict = load_obj(mesh_path)
            v = obj_dict['vertices']
            f = obj_dict['faces']
            c = obj_dict['colors']            
            v *= 1000.0             # when .xml format, m -> mm
            origin_offset = v.mean(axis=0)
            v = v - origin_offset   # when .xml format, get origin_offset, transform system to origin
            origin_mesh_path = mesh_path.split('.')[0] + '_1000_origin.obj'
            save_obj(origin_mesh_path, v, f, c)

        self.mesh = Mesh(v, f)
        
        print(f"mesh_path: {mesh_path}")
        print(f"origin_offset: {origin_offset}")
        return origin_offset
    
    def add_cameras(self):
        self.cameras.add(self.vp)
        self.vp.render()

    def add_origin(self):
        self.vp.add(self.origin)
        self.vp.render()

    def add_mesh(self):
        self.mesh.add(self.vp)
        self.vp.render()

    def remove_cameras(self):
        self.cameras.remove(self.vp)
        self.vp.render()
    
    def show(self):
        self.vp.show()
    
    def update(self):
        self.vp.render()