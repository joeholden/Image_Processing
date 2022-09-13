import nd2
import numpy as np
from skimage import io
import os


def nd2_tif(raw_nd2_path, output_directory=None):
    """Provide input as a raw string path to .nd2 file.
    If not output directory is provided, the image will be saved in the root directory of this script.
    Provide Output directory as a raw string"""
    ND2_PATH_RAW = raw_nd2_path
    tif_filename = ND2_PATH_RAW.replace('\\', '/').split('/')[-1].replace('.nd2', '.tiff')
    image_array = nd2.imread(ND2_PATH_RAW)
    if output_directory != None:
        io.imsave(os.path.join(output_directory, tif_filename), image_array.astype(np.uint16))
    else:
        io.imsave(tif_filename, image_array.astype(np.uint16))


def batch_convert_nd2_tif(path_parent_dir):
    """Creates a folder holding .tif conversions of all the .nd2 files in a given directory.
    Provide the path as a raw string that of course does not end in a backslash"""
    path_parent_dir = path_parent_dir.replace('\\', '/')
    output_dir = os.path.join(path_parent_dir, 'converted_tifs')
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    for root, dirs, files in os.walk(path_parent_dir):
        for file in files:
            if file.endswith('.nd2'):
                nd2_tif(os.path.join(root, file), output_directory=output_dir)


# batch_convert_nd2_tif(r'C:\Users\joema\PycharmProjects\e phys plot')
nd2_tif(r'C:\Users\joema\PycharmProjects\e phys plot\2022-03-17_c1.nd2', output_directory=r'C:\Users\joema\PycharmProjects\e phys plot')