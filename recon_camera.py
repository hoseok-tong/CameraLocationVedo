import os
import cv2 as cv
import numpy as np
from utils import extract_camera_parameters_xml, read_camera_parameters, load_camera_params_mat

class CameraReconstructor:
    def __init__(self, calib_path, origin_offset):
        if isinstance(calib_path, list):    # MVS .txt
            print(calib_path[0])
            intrinsics = []
            extrinsics = []
            for calib in calib_path:
                ii, ee = read_camera_parameters(calib)
                intrinsics.append(ii)
                extrinsics.append(ee)

            intrinsics = np.stack(intrinsics)   # (n, 3, 3)
            extrinsics = np.stack(extrinsics)   # (n, 4, 4)
            # extrinsics[:, :3, 3] += extrinsics[:,:3,:3].transpose(-2,-1) @ origin_offset   # Transform the center of the object to 0,0,0
            # extrinsics[:, :3, 3] -= origin_offset   # Transform the center of the object to 0,0,0
            # extrinsics[:, :3, 3] *= 0.001       # do * 0.001 for MVS .txt

        else:
            if calib_path.split('.')[-1] == 'xml':  # metashape .xml
                print(calib_path)
                camera_params = extract_camera_parameters_xml(calib_path)

                intrinsics = []
                extrinsics = []
                for idx in range(len(camera_params)):
                    tmp_transform = camera_params[idx]['transform_matrix'].astype(np.float32)
                    tmp_intrinsic = np.array(camera_params[idx]['intrinsic_matrix']).astype(np.float32)
                    tmp_intrinsic[0, 2] -= 0  # Adjust cx for cropping
                    tmp_intrinsic[1, 2] -= 0    # Adjust cy for cropping

                    tmp_extrinsic = np.eye(4).astype(np.float32)
                    tmp_extrinsic[:3, :3] = tmp_transform[:3, :3].transpose()
                    tmp_extrinsic[:3, 3] = - tmp_transform[:3, :3].transpose() @ tmp_transform[:3, 3]

                    intrinsics.append(tmp_intrinsic)
                    extrinsics.append(tmp_extrinsic)

                intrinsics = np.stack(intrinsics)   # (n, 3, 3)
                intrinsics[:,0,2] += 2048   # Transform the image coordinate origin
                intrinsics[:,1,2] += 2048   # Transform the image coordinate origin
                intrinsics[:,:2,:2] = intrinsics[:,:2,:2] * (2000/4096)
                extrinsics = np.stack(extrinsics)   # (n, 3, 3)
                extrinsics[:, :3, 3] += origin_offset @ extrinsics[:,:3,:3].transpose(0,2,1)   # Transform the center of the object to 0,0,0


            elif calib_path.split('.')[-1] == 'mat':    # matlab calibration .mat
                print(calib_path)
                camera_params = load_camera_params_mat(calib_path)
                intrinsics = camera_params['K']     # (n, 3, 3)
                extrinsics = np.tile(np.eye(4), (len(intrinsics), 1, 1))    # (n, 4, 4)
                
                extrinsics[:, :3, :3] = camera_params['R'] @ np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
                extrinsics[:, :3, 3] = camera_params['T']
                # extrinsics[:, :3, 3] += origin_offset @ extrinsics[:,:3,:3].transpose(0,2,1)   # Transform the center of the object to 0,0,0

        

        self.camera_params = {
            'K': intrinsics[:, :3, :4],
            'R': extrinsics[:, :3, :3],
            'T': extrinsics[:, :3, 3]
        }

        os.makedirs('./output/cams', exist_ok=True)
        np.savez('./output/cameras.npz', intrinsics=intrinsics, extrinsics=extrinsics)
        self.save_camera_parameters(intrinsics, extrinsics)


    def save_camera_parameters(self, intrinsics, extrinsics):
        for i, (K, E) in enumerate(zip(intrinsics, extrinsics)):
            filename = f"./output/cams/{i:08d}_cam.txt"
            with open(filename, 'w') as f:
                f.write("extrinsic\n")
                for row in E:
                    f.write(' '.join(map(str, row)) + '\n')
                f.write("\nintrinsic\n")
                for row in K:
                    f.write(' '.join(map(str, row)) + '\n')


if __name__ == "__main__":
    # Example usage
    origin_offset = np.array([0, 0, 0])
    c = CameraReconstructor('path_to_calibration_file.xml', origin_offset)
