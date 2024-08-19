# Welcome to the workflow, if you see ##ADJUST TO YOUR NOTEBOOK VALUES you need to adjust the line below with the values you changed in the jupyter notebook. 
# Import necessary packages
from plantcv import plantcv as pcv
import os
# Import the necessary tools to parallelize the workflow, which will allow you to next run all of the images in the set. 
from plantcv.parallel import workflow_inputs

# Set input variables
args = workflow_inputs()

# Set variables
pcv.params.debug = args.debug     # Replace the hard-coded debug with the debug flag

# Import an image from the file. This should stay the same, do not change it from your notebook! 
# Inputs:
#   filename - Image file to be read in (here we have specified "args.image" for the filepath)
#   mode - Return mode of image; either 'native' (default), 'rgb', 'gray', or 'csv'. If your image is not "native" or you want to specify the image type, change the code below.
img, path, filename = pcv.readimage(filename=args.image1)
filename = os.path.split(args.image1)[1]

# Crop image if necessary. This is optiona. 
##ADJUST TO YOUR NOTEBOOK VALUES
#   Parameters:
#          img - RGB, grayscale, or hyperspectral image data
#          x - Starting X coordinate
#          y - Starting Y coordinate
#          h - Height
#          w - Width
#   Context:
#        Crops image
#        Allows users to avoid splicing arrays with Python code, although Numpy arrays can be cropped with this method as well.
crop_img = pcv.crop(img=img, x=1300, y=50, h=2500, w=2300)

# If your image is not straight, rotate it without changing the dimensions of the image.
#    Parameters:
#        img - RGB or grayscale image data
#        rotation_deg - rotation angle in degrees, can be a negative number, positive values move counter clockwise.
#        crop - if crop is set to True, image will be cropped to original image dimensions, if set to False, the image size will be adjusted to accommodate new image dimensions.
#   Context:
#       Rotates image, sometimes it is necessary to rotate an image, especially when clustering objects.
rotate_img = pcv.transform.rotate(crop_img, 0, False)

# First, detect the color card.
#     Parameters:
#          rgb_img - Input cropped RGB image data containing a color card.
#          label - Optional label parameter, modifies the variable name of observations recorded. (default = pcv.params.sample_label)
#          adaptive_method - Adaptive threhold method. 0 (mean) or 1 (Gaussian) (default = 1).
#          block_size - Size of a pixel neighborhood that is used to calculate a threshold value (default = 51). We suggest using 127 if using adaptive_method=0.
#          radius - Radius of circle to make the color card labeled mask (default = 20).
#          min_size - Minimum chip size for filtering objects after edge detection (default = 1000)
#     Returns:
#          labeled_mask - Labeled color card mask
card_mask = pcv.transform.detect_color_card(rgb_img=crop_img, radius=10, adaptive_method=1, block_size=101)

# Make a color card mask for your image. You should see that the color card has little circles on it, nicely inside the color squares.
##ADJUST TO YOUR NOTEBOOK VALUES if you changed the radius, nrows, or ncols
# Make a color card matrix 
#   Parameters:
#       rgb_img - RGB image with color chips visualized, in this case 'rotate_img'
#       mask - a gray-scale img with unique values for each segmented space, representing unique, discrete color chips. card_mask created with pcv.transform.detect_color_card

#   Returns:
#      color_matrix - a n x 4 matrix containing the average red value, average green value, and average blue value for each color chip.
#      headers - a list of 4 headers corresponding to the 4 columns of color_matrix respectively
headers, card_matrix = pcv.transform.get_color_matrix(rgb_img=rotate_img, mask=card_mask)

# Define the standard color card matrix:adjust to your notebook value for pos
std_color_matrix = pcv.transform.std_color_matrix(pos=3)

# Color correct your image to the standard values using the affine function
#        Parameters:
#             rgb_img - an RGB image with color chips visualized
#             source_matrix - array of RGB color values (intensity in the range [0-1]) from the image to be corrected where each row is one color reference and the columns are organized as index,R,G,B; created with plantcv.transform.get_color_matrix.
#             target_matrix - array of target RGB color values (intensity in the range [0-1]) where each row is one color reference and the columns are organized as index,R,G,B; created with plantcv.transform.std_color_matrix.

#        Returns:
#           img_cc - corrected image
img_cc = pcv.transform.affine_color_correction(rgb_img=rotate_img, source_matrix=card_matrix, 
                                               target_matrix=std_color_matrix)


# Thresholding two channels at one time to separate plant from the background
##ADJUST TO YOUR NOTEBOOK VALUES
#    Parameters:
#         rgb_img - Corrected RGB image
#         x_channel - Channel to use for the horizontal coordinate. Options: 'R', 'G', 'B', 'l', 'a', 'b', 'h', 's', 'v', 'gray', and 'index'
#         y_channel - Channel to use for the vertical coordinate. Options: 'R', 'G', 'B', 'l', 'a', 'b', 'h', 's', 'v', 'gray', and 'index'
#         points - List containing two points as tuples defining the segmenting straight line
#         above - Whether the pixels above the line are given the value of 0 or 255
#   Returns:
#        thresholded/binary image
dual_thresh = pcv.threshold.dual_channels(rgb_img = img_cc, x_channel = "a", y_channel = "b", points = [(80,80),(125,138)], above=True)

# Fill in small objects that are not your plant, such as dirt, stray pixels, etc. Change the fill size if needed to fill smaller or bigger portions.
##ADJUST TO YOUR NOTEBOOK VALUES
#     Parameters:
#           bin_img - Binary image data
#           size - minimum object area size in pixels (integer), smaller objects will be filled
#      Context:
#           Used to reduce image noise
#      Returns:
#           fill_image
mask_fill = pcv.fill(bin_img=dual_thresh, size=50)

# If there are pixels in the plant that are not selected and should be, use the fill holes function to fill in holes in the leaf. 
##ADJUST TO YOUR NOTEBOOK VALUES
#     Parameters:
#          gray_img - Grayscale or binary image data
#          kernel - Optional neighborhood, expressed as an array of 1's and 0's. If None, use cross-shaped structuring element.
#     Context:
#          Used to reduce image noise, specifically small dark spots (i.e. "pepper").
#     Returns:
#        filtered_img
mask_fill_holes = pcv.closing(gray_img=mask_fill) 

# Define the region of interest (ROI) that contains your plant. This should include your plant, but not you color card or other objects
##ADJUST TO YOUR NOTEBOOK VALUES
#       Parameters:
#             img - Corrected RGB or grayscale image to plot the ROI on in debug mode.
#             x - The x-coordinate of the upper left corner of the rectangle.
#             y - The y-coordinate of the upper left corner of the rectangle.
#             h - The height of the rectangle.
#             w - The width of the rectangle.
#      Context:
#          Used to define a region of interest in the image.
#      Returns:
#         roi - region of interest
roi1 = pcv.roi.rectangle(img=img_cc, x=500, y=900, h=1300, w=1400)

# Make a new filtered mask that only keeps the plant in your ROI and not objects outside of the ROI
##ADJUST TO YOUR NOTEBOOK VALUES
#       Parameters:
#            mask = binary image data to be filtered
#            roi = region of interest, an instance of the Objects class, output from one of the pcv.roi
#            roi_type = 'partial' (for partially inside, default), 'cutto', or 'largest' (keep only the largest contour)
#      Context:
#           Used to filter objects within a region of interest and decide which ones to keep.
#      Warning:
#           Using roi_type='largest' will only keep the largest outer connected region of non-zero pixels.
#      Returns:
#           filtered_mask
roi_mask  = pcv.roi.filter(mask=mask_fill_holes, roi=roi1, roi_type='partial')

############### Analysis ################ 

# Find shape properties, data gets stored to an Outputs class automatically
#    Parameters:
#     img - Corrected RGB or grayscale image data for plotting.
#     labeled_mask - Labeled mask of objects (32-bit, output from pcv.roi.filter).
#     n_labels - Total number expected individual objects (default = 1).
#     label - Optional label parameter, modifies the variable name of observations recorded. Can be a prefix or list (default = pcv.params.sample_label).
# Context:
#     Used to output size and shape characteristics of individual objects (labeled regions).
# Returns:
#     analysis_image
shape_image = pcv.analyze.size(img=img_cc, labeled_mask=roi_mask)

# Shape properties relative to user boundary line (optional). This is useful if your plant is hanging below the pot and you want height from the top of the pot.
# Set your line_position by finding the x-value at the top of the pot, hover your cursor to get that value

# Parameters:
#       img - Corrected RGB or grayscale image data for plotting
#       labeled_mask - Labeled mask of objects (32-bit).
#       line_position - position of boundary line (a value of 0 would draw the line through the top of the image)
#       n_labels - Total number expected individual objects (default = 1).
#       label - Optional label parameter, modifies the variable name of observations recorded. Can be a prefix or list (default = pcv.params.sample_label).

# Returns:
#       image with boundary data
##ADJUST TO YOUR NOTEBOOK VALUES
shape_bound_image = pcv.analyze.bound_horizontal(img=img_cc,labeled_mask=roi_mask, 
                                               line_position=2275, label="default")

# Determine color properties: Histograms, Color Slices and Pseudocolored Images, output color analyzed images (optional)
# Parameters:
#      rgb_img - Corrected RGB image data
#      labeled_mask - Labeled mask of objects (32-bit, output from pcv.roi.filter).
#      n_labels - Total number expected individual objects (default = 1).
#      colorspaces - 'all', 'rgb', 'lab', or 'hsv'. This can limit the data saved out (default = 'hsv').
#      label - Optional label parameter, modifies the variable name of observations recorded. Can be a prefix or list (default = pcv.params.sample_label).

# Context:
#     Used to extract color data from RGB, LAB, and HSV color channels.
#     Generates histogram of color channel data.
# Returns:
#     Ridgeline plot of histograms of hue values
color_histogram = pcv.analyze.color(rgb_img=img_cc, labeled_mask=roi_mask, colorspaces='all', label="default")

# The save results function will take the measurements stored when running any PlantCV analysis functions, format, 
# and print an output text file for data analysis. The Outputs class stores data whenever any of the following functions
# are ran: analyze_bound_horizontal, analyze_bound_vertical, analyze_color, analyze_nir_intensity, analyze_object, 
# fluor_fvfm, report_size_marker_area, watershed. If no functions have been run, it will print an empty text file 
pcv.outputs.save_results(filename=args.result)
# Next, save the analysis images for inspection if desired. 
pcv.print_image(shape_image, os.path.join(args.outdir, filename + "_shape.jpg"))
pcv.print_image(shape_bound_image, os.path.join(args.outdir, filename + "_shape-bound.jpg"))

# Clear the measurements stored globally into the Ouptuts class
pcv.outputs.clear()
