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

import stat

from osgeo import ogr

from configbuilder.builder.Configuration import Configuration
from configbuilder.builder.exception import *
from configbuilder.providers.ww3.v516.inp import *
from configbuilder.utils.path import copytree
import logging
import os
from netCDF4 import Dataset
from configbuilder.utils.call import execute
import numpy as np
import glob
from datetime import datetime, timedelta
import re
from configbuilder.utils.path import path_leaf
import shutil


class WW3Config(Configuration):

    MODEL = "WW3"
    NETCDF_INC="-I"+os.environ['INCLUDE'].replace(':', ' -I')
    NETCDF_LIB="-L"+os.environ['LD_LIBRARY_PATH'].replace(':', ' -L')+" -lnetcdf -lnetcdff"

    def __init__(self, base_dir,
                 outputDir,
                 name,
                 output_points,
                 wind_forcing_file=None,
                 obc_forcing_points=None,
                 obc_forcing_dir=None,
                 exported_nested_boundaries=None,
                 initial_mode=0,
                 next_restart_time=None,
                 compiler="gnu",
                 mpi_lib = "openmpi"
                 ):

        Configuration.__init__(self,outputDir,name);

        self.model_dir = os.path.join(self.output_config_dir, "model")
        self.bin_dir = os.path.join(self.output_config_dir, "model", "bin")
        self.exe_dir = os.path.join(self.output_config_dir, "model", "exe")
        self.ftn_dir = os.path.join(self.output_config_dir, "model", "ftn")
        self.tmp_dir = os.path.join(self.output_config_dir, "model", "tmp")

        self.config_dir = os.path.join(self.output_config_dir, self.config_name)
        self.bathy_dir = os.path.join(self.output_config_dir, self.config_name, "bathy")
        self.wind_forcing_dir = os.path.join(self.output_config_dir, self.config_name, "wind")
        self.obc_forcing_dir = os.path.join(self.output_config_dir, self.config_name, "obc")
        self.graphique_dir = os.path.join(self.output_config_dir, self.config_name, "graphiques")
        self.restart_dir = os.path.join(self.output_config_dir, self.config_name, "restart")

        self.mpi_lib = mpi_lib
        self.compiler = compiler

        self.set_base_config_dir(base_dir)

        # Makefile
        self.makefiles = []

        # Notebook
        self.inp_files = {}

        # Tweaks
        self.tweaks = []

        self.output_points = {}
        self.exported_nested_boundaries = {}

        # Forcings
        self.wind_forcing_enable = False
        self.obc_forcing_enable = False
        self.obc_forcing_points = {}

        # Config
        self.wind_src_forcing_file=wind_forcing_file
        if self.wind_src_forcing_file is not None:
            self.wind_forcing_enable = True

        if obc_forcing_points is not None:
            self.set_obc_forcing_points(obc_forcing_points)

        self.obc_src_forcing_dir=obc_forcing_dir
        if self.obc_src_forcing_dir is not None and len(self.obc_forcing_points[0]) > 0 :
            self.obc_forcing_enable = True
        elif self.obc_src_forcing_dir is None and len(self.obc_forcing_points[0]) > 0 or self.obc_src_forcing_dir is not None and len(self.obc_forcing_points[0]) == 0:
            raise ValueError(WW3Config.MODEL,
                                       "'obc_forcing_points' and 'obc_forcing_dir' have to be initialized", 1005)

        self.set_output_points(output_points)
        self.set_exported_nested_boundaries(exported_nested_boundaries)
        self.set_initial_mode(initial_mode)
        self.set_next_restart_time(next_restart_time)

    def set_wind_forcing_file(self, value):

        if self.wind_forcing_enable:
            if os.path.isfile(value):
                self.clean_wind_forcing_dir()
                shutil.copyfile(value,os.path.join(self.wind_forcing_dir,os.path.basename(value)))
            else:
                raise DirectoryError(WW3Config.MODEL,
                                     "[Wind forcing directory] No such file: '" + value + "'", 1005)

    def set_obc_forcing_dir(self, value):

        if self.obc_forcing_enable:

            if (os.path.isdir(value)):

                if os.listdir(value):
                    self.clean_obc_forcing_dir()
                    copytree(value,self.obc_forcing_dir)
                else:
                    raise DirectoryError(WW3Config.MODEL,
                                         "[OBC forcing directory] '" + value + "' is empty", 1005)
            else:
                raise DirectoryError(WW3Config.MODEL,
                                     "[OBC forcing directory] No such directory: '" + value + "'", 1005)

    def set_obc_forcing_points(self, value):

        if value is not None:
            if os.path.isfile(value):
                try:
                    shp = ogr.Open(value, 0)
                    if shp is None:
                        raise DirectoryError(WW3Config.MODEL,
                                             "[OBC forcing directory] '" + value + "' is empty", 1005)
                    else:
                        count = 0
                        for layer in shp:
                            count += layer.__len__();

                        self.obc_forcing_points = np.zeros(shape=(count, 4))
                        count = 0

                        for layer in shp:
                            fields = [x.GetName() for x in layer.schema]
                            feature = layer.GetNextFeature()

                            while feature is not None:
                                g = feature.geometry()
                                if g.GetGeometryType() == 1:  # point
                                    self.obc_forcing_points[count][0] = float(g.GetPoint_2D(0)[1])
                                    self.obc_forcing_points[count][1] = float(g.GetPoint_2D(0)[0])

                                count += 1;
                                feature = layer.GetNextFeature()

                except Exception as ex:
                    logging.error("'" + str(ex) + "' Unable to read OBC boundaries points")
            else:
                raise DirectoryError(WW3Config.MODEL,
                                     "[OBC boundaries points] No such file: '" + value + "'", 1005)

    def set_exported_nested_boundaries(self, value):

        if value is not None:
            if (os.path.isfile(value)):
                try:
                    file = open(value, 'r')
                    for line in file.readlines():
                       i,j, lon, lat,name = line.strip().split(" ")
                       self.exported_nested_boundaries[name] = [lon,lat]
                except Exception as ex:
                    logging.error("'" + str(ex) + "' Unable to read nested boundaries")
            else:
                raise DirectoryError(WW3Config.MODEL,
                                     "[Exported nested boundaries] No such file: '" + value + "'", 1005)

    def set_output_points(self, value):

        self.output_points = {}

        if value is not None:
            if os.path.isfile(value):
                try:
                    file = open(value, 'r')
                    for line in file.readlines():
                        lon, lat, name = line.strip().split(" ")
                        self.output_points[name] = [lon, lat]
                except Exception as ex:
                    logging.error("'" + str(ex) + "' Unable to read output points")
            else:
                raise DirectoryError(WW3Config.MODEL,
                                     "[Outpout points] No such file: '" + value + "'", 1005)

    def set_initial_mode(self, value):

        if type(value) == int:
            if value == 0 or value == 1:
                self.initial_mode = value
            else:
                raise RunModeValueError(WW3Config.MODEL,
                                        "Initial mode has to be 0 or 1. Current value : '" + str(value) + "'",
                                        1005)
        else:
            raise RunModeValueError(WW3Config.MODEL,
                                    "Initial mode has to be an integer. Current type : '" + str(type(value)) + "'",
                                    1005)

    def set_next_restart_time(self, value):

        if value is not None:
            if type(value) == datetime:
                self.next_restart_time = value
            else:
                datetimeFormat = '%Y-%m-%d %H:%M:%S'
                try:
                    self.next_restart_time = datetime.strptime(value, datetimeFormat)
                except ValueError:
                    raise DateValueError(WW3Config.MODEL,
                                         "Restart time '" + str(value) + "' does not match format '" + str(
                                             datetimeFormat) + "'",
                                         1005)
        else:
            self.next_restart_time = None


    def make_grid(self):

        if "ww3_grid" not in self.inp_files:
            raise ConfigIntegrityError(WW3Config.MODEL,
                                       "Inp file 'ww3_grid' has to be initialized", 1005)

        if not os.path.isfile(os.path.join(self.config_dir, "ww3_grid")):
            self.build()

        logging.info("Making grid")

        execute(["./ww3_grid"],cwd=self.config_dir)

    def make_wind_forcing(self):

        if self.wind_src_forcing_file is not None:

            if "ww3_prnc" not in self.inp_files:
                raise ConfigIntegrityError(WW3Config.MODEL,
                                           "Inp file 'ww3_prnc' has to be initialized", 1005)

            if not os.path.isfile(os.path.join(self.config_dir, "ww3_prnc")):
                self.build()

            logging.info("Making wind forcing")

            self.set_wind_forcing_file(self.wind_src_forcing_file)

            for file in sorted(os.listdir(self.wind_forcing_dir)):
                try:
                    ncfile = Dataset(os.path.join(self.wind_forcing_dir, file), 'r')
                    if "U10M" in ncfile.variables and "V10M" in ncfile.variables:
                        self.inp_files["ww3_prnc"].set_type("WND")
                        self.inp_files["ww3_prnc"].set_file(os.path.join("wind", file))
                        self.inp_files["ww3_prnc"].generate(os.path.join(self.output_config_dir, self.config_name))

                        execute(["./ww3_prnc"], cwd=self.config_dir)
                    ncfile.close()

                except OSError as ex:
                    logging.debug("'" + str(os.path.join(self.wind_forcing_dir, file)) + "' is not a NetCDF file")

            if not os.path.isfile(os.path.join(self.config_dir, "wind.ww3")):
                raise MakeError(WW3Config.MODEL,
                                "No wind file generated", 1005)

    def make_obc_forcing(self):

        if self.obc_src_forcing_dir is not None:

            if "ww3_bounc" not in self.inp_files:
                raise ConfigIntegrityError(WW3Config.MODEL,
                                           "Inp file 'ww3_bounc' has to be initialized", 1005)

            if not os.path.isfile(os.path.join(self.config_dir, "ww3_bounc")):
                self.build()

            logging.info("Making OBC forcing")

            self.set_obc_forcing_dir(self.obc_src_forcing_dir)
            self.inp_files["ww3_bounc"].set_files(sorted(os.listdir(self.obc_forcing_dir)))
            self.inp_files["ww3_bounc"].generate(os.path.join(self.output_config_dir, self.config_name))

            execute(["./ww3_bounc"], cwd=self.config_dir)

            if not os.path.isfile(os.path.join(self.config_dir, "nest.ww3")):
                raise MakeError(WW3Config.MODEL,
                                "No OBC file generated", 1005)

    def save_restart_file(self):

        save_file = os.path.join(self.restart_dir, self.next_restart_time.strftime("%Y%m%d_%H%M%S") + ".ww3")

        times = []
        files = []

        for file in sorted(glob.glob(os.path.join(self.config_dir, "*.ww3"))):
            groups = re.search("^restart([0-9]+).ww3$", path_leaf(file))
            if groups:
                current_time = self.inp_files["ww3_shel"].start_time + timedelta(seconds=1800 * int(groups.group(1)))
                times.append(current_time)
                files.append(file)

        nearest_t_index = (np.abs(np.asarray(times) - self.next_restart_time)).argmin()
        if abs(self.next_restart_time - times[nearest_t_index]) >= timedelta(days=1):
            raise ConfigIntegrityError(WW3Config.MODEL,
                                       "No restart file", 1005)

        restart_file = os.path.join(self.config_dir, files[nearest_t_index])

        if os.path.isfile(restart_file):
            shutil.copy2(restart_file, save_file)
        else:
            raise ConfigIntegrityError(WW3Config.MODEL,
                                       "No restart file", 1005)

    def find_restart_file(self, value):

        if not self.inp_files["ww3_shel"]:
            raise ConfigIntegrityError(WW3Config.MODEL,
                                       "Inp file 'ww3_shel' has to be initialized", 1005)

        files = []
        times = []

        for file in sorted(glob.glob(os.path.join(self.restart_dir, "*.ww3"))):

            if os.path.isfile(os.path.join(self.restart_dir, file)):
                groups = re.search("^([0-9]{4})([0-9]{2})([0-9]{2})\_([0-9]{2})([0-9]{2})([0-9]{2}).*$",
                                   path_leaf(file))
                if groups:
                    current_time = datetime(int(groups.group(1)), int(groups.group(2)), int(groups.group(3)),
                                            int(groups.group(4)), int(groups.group(5)),
                                            int(groups.group(6)))
                    times.append(current_time)
                    files.append(file)

        if len(times) == 0:
            raise ConfigIntegrityError(WW3Config.MODEL,
                                       "No restart file found in 'restart' directory",
                                       1005)

        nearest_t_index = (np.abs(np.asarray(times) - value)).argmin()
        if abs(value - times[nearest_t_index]) != timedelta(seconds=0):
            raise ConfigIntegrityError(WW3Config.MODEL,
                                       "No restart file found for time '" + str(
                                           value) + "'",
                                       1005)

        shutil.copy2(os.path.join(self.restart_dir, files[nearest_t_index]),
                     os.path.join(self.config_dir, "restart.ww3"))

    def clean_wind_forcing_dir(self):

        try:
            if os.path.isfile(os.path.join(self.config_dir, "wind.ww3")):
                os.unlink(os.path.join(self.config_dir, "wind.ww3"))
        except Exception as ex:
            raise FileError(WW3Config.MODEL, ex, 1005)

        for filename in os.listdir(self.wind_forcing_dir):
            file_path = os.path.join(self.wind_forcing_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as ex:
                raise FileError(WW3Config.MODEL, ex, 1005)

    def clean_obc_forcing_dir(self):

        try:
            if os.path.isfile(os.path.join(self.config_dir, "nest.ww3")):
                os.unlink(os.path.join(self.config_dir,  "nest.ww3"))
        except Exception as ex:
            raise FileError(WW3Config.MODEL, ex, 1005)

        for filename in os.listdir(self.obc_forcing_dir):
            file_path = os.path.join(self.obc_forcing_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as ex:
                raise FileError(WW3Config.MODEL, ex, 1005)

    def clean_config_restart(self):

        try:
            for file in sorted(glob.glob(os.path.join(self.config_dir, "restart*.ww3"))):
                if os.path.isfile(os.path.join(self.config_dir, file)):
                    os.unlink(os.path.join(self.config_dir, file))
        except Exception as ex:
            raise FileError(WW3Config.MODEL, ex, 1005)

    def generate(self):

        if os.listdir(self.output_config_dir):
            raise DirectoryError(WW3Config.MODEL,
                                 "[Output configuration directory] '" + str(self.output_config_dir) + "' is not empty", 1005)

        if self.base_config_dir is None:
            raise DirectoryError(WW3Config.MODEL,
                                 "[Model base directory] Attribute 'base_config_dir' is not initiliazed",
                                 1005)

        if len(self.makefiles) == 0:
            raise MakeError(WW3Config.MODEL,
                                 "[Makefile] No makefiles are settled",
                            1005)

        logging.info("Create directory and copy source code...")

        # 1. Copie du modèle
        copytree(self.base_config_dir,self.output_config_dir)

        # 2. Création de l'arborescence de la config
        os.mkdir(self.config_dir)
        os.mkdir(self.bathy_dir)
        os.mkdir(self.wind_forcing_dir)
        os.mkdir(self.obc_forcing_dir)
        os.mkdir(self.graphique_dir)
        os.mkdir(self.restart_dir)

        self.make_grid()
        self.update()

    def update(self):

        if self.exists():

            logging.info("Generate files...")

            # INP  files
            for nb in self.inp_files.values():
                logging.info("Making "+nb.template_filename+" ...")
                nb.generate(self.config_dir)

            # Tweaks
            for tw in self.tweaks:
                logging.info("Making "+tw.template_filename+" ...")
                tw.generate(self.ftn_dir)

            self.make_grid()

            # Interpolate forcings
            self.make_wind_forcing()
            self.make_obc_forcing()

            self.clean_config_restart()

            if self.initial_mode == 1:
                self.find_restart_file(self.inp_files["ww3_shel"].start_time)

    def build(self):

        if self.exists():

            # Makefile
            for mk in self.makefiles:
                logging.info("Making " + mk.template_filename + " ...")
                mk.generate(self.bin_dir)

            logging.info("Build executable...")

            my_env = os.environ.copy()
            my_env["WWATCH3_ENV"] = os.path.join(self.bin_dir,"wwatch3.env")
            my_env["WWATCH3_NETCDF"] = "NC4"
            # On trouve le path de nc-config
            res = [i for i in os.environ['PATH'].split(':') if "netcdf" in i]
            nc_config = [i for i in res if "/c/" in i]

            my_env["NETCDF_CONFIG"] = os.path.join(nc_config[0],"nc-config")

            try:
                execute(["./w3_clean","-c"], cwd=self.bin_dir,env=my_env)
                execute(["./w3_setup","../ -s current -c ",self.compiler.lower() ,"-q"], cwd=self.bin_dir,env=my_env)

                # Add execution to comp file
                st = os.stat(os.path.join(self.bin_dir, "comp"))
                os.chmod(os.path.join(self.bin_dir, "comp"), st.st_mode | stat.S_IEXEC)

                # Add execution to link file
                st = os.stat(os.path.join(self.bin_dir, "link"))
                os.chmod(os.path.join(self.bin_dir, "link"), st.st_mode | stat.S_IEXEC)

                execute(["./w3_make"], cwd=self.bin_dir,env=my_env)

            except ExecutionError as ex:
                raise MakeError(WW3Config.MODEL,str(ex), 1005)

            if not os.path.isfile(os.path.join(self.exe_dir, "ww3_shel")) or not os.path.isfile(os.path.join(self.exe_dir, "ww3_prnc")):
                raise MakeError(WW3Config.MODEL,
                                "No executable generated", 1005)

            copytree(self.exe_dir,self.config_dir)

    def check_integrity(self):

        if self.exists():

            logging.info("Check integrity...")

    def run(self):

        if self.exists():

            logging.info("Run...")

            # 1. On teste si le notebook_time a été initialisé par la classe fille
            if "ww3_shel" not in self.inp_files:
                raise ConfigIntegrityError(WW3Config.MODEL,
                                           "Inp file 'ww3_shel.inp' has to be initialized", 1005)

            # 2. On teste si l'exécutable exists
            if not os.path.isfile(os.path.join(self.config_dir, "ww3_shel")):
                raise ConfigIntegrityError(WW3Config.MODEL,
                                           "No executable exist", 1005)

            # 3. Save old end_time
            if self.next_restart_time is not None:
                end_time = self.inp_files["ww3_shel"].end_time
                self.inp_files["ww3_shel"].set_end_time(self.next_restart_time)
                self.inp_files["ww3_shel"].generate(self.config_dir)

                # 5. Run test
                execute(["mpirun","-np","7","./ww3_shel"],cwd=self.config_dir)

                # 6. Restore end_time in notebook_time
                self.inp_files["ww3_shel"].set_end_time(end_time)
                self.inp_files["ww3_shel"].set_start_time(self.next_restart_time)
                self.inp_files["ww3_shel"].generate(self.config_dir)

                logging.info("Make restart...")

                # 9. Save the restart
                self.save_restart_file()
                self.find_restart_file(self.next_restart_time)

            logging.info("Run...")

            # 10. Run
            execute(["mpirun", "-np", "7","./ww3_shel"],cwd=self.config_dir)












