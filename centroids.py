import cv2
import numpy as np
from skimage.morphology import disk
from skimage.filters import threshold_otsu
from skimage.morphology import closing, opening, remove_small_objects, remove_small_holes
from skimage.measure import label, regionprops

# Load camera parameters
# Assuming camera parameters are stored in a dictionary format in a file 'calibration.npz'
camera_params = np.load('calibration.npz', allow_pickle=True)
camera_matrix = camera_params['mtx']
dist_coeffs = camera_params['dist']

# Read and undistort the image
Ij = cv2.imread('vista_superior.jpeg')
Ioriginal = cv2.undistort(Ij, camera_matrix, dist_coeffs)
#Ioriginal = cv2.resize(Ioriginal, (1200, 700))
#Ioriginal = Ioriginal[350:650, 400:900]

# Display original and undistorted images
# plt.figure()
# plt.subplot(1, 2, 1)
# plt.imshow(cv2.cvtColor(Ij, cv2.COLOR_BGR2RGB))
# plt.title('Original Image')
# plt.subplot(1, 2, 2)
# plt.imshow(cv2.cvtColor(Ioriginal, cv2.COLOR_BGR2RGB))
# plt.title('Undistorted Image')
# plt.show()

# Convert to grayscale
I = cv2.cvtColor(Ioriginal, cv2.COLOR_BGR2GRAY)

# Binarize the image
limiar = threshold_otsu(I)
_, ImagemC = cv2.threshold(I, limiar, 255, cv2.THRESH_BINARY)

# # Invert the image
#ImagemC = np.invert(ImagemC)

# # Morphological opening
ImagemC = closing(ImagemC, disk(6)) 
ImagemC = cv2.medianBlur(ImagemC, 11)
ImagemC = cv2.Canny(ImagemC, 50, 100)
ImagemC = closing(ImagemC, disk(10)) 
#ImagemC = closing(ImagemC, disk(8))
#ImagemC = opening(ImagemC, disk(8))
#ImagemC = cv2.medianBlur(ImagemC, 11)
cv2.imwrite("C.png", ImagemC)
cv2.imshow("", ImagemC)
cv2.waitKey(500)

detected_circles = cv2.HoughCircles(ImagemC,  
                   cv2.HOUGH_GRADIENT, 1, 90, param1 = 100, 
               param2 = 6, minRadius = 17, maxRadius = 22) 

if detected_circles is not None: 
  
    print(len(detected_circles))
    # Convert the circle parameters a, b and r to integers. 
    detected_circles = np.uint16(np.around(detected_circles)) 
  
    for pt in detected_circles[0, :]: 
        a, b, r = pt[0], pt[1], pt[2] 
  
        # Draw the circumference of the circle. 
        cv2.circle(Ioriginal, (a, b), r, (0, 255, 0), 2) 
  
        # Draw a small circle (of radius 1) to show the center. 
        cv2.circle(Ioriginal, (a, b), 1, (0, 0, 255), 3)

cv2.imshow("img", cv2.resize(Ioriginal, (1200, 700)))
cv2.waitKey(500)
cv2.imwrite("furos.png", Ioriginal)

# Label regions
imLabel, N = label(ImagemC, return_num=True)

# Analyze regions
info = []
for region in regionprops(imLabel):
    info.append({
        'area': region.area,
        'centroid': region.centroid,
        'bounding_box': region.bbox,
        'label': region.label
    })

# Calculate the mean area
areas = np.array([region['area'] for region in info])
mean_area = np.mean(areas)

# Filter regions based on area
for region in info:
    if region['area'] > mean_area or region['area'] < mean_area / 3:
        ImagemC[imLabel == region['label']] = 0

# Re-label regions
imLabel, N = label(ImagemC, return_num=True)

# Analyze the new regions
info = []
for region in regionprops(imLabel):
    info.append({
        'area': region.area,
        'centroid': region.centroid,
        'bounding_box': region.bbox
    })

# Display the final image
# plt.figure()
# plt.imshow(ImagemC, cmap='gray')
# plt.title('Final Image')
# plt.show()

# Function to plot bounding boxes
def plot_bbs(image, info, index):
    vmin, vmax, umin, umax = info[index]['bounding_box']
    cv2.rectangle(image, (umin, vmin), (umax, vmax), (0, 255, 0), 2)

# Example usage of plot_bbs function
#plot_bbs(Ioriginal, info, 0)
