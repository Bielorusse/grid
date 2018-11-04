"""
main script for grid layout of erdorbit.

version of the 20180815.

optional arguments:
  -h, --help      show this help message and exit
  -config CONFIG  custom configuration file
"""

import numpy as np
import framemod
import scmod
import pygame
import pygame.locals
from OpenGL.GL import *
from OpenGL.GLU import *
import argparse
from datetime import datetime
import os
import inspect
import gridmod

def read_config(config_file, config_dict):
    """
    Read config file and store parameters in dictionnary.

    Input:
    -config_file    string
    -config_dict     dictionnary
    """

    with open(config_file, "r") as file:

        file_contents = file.readlines()

    for line in file_contents:

        if not line.startswith("#"):

            param = line.split("=")[0].split()[0]

            value = line.split("=")[1].split()[0]

            config_dict[param] = value

    return config_dict

def write_txt_file(a, e, i, raan, om, s, dur, shift_ranges):
    """
    Writes txt file containing parameters.
    Input:
    -a              float
    -e              float
    -i              float
    -raan           float
    -om             float
    -step           float
    -dur            float
    -shif_ranges    dict
    """

    if not os.path.isdir("output"):

        os.mkdir("output")

    with open("output/" + datetime.now().strftime("%Y%m%d-%H%M") + "-info.txt", "w") as file:

        file.write("ships version 1.1 \n\n")

        file.write("time parameters: \n")
        file.write(
        "step (s)   {}\n".format(step)
        + "dur  (s)   {}\n".format(dur)
        )

        file.write("\norbital parameters: \n")
        file.write(
        "a    (km)  {}\n".format(a)
        + "e    (-)   {}\n".format(e)
        + "i    (deg) {}\n".format(i)
        + "raan (deg) {}\n".format(raan)
        + "om   (deg) {}\n".format(om)
        )

        file.write("\nshift: \n")

        for key in shift_ranges:

            file.write("{:5s}".format(key))

            for value in shift_ranges[key][:-1]:

                file.write("{},".format(value))

            file.write("{}\n".format(shift_ranges[key][-1]))

def display_curve(list_of_vertices, output_dir):
    """
    Display a curve.

    Input:
    -list_of_vertices   list of tuples of floats
    -output_dir         string
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

        for i in range(len(list_of_vertices) - 1):

            framemod.draw_line(list_of_vertices[i:i+2])

        pygame.display.flip()

        pygame.image.save(pygame.display.get_surface(), image_name)

if __name__ == "__main__":

    if os.path.dirname(inspect.getfile(inspect.currentframe())) == "":
        output_dir = "output"
    else:
        output_dir = os.path.dirname(inspect.getfile(inspect.currentframe())) + "/output"

    parser = argparse.ArgumentParser("Orbital animations.")
    parser.add_argument("-config", help="custom configuration file")
    args = parser.parse_args()

    if os.path.dirname(inspect.getfile(inspect.currentframe())) == "":
        config_default_file = "config_default.txt"
    else:
        config_default_file = os.path.dirname(inspect.getfile(inspect.currentframe())) \
            + "/config_default.txt"

    config = read_config(config_default_file, {})

    if args.config != None:
        config = read_config(args.config, config)

    grid_size = float(config["grid_size"])

    a = float(config["a"])
    e = float(config["e"])
    inc = float(config["inc"])
    raan = float(config["raan"])
    om = float(config["om"])

    MU_PLANET = float(config["mu_planet"])
    PLANET_ROT = float(config["planet_rot"])

    step = float(config["step"])
    dur = float(config["dur"])

    time_list = np.arange(0, dur, step)

    ship = scmod.Ship([a, e, inc, raan, om], len(time_list))

    for i in range(len(time_list)):

        ship.vertices[i, 0] = time_list[i]

        ship.vertices[i, 1:] = scmod.rotate_frame_around_y(
            ship.scale * scmod.from_orbital_to_cartesian_coordinates(
                ship.orbital_parameters[0],
                ship.orbital_parameters[1],
                ship.orbital_parameters[2],
                ship.orbital_parameters[3],
                ship.orbital_parameters[4],
                ship.vertices[i, 0],
                MU_PLANET
            ),
            PLANET_ROT * time_list[i]
        )

    ship.vertices[:, 1:] = scmod.rescale_to_cube(ship.vertices[:, 1:], grid_size)

    grid = gridmod.Grid(9, 9, grid_size)

    for row in range(grid.rows):
        for col in range(grid.cols):

            grid.plots[row][col].alpha = (row-grid.rows//2) * 15
            grid.plots[row][col].beta = -(col-grid.rows//2) * 15 + 25

    grid.set_grid_vertices(ship.vertices[:, 1:])

    framemod.initiate_pygame_frame()

    grid.display(output_dir)

    # display_curve(ship.vertices[:, 1:], output_dir)
