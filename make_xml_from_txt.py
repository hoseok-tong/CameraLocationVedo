import os
import numpy as np
import xml.etree.ElementTree as ET

def read_camera_parameters(filename):
    """
    Reads camera parameters from a text file.

    Parameters:
    filename (str): Path to the text file.

    Returns:
    tuple: Intrinsics and extrinsics matrices.
    """
    with open(filename) as f:
        lines = f.readlines()
        lines = [line.rstrip() for line in lines]

    extrinsics = np.fromstring(' '.join(lines[1:5]), dtype=np.float32, sep=' ').reshape((4, 4))
    intrinsics = np.fromstring(' '.join(lines[7:10]), dtype=np.float32, sep=' ').reshape((3, 3))
    return intrinsics, extrinsics

def write_camera_parameters_to_xml(camera_parameters, output_file, width, height):
    """
    Writes camera parameters to an XML file.

    Parameters:
    camera_parameters (list): List of dictionaries containing camera parameters.
    output_file (str): Path to the output XML file.
    """
    root = ET.Element("document", version="2.0.0")

    chunk = ET.SubElement(root, "chunk", label="Chunk 1", enabled="true")

    sensors = ET.SubElement(chunk, "sensors", next_id=str(len(camera_parameters)))
    cameras = ET.SubElement(chunk, "cameras", next_id=str(len(camera_parameters)), next_group_id="0")

    for idx, params in enumerate(camera_parameters):
        sensor = ET.SubElement(sensors, "sensor", id=str(idx), label="unknown", type="frame")
        ET.SubElement(sensor, "resolution", width=str(width), height=str(height))
        ET.SubElement(sensor, "property", name="layer_index", value="0")
        bands = ET.SubElement(sensor, "bands")
        for band in ["Red", "Green", "Blue"]:
            ET.SubElement(bands, "band", label=band)
        ET.SubElement(sensor, "data_type").text = "float32"
        calibration = ET.SubElement(sensor, "calibration", attrib={"type": "frame", "class": "adjusted"})
        ET.SubElement(calibration, "resolution", width=str(width), height=str(height))
        ET.SubElement(calibration, "f").text = str(params["intrinsic"][0, 0])
        ET.SubElement(calibration, "cx").text = str(params["intrinsic"][0, 2] - 992.0)  # Metashape has pixel coord (0,0) on image center
        ET.SubElement(calibration, "cy").text = str(params["intrinsic"][1, 2] - 992.0)  # Metashape has pixel coord (0,0) on image center

        camera = ET.SubElement(cameras, "camera", id=str(idx), sensor_id=str(idx), component_id="0", label=f"{idx:08d}")    # deal with image naming
        # camera = ET.SubElement(cameras, "camera", id=str(idx), sensor_id=str(idx), component_id="0", label=f"00_{idx:06d}")   # deal with image naming
        transform = ET.SubElement(camera, "transform")
        extrinsic = params["extrinsic"]
        extrinsic[:3,3] = - extrinsic[:3,:3].transpose() @ extrinsic[:3,3]
        extrinsic[:3,:3] = extrinsic[:3,:3].transpose()
        transform.text = ' '.join(map(str, extrinsic.flatten()))

    # Add dummy components section
    components = ET.SubElement(chunk, "components", next_id="1", active_id="0")
    component = ET.SubElement(components, "component", id="0", label="Component 1")
    partition = ET.SubElement(component, "partition")
    ET.SubElement(partition, "camera_ids").text = ' '.join(str(i) for i in range(len(camera_parameters)))

    tree = ET.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def main(txt_folder, output_xml):
    camera_parameters = []
    txt_files = sorted([f for f in os.listdir(txt_folder) if f.endswith('_cam.txt')])

    for txt_file in txt_files:
        intrinsic, extrinsic = read_camera_parameters(os.path.join(txt_folder, txt_file))
        camera_parameters.append({"intrinsic": intrinsic, "extrinsic": extrinsic})

    write_camera_parameters_to_xml(camera_parameters, output_xml, width=1984, height=1984)



if __name__ == "__main__":
    txt_folder = "E:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_Face_KHS/Output/cams/frame0005"  # Folder containing the .txt files
    output_xml = "E:/DATA/MDI_Database_1/BYRoad_Studio/20240104/20240104_Face_KHS/Output/cams/frame0005/cameras.xml"  # Output XML file path
    main(txt_folder, output_xml)
