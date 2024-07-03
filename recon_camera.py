import os
import cv2 as cv
import numpy as np
from utils import extract_camera_parameters_xml, read_camera_parameters, load_camera_params_mat

class CameraReconstructor:
    def __init__(self, calib_path, origin_offset, image_size):
        if isinstance(calib_path, list):    # MVS .txt
            print(f'calib_path: {calib_path[0]}')
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

        else:
            if calib_path.split('.')[-1] == 'xml':  # metashape .xml
                print(f'calib_path: {calib_path}')
                camera_params = extract_camera_parameters_xml(calib_path)

                intrinsics = []
                extrinsics = []
                for idx in range(len(camera_params)):
                    tmp_transform = camera_params[idx]['transform_matrix'].astype(np.float32)
                    tmp_intrinsic = np.array(camera_params[idx]['intrinsic_matrix']).astype(np.float32)

                    tmp_extrinsic = np.eye(4).astype(np.float32)
                    tmp_extrinsic[:3, :3] = tmp_transform[:3, :3].transpose()
                    tmp_extrinsic[:3, 3] = - tmp_transform[:3, :3].transpose() @ tmp_transform[:3, 3]

                    intrinsics.append(tmp_intrinsic)
                    extrinsics.append(tmp_extrinsic)

                intrinsics = np.stack(intrinsics)       # (n, 3, 3)
                intrinsics[:,0,2] += image_size[0]/2    # Transform the image coordinate origin (image coord: center -> top left)
                intrinsics[:,1,2] += image_size[1]/2    # Transform the image coordinate origin (image coord: center -> top left)
                # intrinsics[:,0,2] = (intrinsics[:,0,2] - 1024)              # Crop left region
                # intrinsics[:,1,2] = (intrinsics[:,1,2] - 0)                 # Crop top region
                # intrinsics[:,:2,:3] = intrinsics[:,:2,:3] * (1920/3072)     # Reflect the resize 3072x3072 -> 1920x1920 
                extrinsics = np.stack(extrinsics)       # (n, 3, 3)
                extrinsics[:, :3, 3] *= 1000            # m -> mm scale
                extrinsics[:, :3, 3] += origin_offset @ extrinsics[:,:3,:3].transpose(0,2,1)   # Transform the center of the system to 0,0,0
                np.savez(os.path.join(os.path.split(calib_path)[0], 'cameras.npz'), intrinsics=intrinsics, extrinsics=extrinsics)
                save_cams_path = os.path.join(os.path.split(calib_path)[0], 'cams')
                os.makedirs(save_cams_path, exist_ok=True)
                self.save_camera_parameters(save_cams_path, intrinsics, extrinsics)


            elif calib_path.split('.')[-1] == 'mat':    # matlab calibration .mat
                print(f'calib_path: {calib_path}')
                camera_params = load_camera_params_mat(calib_path)
                intrinsics = camera_params['K']     # (n, 3, 3)
                extrinsics = np.tile(np.eye(4), (len(intrinsics), 1, 1))    # (n, 4, 4)
                
                extrinsics[:, :3, :3] = camera_params['R'] @ np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
                extrinsics[:, :3, 3] = camera_params['T']
                extrinsics[:, :3, 3] += origin_offset @ extrinsics[:,:3,:3].transpose(0,2,1)   # Transform the center of the system to 0,0,0


        self.camera_params = {
            'K': intrinsics[:, :3, :4],
            'R': extrinsics[:, :3, :3],
            'T': extrinsics[:, :3, 3]
        }


    def save_camera_parameters(self, save_cams_path, intrinsics, extrinsics):
        for i, (K, E) in enumerate(zip(intrinsics, extrinsics)):
            filename = f"{save_cams_path}/{i:08d}_cam.txt"
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
    image_size = (1984,1984)
    c = CameraReconstructor('path_to_calibration_file.xml', origin_offset, image_size)