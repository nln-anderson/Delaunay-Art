# Delaunay Art Generator version 3
# Added center distribution (still has errors)

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from PIL import Image, ImageDraw
from typing import Optional

def draw_triangulation(img: Image, triangulation: Delaunay, points: np.ndarray) -> Image:
    """
    This function draws the art given an image and triangulation.

    PARAMETERS:
    img (image) - the original image
    triangulation (Delanay object) - the object that contains the information of the triangulation
    points (array) - 2D array with the generated coordinates for the triangulation


    OUTPUT:
    triangulation art (image) - the picture with the art
    """

    img_width, img_height = img.size
    # Create a blank canvas for our art
    triangulation_art = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(triangulation_art)

    for simplex in triangulation.simplices:

        # Gather the vertices of the triangle
        triangle = []
        for i in simplex:
            triangle.append(tuple(points[i]))

             # Calculate the average color of the triangles
        red_channel = []
        green_channel = []
        blue_channel = []
        for pixel in triangle:
            red_channel.append(img.getpixel(pixel)[0])
            green_channel.append(img.getpixel(pixel)[1])
            blue_channel.append(img.getpixel(pixel)[2])

        # Calculate the mean for each channel
        avg_red = int(np.mean(red_channel))
        avg_green = int(np.mean(green_channel))
        avg_blue = int(np.mean(blue_channel))

        # Create a tuple with the average values for each channel
        avg_color = (avg_red, avg_green, avg_blue)

        # Fill the triangle with the average color
        draw.polygon(triangle, avg_color)

    return triangulation_art

def generate_points(img: Image, num_points: int, distribution: int) -> np.ndarray:
    """
    This function generates an array of random or uniform coordinates within the image.

    PARAMETERS:
    num_points (integer) - the number of points in the pointset
    distribution (integer, 0 or 1) - 0 creates a random distribution and 1 creates a uniform distribution
    img (image) - the image that the pointset must fit within

    OUTPUT:
    points (array) - 2D array that contains the points for our triangulation
    """

    img_width, img_height = img.size
    # Generate points within the image boundaries
        # Random first
    if distribution == 0:
        # This will generate random numbers between 0 and 1 in a pair, then multiply by the array to fit the image
        points = np.random.rand(num_points, 2) * np.array([img_width, img_height])
        
    
        # Then the uniform distribution
    if distribution == 1:
        points = []
        for x in range(1, img_width+1, int(img_width/(np.sqrt(num_points)))):
            for y in range(1, img_height+1, int(img_height/(np.sqrt(num_points)))):
                points.append([x,y])
        points = np.array(points)

        # Distribution centered at the origin
    if distribution == 2:
        
        x_vals = np.random.normal(img_width/2, img_width/8, num_points)
        x_list = x_vals.tolist()

        y_vals = np.random.normal(img_height/2, img_height/8, num_points)
        y_list = y_vals.tolist()
       
        
        # Combine the x any y
        coordinate_list = []
        for num in range(len(x_list)):
            x = x_list[num]
            y = y_list[num]
            coordinate_list.append([x,y])

        # Remove points that aren't in the image boundaries
        for item in coordinate_list:
            if item[0] >= img_width or item[0] <= 0:
                coordinate_list.remove(item)
            elif item[1] >= img_height or item[1] <= 0:
                coordinate_list.remove(item)


        points = np.array(coordinate_list)

    # Ensure the corners have points to prevent weird borders
    corner_points = [[1,1], [img_width-1, 1], [1, img_height-1], [img_width-1, img_height-1]]
    corner_points_arrary = np.array(corner_points)
    points = np.append(points, corner_points_arrary, axis=0)
    # corner_points = np.vstack(corner_points)

    return points
    
def del_triangulation(points: np.ndarray) -> Delaunay:
    """
    Performs the triangulation on the pointset.

    PARAMETERS:
    points (array) - array with all the points

    OUTPUT:
    del_triangulation - the triangulation
    """
    # Perform Delaunay triangulation
    del_triangulation = Delaunay(points)
    return del_triangulation

# This function doesn't function as of now
def FSdel_triangulation(points):
    """
    Similar to del_triangulation, except it performs the furthest-site delaunay triangulation.

    PARAMETERS:
    points (array) - array containing all of the points

    OUTPUT:
    FSdel_triangulation - the triangulation
    """
    # Perform Delanay triangulation with furthest point turned on
    FSdel_triangulation = Delaunay(points, furthest_site=True)
    print(points)
    return FSdel_triangulation

def display_results(img: Image, del_triangulation_art: Image) -> None:
    """
    Displays the images side by side.
    """
    # Display the two images side by side
    plt.subplot(1, 2, 1)
    plt.imshow(img)
    plt.title("Original Image")

    plt.subplot(1, 2, 2)
    plt.imshow(del_triangulation_art)
    plt.title("Delaunay Triangulation Art")

    #plt.subplot(1, 3, 3)
    #plt.imshow(FSdel_triangulation_art)
   # plt.title("Furthest-Site Delaunay Triangulation Art")

    plt.show()

# Work in progress function
def error(img1: Image, img2: Image):
    """
    Calculates the error between two images.

    PARAMETERS:
    img1 (image) - first image
    img2 (image) - first image
    """
    img1_pixels = []
    for pixel in img1:
        img1_pixels.append(pixel.getpixel())

def main() -> None:
    img_name = input("Enter the name of the image to be triangualted: ")

    # Get image path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, img_name)

    # Load the image
    img = Image.open(image_path)
    img_width, img_height = img.size

    num_points = int(input("How many points would you like to use: "))

    distribution = int(input("Random distrubution (0) or uniform distribution (1) or centered distribution (2): "))
    
    points = generate_points(img, num_points, distribution)

    del_triangulation_art = draw_triangulation(img, del_triangulation(points), points)

    # FSdel_triangulation_art = draw_triangulation(img, FSdel_triangulation(points), points)

    display_results(img, del_triangulation_art)

    save = input("Would you like to save the image ('yes' or 'no'): ")

    if save == 'yes':

        # Save the image in the project folder
        output_path = os.path.join(script_dir, f"{img_name}, {num_points} points, distribution type {distribution}.png")
        del_triangulation_art.save(output_path)
        print("Result saved at:" + str(output_path))

main()