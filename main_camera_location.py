import sys
import numpy as np

from glob import glob
from PyQt5 import QtWidgets, QtCore
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from renderer import CameraPlotter
from recon_camera import CameraReconstructor



class Visualizer(QtWidgets.QWidget):
    def __init__(self, calib_path, mesh_path=None, parent=None):
        super().__init__(parent)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(33)
        self.timer.timeout.connect(self.render)
        self.counter = 0
        self.play = False
        self.init_ui()
        self.load_data(calib_path, mesh_path)
    
    def init_ui(self):
        renderer_before = QVTKRenderWindowInteractor(self)
        self.plotter_before = CameraPlotter(qt_widget=renderer_before)
        self.plotter_before.show()

        
        layout = QtWidgets.QGridLayout()
        layout.addWidget(renderer_before,  0, 0, 1, 1)
        self.setLayout(layout)
    
    def load_data(self, calib_path, mesh_path):
        if mesh_path != None:
            origin_offset = self.plotter_before.init_mesh(mesh_path)
            self.plotter_before.add_mesh()
        else:
            origin_offset = np.array([0.0, 0.0, 0.0]) 

        self.reconstructor = CameraReconstructor(calib_path, origin_offset)
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
    
    # calib_path = sorted(glob("D:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_Face_KHS/Output/cams/frame0005/*.txt"))  # Folder containing the .txt files
    # calib_path = sorted(glob("./output/cams/*.txt"))  # Folder containing the .txt files
    # calib_path = 'data/initial_camera_params_2024-01-04.mat'
    # calib_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_Face_KHS/metashape/20240104_Face_KHS_cameras.xml'
    # calib_path = 'D:/workspace/NeuralHaircut/implicit-hair-data/data/custom/20240515_humanhair_seq/image/20240515_humanhair_seq_cameras.xml'
    # calib_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240515/20240515_hairreal/selected/20240515_hairreal_cameras.xml'
    # calib_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240515/20240515_hairrecon/20240515_hairrecon_cameras.xml'
    # calib_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240515/20240515_waverecon/20240515_waverecon_cameras.xml'
    # calib_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240520/20240520_hairreal/selected/20240520_hairreal_cameras.xml'
    # calib_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240520/20240520_hairstraight/20240520_hairstraight_cameras.xml'
    calib_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240520/20240520_hairwave/20240520_hairwave_cameras.xml'

    mesh_path = None
    # mesh_path = 'D:/workspace/pose_B2_recon/data/head_prior_mvs.obj'
    # mesh_path = 'D:/workspace/pose_B2_recon/data/20240515_hairrecon_simpl.obj'
    # mesh_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_Face_KHS/metashape/20240104_Face_KHS_obj_origin.obj'
    # mesh_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_Face_KHS/metashape/20240104_Face_KHS_obj.obj'
    # mesh_path = 'D:/workspace/NeuralHaircut/implicit-hair-data/data/custom/20240515_humanhair_seq/image/20240515_humanhair_seq_obj.obj'
    # mesh_path = 'D:/workspace/NeuralHaircut/implicit-hair-data/data/custom/20240515_humanhair_seq/image/20240515_humanhair_seq_obj.obj'
    # mesh_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240515/20240515_hairreal/selected/20240515_hairreal_obj_facecrop.obj'
    # mesh_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240515/20240515_hairrecon/20240515_hairrecon_obj_facecrop.obj'
    # mesh_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240515/20240515_waverecon/20240515_waverecon_obj_facecrop.obj'
    # mesh_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240520/20240520_hairreal/selected/20240520_hairreal_obj_facecrop.obj'
    # mesh_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240520/20240520_hairstraight/20240520_hairstraight_obj_facecrop.obj'
    mesh_path = 'D:/DATA/MDI_Database_1/BYRoad_Studio/20240520/20240520_hairwave/20240520_hairwave_obj_facecrop.obj'
    
    window = Visualizer(calib_path, mesh_path)

    window.setWindowTitle('Visualizer')
    window.setGeometry(100, 200, 600, 800)
    window.show()
    sys.exit(app.exec_())
