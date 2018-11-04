"""
Creates a grid layout to display 3D objects.

Version 0.4 of the 20180815.
"""

import pygame
import pygame.locals
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import framemod
import os
import inspect
import scmod
from datetime import datetime

class Plot:
    """
    Plot
    """

    def __init__(self, center_coords, scale_factor):
        """
        Plot constructor.

        Input:
        -center_coords  tuple of 3 floats
        -scale_factor   float
        """

        self.alpha = 0.0
        self.beta = 0.0
        self.gamma = 0.0
        self.vertices = []
        self.center = center_coords
        self.scale_factor = scale_factor

    def set_plot_vertices(self, list_of_vertices):
        """
        Set vertices to be displayed in the plot.

        Input:
        -list_of_vertices   list of tuples of floats
        """

        vertex = []

        for i in range(len(list_of_vertices)):

            vertex = list_of_vertices[i]

            vertex = scmod.rotate_frame_around_x(vertex, self.alpha)
            vertex = scmod.rotate_frame_around_y(vertex, self.beta)
            vertex = scmod.rotate_frame_around_z(vertex, self.gamma)

            self.vertices.append(np.asarray(vertex) / self.scale_factor + self.center)

class Grid:
    """
    Grid representation of 3D objects.
    """

    def __init__(self, rows, cols, spacing_factor):
        """
        Grid constructor.

        Input:
        -rows               integer
        -cols               integer
        -spacing_factor     float
        """

        self.rows = rows
        self.cols = cols

        scale_factor = max(self.rows, self.cols)

        self.spacing_factor = spacing_factor

        self.plots = []
        for row in range(self.rows):
            self.plots.append([])
            for col in range(self.cols):

                center_coords = (
                    self.spacing_factor * (-self.cols + 2 * col + 1) / scale_factor,
                    self.spacing_factor * (-self.rows + 2 * row + 1) / scale_factor,
                    0
                )

                self.plots[row].append(Plot(center_coords, scale_factor))

    def set_grid_vertices(self, list_of_vertices):
        """
        Set vertices to be displayed in the grid.

        Input:
        -list_of_vertices   list of tuples of floats
        """

        for row in range(self.rows):

            for col in range(self.cols):

                self.plots[row][col].set_plot_vertices(list_of_vertices)

    def display(self, output_dir):
        """
        Display grid and save as image.

        Input:
        -output_dir     string
        """

        folder_name = output_dir + "/temp"
        image_name = output_dir + "/" + datetime.now().strftime("%Y%m%d-%H%M") + "-image.png"

        while True:

            # closing animation window at any event
            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    pygame.quit()

                    quit()

            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            for row in range(self.rows):
                for col in range(self.cols):

                    for i in range(len(self.plots[0][0].vertices) - 1):

                        framemod.draw_line(self.plots[row][col].vertices[i:i+2])

            pygame.display.flip()

            pygame.image.save(pygame.display.get_surface(), image_name)

def display_grid_animation(list_of_grids, save_frames):
    """
    Display grid animation and save frames, video file and gif.

    Input:
    -list_of_grids   list of Grid instances
    -save_frames    boolean
    """

    if not os.path.isdir("output"):
        os.mkdir("output")
    if not os.path.isdir("output/temp"):
        os.mkdir("output/temp")
    output_dir = "output"

    frame_count = 0

    while True:

        # closing animation window at any event
        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()

                quit()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        if frame_count == (len(list_of_grids) - 1):

            if save_frames:

                framemod.image_to_video(output_dir)

                framemod.image_to_gif(output_dir)

                pygame.quit()

                quit()

            else:

                frame_count = 0

                pygame.display.flip()

                pygame.time.wait(10)

        else:

            for row in range(list_of_grids[frame_count].rows):
                for col in range(list_of_grids[frame_count].cols):

                    for i in range(len(list_of_grids[frame_count].plots[0][0].vertices) - 1):

                        framemod.draw_line(list_of_grids[frame_count].plots[row][col].vertices[i:i+2])

            pygame.display.flip()

            if save_frames:

                framemod.save_frame(frame_count, output_dir)

            pygame.time.wait(10)

            frame_count += 1

if __name__ == "__main__":

    framemod.initiate_pygame_frame()

    nb_of_frames = 90

    list_of_grids = []

    for frame in range(nb_of_frames):

        list_of_grids.append(Grid(10, 10))

        for row in range(list_of_grids[-1].rows):
            for col in range(list_of_grids[-1].cols):

                list_of_grids[-1].plots[row][col].alpha = (row + frame) * 2
                list_of_grids[-1].plots[row][col].beta = (-col + frame) * 2

        list_of_grids[-1].set_grid_vertices([
            (0.75, 0.75, 0),
            (-0.75, 0.75, 0),
            (-0.75, -0.75, 0),
            (0.75, -0.75, 0),
            (0.75, 0.75, 0)
        ])

    display_grid_animation(
        list_of_grids,
        True
    )
