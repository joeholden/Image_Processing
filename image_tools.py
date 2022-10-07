import nd2
import numpy as np
from skimage import io
import tifffile as tifi
import cv2
from pathlib import Path
import os
from pprint import pprint
import roifile
import matplotlib as mpl


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

                
def get_nd2_metadata(path_to_nd2, metadata=False, experiment=False, text_info=False,
                     custom_data=False, attributes=False):
    with nd2.ND2File(path_to_nd2) as f:
        if metadata:
            pprint(f.metadata)
        if experiment:
            pprint(f.experiment)
        if text_info:
            pprint(f.text_info)
        if custom_data:
            pprint(f.custom_data)
        if attributes:
            pprint(f.attributes)
    
    
def downsize_large_tif(image_path, scale_factor, save_full_size=False, output_directory=None):
    """Accepts a raw string for the image path and accepts .nd2 or .tif paths
    If you want to scale down the image, provide a scale factor. For example sf of 2 decreases each dimension by 2,
     so decreases area by a factor of 4."""
    # Set up necessary folder and filename variables
    slash_corrected_path = image_path.replace('\\', '/')
    filename = Path(slash_corrected_path).stem
    if not os.path.exists(filename):
        os.mkdir(filename)

    # If the filetype is .nd2, make it a tiff and save the path of the tif. If the path is to a tiff already,
    # point to it.
    if slash_corrected_path.endswith('nd2'):
        nd2_tif(image_path, output_directory=Path(slash_corrected_path).stem)
        tif_path = os.path.join(Path(slash_corrected_path).stem, filename + '.tiff')
    else:
        tif_path = slash_corrected_path

    # Read in the tif. If the files are too large, cv2 cannot open them. Use Tifffile instead
    img = tifi.imread(tif_path)
    img_dims = img.shape
    page_count = img_dims[0]  # check how channels vs pages are stored in array
    pixel_dims = (img_dims[1], img_dims[2])
    scaled_dims = tuple(int(round(i / scale_factor, 0)) for i in pixel_dims)

    # For each page in tiff, save each page separately. Both full size and scaled.
    for i in range(page_count):
        page = img[i]
        if save_full_size:
            cv2.imwrite(f'{filename}/original_scale_page {i}.png', page)
        resized_page = cv2.resize(page, scaled_dims)
        cv2.imwrite(f'{filename}/scaled_{scale_factor}_page_{i}.png', resized_page)  
        

def get_roi_pixels(roi_path):
    """Returns a list of pixel points that lie within a polygon ROI. Be sure to reference these points
    in opencv as reversed. They are saved (i, j) but referencing a pixel in opencv would be image[j, i]"""
    roi = roifile.ImagejRoi.fromfile(roi_path)
    # rectangle bounds
    x_bounds = (min([i[0] for i in roi.coordinates()]), max([i[0] for i in roi.coordinates()]))
    y_bounds = (min([i[1] for i in roi.coordinates()]), max([i[1] for i in roi.coordinates()]))

    px_inside = []
    path = mpl.path.Path(roi.coordinates())
    for i in range(x_bounds[0], x_bounds[1]):
        for j in range(y_bounds[0], y_bounds[1]):
            inside_test = path.contains_point((i, j), transform=None, radius=0.0)
            if inside_test:
                px_inside.append((i, j))
    return px_inside        
