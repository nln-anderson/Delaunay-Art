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
class Model:
    # No Instance vars

    # Methods:
    def draw_triangulation(self, img: Image, triangulation: Delaunay, points: np.ndarray) -> Image:
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

    def generate_points(self, img: Image, num_points: int, distribution: Distribution) -> np.ndarray:
        """
        This function generates an array of random or uniform coordinates within the image.

        PARAMETERS:
        num_points (integer) - the number of points in the pointset
        distribution (integer, 0 or 1) - 0 creates a random distribution and 1 creates a uniform distribution
        img (image) - the image that the pointset must fit within

        OUTPUT:
        points (np.ndarray) - 2D array that contains the points for our triangulation
        """

        img_width, img_height = img.size
        # Generate points within the image boundaries
            # Random first
        if distribution == Distribution.RANDOM:
            # This will generate random numbers between 0 and 1 in a pair, then multiply by the array to fit the image
            points = np.random.rand(num_points, 2) * np.array([img_width, img_height])
            
        
            # Then the uniform distribution
        if distribution == Distribution.UNIFORM:
            points = []
            for x in range(1, img_width+1, int(img_width/(np.sqrt(num_points)))):
                for y in range(1, img_height+1, int(img_height/(np.sqrt(num_points)))):
                    points.append([x,y])
            points = np.array(points)

            # Distribution centered at the origin
        if distribution == Distribution.CENTERED:
            
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
        
    def del_triangulation(self, points: np.ndarray) -> Delaunay:
        """
        Performs the triangulation on the pointset.

        PARAMETERS:
        points (array) - array with all the points

        OUTPUT:
        del_triangulation (Denaunay) - the triangulation of Delaunay type
        """
        # Perform Delaunay triangulation
        del_triangulation = Delaunay(points)
        return del_triangulation

"Tests for Model ----------------------------------------------"
# image = Image.open("starry_night.jpg")
# m = Model()
# points = m.generate_points(image, 1000, Distribution.RANDOM)
# triang = m.del_triangulation(points)
# art = m.draw_triangulation(image,triang,points)
# plt.imshow(art)
# plt.show()

class View(tk.CTkFrame):
    """View class for the app. Handles the widgets
    """

    # Instance vars (need to be able to access these in the controller)
    orig_img: tk.CTkImage
    art_img: tk.CTkImage
    num_points_entry: tk.CTkEntry
    distribution_dropdown: tk.CTkOptionMenu
    generate_button: tk.CTkButton

    model: Model
    
    def __init__(self, parent: tk.CTkFrame, model: Model) -> None:
        super().__init__(parent)
        self.model = model
        self.create_layout()

    # Methods:
    def create_layout(self) -> None:
        """Creaes the GUI layout
        """
        # First create the top level frams
        img_frame = tk.CTkFrame(self)
        options_frame= tk.CTkFrame(self)
        bottom_frame = tk.CTkFrame(self)

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
        generate_button = tk.CTkButton(bottom_frame, text="Generate Image")

        num_points_lab.pack(side="left")
        num_points_entry.pack(side="left")
        distribution_dropdown.pack(side="left")
        generate_button.pack(side="top")

        # Assigning the instance vars
        self.orig_img = orig_img
        self.art_img = art_img
        self.num_points_entry = num_points_entry
        self.distribution_dropdown = distribution_dropdown
        self.generate_button = generate_button

class Controller:
    """Controller that connects the View and Model. Handles operations between the two
    """
    # Instance Vars
    model: Model
    view: View

    def __init__(self, model: Model, view: View) -> None:
        self.model = model
        self.view = view
        self.set_generate()

    # Methods
    def set_generate(self):
        """Sets the command of the generate button
        """
        self.view.generate_button.configure(command= self.update_art)

    def update_art(self):
        """Generates the art and updates the GUI to display it.
        """
        # Gather the inputs from GUI
        num_points = int(self.view.num_points_entry.get())
        dis = self.view.distribution_dropdown.get()
        if dis == "Random":
            dis = Distribution.RANDOM
        elif dis == "Uniform":
            dis = Distribution.UNIFORM
        else:
            dis = Distribution.CENTERED
        
        # Create the art image
        points = self.model.generate_points(Image.open("starry_night.jpg"), num_points, dis)
        triang = self.model.del_triangulation(points)
        art = self.model.draw_triangulation(Image.open("starry_night.jpg"),triang, points)

        # Update the GUI
        self.view.art_img.configure(light_image = art, dark_image = art)

def main():
    """Connects the MVC to run the app
    """
    # Create the window for the app
    window = tk.CTk()
    window.title("Delaunay Art Generator")

    # Create the MVC
    m = Model()
    v = View(window, m)
    c = Controller(m, v)

    # Pack the view
    v.pack(side="top")

    window.mainloop()

main()
