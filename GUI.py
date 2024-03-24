# Trying to make the app work

import customtkinter as tk
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Delaunay
from PIL import Image, ImageDraw
from typing import Callable, Optional
from enum import Enum

# Enumerated class for our distribution options
class Distribution(Enum):
    RANDOM = 0
    UNIFORM = 1
    CENTERED = 2

# Functions:
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

def generate_points(img, num_points, distribution):
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
        
        x_vals = np.random.normal(img_width/2, img_width/4, num_points)
        x_list = x_vals.tolist()

        y_vals = np.random.normal(img_height/2, img_height/4, num_points)
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
    
def del_triangulation(points):
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

def GUI_event_handler(image: Image, num_points_entry: tk.CTkEntry, distribution_dropdown: tk.CTkOptionMenu) -> Callable[[], None]:
    """
    Handles the generate button function.
    """
    def event():
        num_points = int(num_points_entry.get())
        dis_type = distribution_dropdown.get()
        if dis_type == "Random":
            dis_type = 0
        elif dis_type == "Uniform":
            dis_type = 1
        elif dis_type == "Centered":
            dis_type = 2
        
        points = generate_points(image, num_points, dis_type)
        triang = del_triangulation(points)
        art = draw_triangulation(image, triang, points)
        # Set the image in the GUI
        art_img.configure(light_image=art, dark_image=art)
    
    return event



# GUI
# Creating the top-level frames
main = tk.CTk()
img_frame = tk.CTkFrame(main)
options_frame= tk.CTkFrame(main)
bottom_frame = tk.CTkFrame(main)

# Packing them
img_frame.pack(side="top")
options_frame.pack(side="top")
bottom_frame.pack(side="top")

# Getting the image to create the app
image = Image.open("starry_night.jpg")
img_width, img_height = image.size

# Creating the widgets and packing
orig_img = tk.CTkImage(light_image= image, dark_image= image, size=(300, 300))
art_img = tk.CTkImage(light_image= image, dark_image= image, size=(300, 300))
art_img_lab = tk.CTkLabel(img_frame, text="", image=art_img)
orig_img_lab = tk.CTkLabel(img_frame, text="", image=orig_img)

orig_img_lab.pack(side="left")
art_img_lab.pack(side="left")

# More widgets and packing
num_points_lab = tk.CTkLabel(options_frame, text="Number of Points:")
num_points_entry = tk.CTkEntry(options_frame)
distribution_dropdown = tk.CTkOptionMenu(options_frame, values= ["Random", "Uniform", "Centered"])
num_points_entry.insert(0, 1000) # Putting a default value so that app starts with a triangulated image
generate_button = tk.CTkButton(bottom_frame, text="Generate Image", command=GUI_event_handler(image, num_points_entry, distribution_dropdown))

num_points_lab.pack(side="left")
num_points_entry.pack(side="left")
distribution_dropdown.pack(side="left")
generate_button.pack(side="top")

# Starting the mainloop
main.mainloop()