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
import logging
import os
from pathlib import Path

import itertools
import numpy as np
from configbuilder.builder.exception import *
from configbuilder.builder.exception.DateValueError import DateValueError
from configbuilder.providers.ww3.WW3Config import WW3Config
from configbuilder.providers.ww3.v516.build import *
from configbuilder.providers.ww3.v516.inp import *
from configbuilder.providers.ww3.v516.inp.BouncFile import BouncFile
from configbuilder.providers.ww3.v516.inp.OunpFile import OunpFile
from netCDF4 import Dataset


class WW3CurviConfig(WW3Config):

    VERSION = "V516"

    def __init__(self,
                 model_source_dir,
                 outputDir,
                 name,
                 symphonie_grid_file,
                 wind_forcing_file,
                 output_points,
                 start_time,
                 end_time,
                 global_time_step,
                 spatial_time_step,
                 spectral_time_step,
                 source_time_step,
                 exported_nested_boundaries=None,
                 initial_mode=0,
                 next_restart_time=None,
                 mpi_lib="openmpi",
                 compiler="gnu",
                 debug_mode=False,
                 obc_forcing_points=None,
                 obc_forcing_dir=None,
                 ):

        WW3Config.__init__(self,
                           model_source_dir,
                           outputDir,
                           name,
                           wind_forcing_file=wind_forcing_file,
                           obc_forcing_points= obc_forcing_points,
                           obc_forcing_dir=obc_forcing_dir,
                           output_points=output_points,
                           exported_nested_boundaries=exported_nested_boundaries,
                           initial_mode=initial_mode,
                           next_restart_time=next_restart_time,
                           compiler=compiler,
                           mpi_lib=mpi_lib
                           );

        # Makefile
        self.makefiles.append(CompFile(os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(), "build"),
                                       WW3Config.NETCDF_INC,
                                       compiler=compiler,
                                       mpi_lib=mpi_lib,
                                       debug_mode=debug_mode))
        self.makefiles.append(LinkFile(os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(), "build"),
                                       WW3Config.NETCDF_LIB,
                                       compiler=compiler,
                                       mpi_lib=mpi_lib))

        self.makefiles.append(SwitchFile(os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(), "build")))

        self.makefiles.append(EnvironnementFile(
            os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(), "build"),
            mpi_lib=mpi_lib,
            model_dir=self.model_dir,tmp_dir=self.tmp_dir))

        # ww3_grid.inp
        nb = GridFile(os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(), "inp"),
                      config_name=self.config_name,
                      global_time_step=global_time_step,
                      spatial_time_step=spatial_time_step,
                      spectral_time_step=spectral_time_step,
                      source_time_step=source_time_step,
                      bathy_dir=self.bathy_dir,
                      obc_forcing_points=self.obc_forcing_points)
        self.inp_files["ww3_grid"] = nb

        # ww3_prnc.inp
        nb = PrncFile(os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(), "inp"))
        self.inp_files["ww3_prnc"] = nb

        nb = BouncFile(
            os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(),
                         "inp"))
        self.inp_files["ww3_bounc"] = nb

        # ww3_shel.inp
        nb = ShelFile(
            os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(), "inp"),
            start_time,
            end_time,
            self.output_points,
            self.exported_nested_boundaries,
            self.wind_forcing_enable
        )
        self.inp_files["ww3_shel"] = nb

        # ww3_ounf.inp
        nb = OunfFile(
            os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(), "inp"),
            start_time,
            end_time)
        self.inp_files["ww3_ounf"] = nb

        # ww3_ounp.inp
        nb = OunpFile(
            os.path.join(WW3Config.BASE_DIR, WW3Config.MODEL.lower(), WW3CurviConfig.VERSION.lower(),
                         "inp"),
            start_time,
            end_time)
        self.inp_files["ww3_ounp"] = nb

        self.symphonie_input_grid_file = symphonie_grid_file

    def make_grid(self):

        if "ww3_grid" not in self.inp_files and "ww3_ounf" not in self.inp_files:
            raise ConfigIntegrityError(WW3Config.MODEL,
                                       "Inp file 'ww3_grid' and 'ww3_ounf' have to be initialized", 1005)

        if self.symphonie_input_grid_file != None:
            if os.path.isfile(self.symphonie_input_grid_file):

                try:
                    ncfile = Dataset(self.symphonie_input_grid_file)

                    logging.info("Making grid")

                    lon = ncfile.variables["longitude_t"]
                    lat = ncfile.variables["latitude_t"]
                    bathy =  np.ma.filled(ncfile.variables["hm_w"],fill_value=np.nan)
                    # SYMPHONIE < v293
                    #mask = np.ma.filled(ncfile.variables["mask_t"][0],fill_value=np.nan)
                    # SYMPHONIE >= v293
                    mask = np.ma.filled(ncfile.variables["mask_t"], fill_value=np.nan)

                    x_size = np.shape(lon)[1]
                    y_size = np.shape(lon)[0]

                    # On cherche les indices des points de frontières ouvertes
                    # nb_points = len(self.obc_forcing_points[0]);
                    # if nb_points > 0:
                    #     logging.info("Searching indexes of boundary input points")
                    #     dist = np.zeros([nb_points,y_size,
                    #                      x_size])
                    #     dist[:] = 10000000
                    #     for j,i,index_point in itertools.product(range(0, y_size), range(0, x_size), range(0, nb_points)):
                    #         dist[index_point,j, i] = distance_on_unit_sphere(self.obc_forcing_points[index_point][1], self.obc_forcing_points[index_point][0], lon[j, i],
                    #                                                      lat[j, i])
                    #
                    #     for index_point in range(0, nb_points):
                    #         self.obc_forcing_points[index_point][2], self.obc_forcing_points[index_point][3] = np.where(
                    #             dist[index_point] == np.min(dist[index_point]))

                    lon_file = open(os.path.join(self.bathy_dir, "longitude.dat"), "w")
                    lat_file = open(os.path.join(self.bathy_dir, "latitude.dat"), "w")
                    bathy_file = open(os.path.join(self.bathy_dir, "bathy.dat"), "w")
                    mask_file = open(os.path.join(self.bathy_dir, "mask.dat"), "w")
                    logging.debug("Writing grid files")
                    for j, i in itertools.product(range(0, y_size), range(0, x_size)):
                        lon_file.write(str(lon[j, i]) + "\n")
                        lat_file.write(str(lat[j, i]) + "\n")
                        bathy_file.write(str(bathy[j, i]) + "\n")

                        #if nb_points > 0 and bathy[j, i] > 0 and [j, i] in self.obc_forcing_points[:,2:4]:
                        if i ==0 and int(mask[j, i]) == 1 :
                            # It is a boundary input point
                            mask_file.write(str(int(2)) + "\n")
                        elif mask[j, i] == bathy[j, i] < 0:
                            # It is a wet land
                            mask_file.write(str(int(16)) + "\n")
                        else:
                            mask_file.write(str(int(mask[j, i])) + "\n")
                    lon_file.close()
                    lat_file.close()
                    bathy_file.close()
                    mask_file.close()
                    ncfile.close()

                    self.inp_files["ww3_grid"].set_x_size(x_size)
                    self.inp_files["ww3_grid"].set_y_size(y_size)
                    self.inp_files["ww3_grid"].generate(self.config_dir)

                    self.inp_files["ww3_ounf"].set_x_size(x_size)
                    self.inp_files["ww3_ounf"].set_y_size(y_size)
                    self.inp_files["ww3_ounf"].generate(self.config_dir)

                except OSError as ex:
                    logging.debug("'" + str(self.symphonie_input_grid_file) + "' is not a NetCDF file :" + str(ex))

            else:
                raise FileError("GridFile",
                                "SYMPHONIE grid file '" + str(self.symphonie_input_grid_file) + "' doesn't exist", 1005)

        WW3Config.make_grid(self)



















