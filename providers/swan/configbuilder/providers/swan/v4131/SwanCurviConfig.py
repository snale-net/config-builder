#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2024 [SNALE - French SAS Company - RCS 951 724 616]
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from __future__ import division, print_function, absolute_import
from configbuilder.providers.swan.SwanConfig import SwanConfig
from configbuilder.builder.ConfigFile import ConfigFile
from configbuilder.providers.swan.v4131.build import *
from configbuilder.builder.exception import *
from configbuilder.providers.swan.v4131.swn import *
from configbuilder.builder.exception.DateValueError import DateValueError
from configbuilder.utils.path import copytree
import numpy as np
from netCDF4 import Dataset
import os
import logging


class SwanCurviConfig(SwanConfig):

    VERSION = "V4131"

    def __init__(self,
                 outputDir,
                 name,
                 symphonie_grid_file,
                 start_time,
                 end_time,
                 global_time_step,
                 wind_forcing_dir=None,
                 obc_forcing_dir=None,
                 initial_mode=0,
                 next_restart_time=None,
                 mpi_lib="intelmpi",
                 compiler="intel",
                 debug_mode=False,
                 ):

        SwanConfig.__init__(self, os.path.join(ConfigFile.BASE_DIR, "configbuilder", SwanConfig.MODEL.lower(), SwanCurviConfig.VERSION.lower(), "model"),
                            outputDir,
                            name,
                            wind_forcing_dir=wind_forcing_dir,
                            obc_forcing_dir=obc_forcing_dir,
                            initial_mode=initial_mode,
                            next_restart_time=next_restart_time);

        # Makefile
        self.makefiles["macro.inc"] = MacrosFile(os.path.join(ConfigFile.BASE_DIR, "configbuilder", SwanConfig.MODEL.lower(), SwanCurviConfig.VERSION.lower(), "build"),
                                                 compiler=compiler,
                                                 mpi_lib=mpi_lib,
                                                 debug_mode=debug_mode)

        # Swn files
        # config.swn
        nb = SwnFile(
            os.path.join(ConfigFile.BASE_DIR, "configbuilder", SwanConfig.MODEL.lower(), SwanCurviConfig.VERSION.lower(), "swn"),
            config_name=self.config_name,
            start_time=start_time,
            end_time=end_time,
            global_time_step=global_time_step,
            bathy_dir=self.bathy_dir)
        self.swn_files["config"] = nb

        self.symphonie_input_grid_file = symphonie_grid_file

    def make_grid(self):

        if "config" not in self.swn_files:
            raise ConfigIntegrityError(SwanConfig.MODEL,
                                       "Swn file 'config' has to be initialized", 1005)

        if self.symphonie_input_grid_file != None:
            if os.path.isfile(self.symphonie_input_grid_file):

                try:
                    ncfile = Dataset(self.symphonie_input_grid_file)

                    logging.info("Making grid")

                    lon = ncfile.variables["longitude_t"]
                    lat = ncfile.variables["latitude_t"]
                    bathy = np.ma.filled(ncfile.variables["hm_w"], fill_value=np.nan)
                    # SYMPHONIE < v293
                    # mask = np.ma.filled(ncfile.variables["mask_t"][0],fill_value=np.nan)
                    # SYMPHONIE >= v293
                    mask = np.ma.filled(ncfile.variables["mask_t"], fill_value=np.nan)

                    x_size = np.shape(lon)[1]
                    y_size = np.shape(lon)[0]

                    file = open(os.path.join(self.bathy_dir, "coords.dat"), "w")
                    file.write("x-coordinate\n")
                    for i in range(0, x_size):
                        for j in range(0, y_size):
                            file.write(str(lon[j, i])+ " ")
                        file.write("\n")

                    file.write("y-coordinate\n")
                    for i in range(0, x_size):
                        for j in range(0, y_size):
                            file.write(str(lat[j, i]) + " ")
                        file.write("\n")
                    file.close()

                    file = open(os.path.join(self.bathy_dir, "bathy.dat"), "w")
                    for i in range(0, x_size):
                        for j in range(0, y_size):
                            file.write(str(bathy[j, i]) + " ")
                        file.write("\n")
                    file.close()

                    file = open(os.path.join(self.bathy_dir, "mask.dat"), "w")
                    for j in range(0, y_size):
                        for i in range(0, x_size):
                            file.write(str(int(mask[j, i])) + "\n")
                    file.close()

                    ncfile.close()

                    self.swn_files["config"].set_x_size(x_size)
                    self.swn_files["config"].set_y_size(y_size)
                    self.swn_files["config"].generate(self.config_dir)

                except OSError as ex:
                    logging.debug("'" + str(self.symphonie_input_grid_file) + "' is not a NetCDF file :" + str(ex))

            else:
                raise FileError("GridFile",
                                "SYMPHONIE grid file '" + str(self.symphonie_input_grid_file) + "' doesn't exist",
                                1005)





















