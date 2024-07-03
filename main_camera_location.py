import os
import sys
import numpy as np

from glob import glob
from PyQt5 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from renderer import CameraPlotter
from recon_camera import CameraReconstructor



class Visualizer(QtWidgets.QWidget):
    def __init__(self, image_size, calib_path, mesh_path=None, parent=None):
        super().__init__(parent)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.render)
        self.counter = 0
        self.play = False
        self.init_ui()
        self.load_data(calib_path, mesh_path, image_size)
    
    def init_ui(self):
        renderer_before = QVTKRenderWindowInteractor(self)
        self.plotter_before = CameraPlotter(qt_widget=renderer_before)
        self.plotter_before.show()

        
        layout = QtWidgets.QGridLayout()
        layout.addWidget(renderer_before,  0, 0, 1, 1)
        self.setLayout(layout)
    
    def load_data(self, calib_path, mesh_path, image_size):
        if mesh_path != None:
            origin_offset = self.plotter_before.init_mesh(mesh_path, calib_path)
            self.plotter_before.add_mesh()
        else:
            origin_offset = np.array([0.0, 0.0, 0.0]) 

        self.reconstructor = CameraReconstructor(calib_path, origin_offset, image_size)
        camera_params = self.reconstructor.camera_params
        self.plotter_before.load_cameras(camera_params)
        self.plotter_before.add_cameras()


    def render(self):
        if self.counter > self.seq_len - 1:
            self.counter = 0

        self.counter += 1




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    
    image_size = (1984,1984)

    # calib_path = sorted(glob("E:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_Face_KHS/Output/cams/frame0005/*.txt"))  # Folder containing the .txt files
    # calib_path = 'E:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_KHS_metashape/cameras.xml'
    calib_path = './data/test/cameras.xml'

    # mesh_path = 'E:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_Face_KHS/Output/points_mvsnet/frame0005/3D_Scan/filtered_mesh_9.obj'
    # mesh_path = 'E:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_KHS_metashape/mesh3D.obj'
    mesh_path = './data/test/mesh3D.obj'

    window = Visualizer(image_size, os.path.abspath(calib_path), os.path.abspath(mesh_path))

    window.setWindowTitle('Visualizer')
    window.setGeometry(100, 200, 600, 800)
    window.show()
    sys.exit(app.exec_())
