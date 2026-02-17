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
import glob
import logging
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from configbuilder.builder.exception import *
from configbuilder.providers.swan.v431.swn import *
from netCDF4 import Dataset

from configbuilder.builder.configuration import Configuration
from configbuilder.utils.call import execute
from configbuilder.utils.path import copytree
from configbuilder.utils.path import path_leaf


class SwanConfig(Configuration):
    BASE_DIR = Path(__file__).resolve().parent.parent
    MODEL = "SWAN"

    if 'INCLUDE' in os.environ:
        NETCDF_INC = "-I" + os.environ['INCLUDE'].replace(':', ' -I')
    else:
        NETCDF_INC = ""
    if 'LD_LIBRARY_PATH' in os.environ:
        NETCDF_LIB = "-L" + os.environ['LD_LIBRARY_PATH'].replace(':', ' -L') + " -lnetcdf -lnetcdff -lpnetcdf"
    else:
        NETCDF_LIB = ""

    def __init__(
            self,
            model_source_dir,
            outputDir,
            name,
            wind_forcing_dir=None,
            obc_forcing_dir=None,
            initial_mode=0,
            next_restart_time=None):

        Configuration.__init__(self, model_source_dir, name, outputDir);

        self.model_dir = os.path.join(self.output_config_dir, "model")

        self.config_dir = os.path.join(self.output_config_dir, self.config_name)
        self.bathy_dir = os.path.join(self.output_config_dir, self.config_name, "bathy")
        self.wind_forcing_dir = os.path.join(self.output_config_dir, self.config_name, "wind")
        self.obc_forcing_dir = os.path.join(self.output_config_dir, self.config_name, "obc")
        self.graphique_dir = os.path.join(self.output_config_dir, self.config_name, "graphiques")
        self.restart_dir = os.path.join(self.output_config_dir, self.config_name, "restart")

        # Makefile
        self.makefiles = {}

        # Notebook
        self.swn_files = {}

        # Tweaks
        self.tweaks = []

        self.set_wind_forcing_dir(wind_forcing_dir)
        self.set_obc_forcing_dir(obc_forcing_dir)

        self.set_initial_mode(initial_mode)
        self.set_next_restart_time(next_restart_time)

    def check_model_source_dir(self):

        if (not os.path.exists(os.path.join(self.model_source_dir, "Makefile"))):
            raise DirectoryError("SymphonieConfig",
                                 "[Model directory] is not a proper SWAN instance : No fortran files", 1005)

    def set_wind_forcing_dir(self, value):

        if value is not None:
            if (os.path.isdir(value)):

                if os.listdir(value):
                    self.wind_forcing_dir = value
                else:
                    raise DirectoryError(SwanConfig.MODEL,
                                         "[Wind forcing directory] '" + value + "' is empty", 1005)
            else:
                raise DirectoryError(SwanConfig.MODEL,
                                     "[Wind forcing directory] No such directory: '" + value + "'", 1005)
        else:
            self.wind_forcing_dir = None

    def set_obc_forcing_dir(self, value):

        if value is not None:
            if (os.path.isdir(value)):

                if os.listdir(value):
                    self.obc_forcing_dir = value
                else:
                    raise DirectoryError(SwanConfig.MODEL,
                                         "[OBC forcing directory] '" + value + "' is empty", 1005)
            else:
                raise DirectoryError(SwanConfig.MODEL,
                                     "[OBC forcing directory] No such directory: '" + value + "'", 1005)
        else:
            self.obc_forcing_dir = None

    def set_initial_mode(self, value):

        if type(value) == int:
            if value == 0 or value == 1:
                self.initial_mode = value
            else:
                raise RunModeValueError(SwanConfig.MODEL,
                                        "Initial mode has to be 0 or 1. Current value : '" + str(value) + "'",
                                        1005)
        else:
            raise RunModeValueError(SwanConfig.MODEL,
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
                    raise DateValueError(SwanConfig.MODEL,
                                         "Restart time '" + str(value) + "' does not match format '" + str(
                                             datetimeFormat) + "'",
                                         1005)
        else:
            self.next_restart_time = None

    def make_wind_forcing(self):

        if self.wind_forcing_dir is not None:

            logging.info("Making wind forcing")

            files = []

            for file in sorted(os.listdir(self.wind_forcing_dir)):
                try:
                    ncfile = Dataset(os.path.join(self.wind_forcing_dir, file), 'r')
                    if "U10M" in ncfile.variables and "V10M" in ncfile.variables:
                        files.append(os.path.join("wind", file))
                    ncfile.close()

                except OSError as ex:
                    logging.debug("'" + str(os.path.join(self.wind_forcing_dir, file)) + "' is not a NetCDF file")

            if len(files) == 0:
                raise FileError("WindForcing", "No wind forcing file found", 1005)

    def make_obc_forcing(self):

        if self.obc_forcing_dir is not None:

            logging.info("Making OBC list")

            varT = open(os.path.join(self.output_config_dir, self.config_name, "LIST", "obc", "list_var_T"), 'w')
            varS = open(os.path.join(self.output_config_dir, self.config_name, "LIST", "obc", "list_var_S"), 'w')
            varU = open(os.path.join(self.output_config_dir, self.config_name, "LIST", "obc", "list_var_U"), 'w')
            varV = open(os.path.join(self.output_config_dir, self.config_name, "LIST", "obc", "list_var_V"), 'w')
            varSSH = open(os.path.join(self.output_config_dir, self.config_name, "LIST", "obc", "list_var_SSH"), 'w')
            gridT = open(os.path.join(self.output_config_dir, self.config_name, "LIST", "obc", "list_grid_T"), 'w')
            gridU = open(os.path.join(self.output_config_dir, self.config_name, "LIST", "obc", "list_grid_U"), 'w')
            gridV = open(os.path.join(self.output_config_dir, self.config_name, "LIST", "obc", "list_grid_V"), 'w')

            foundGridFile = False

            for file in sorted(os.listdir(self.obc_forcing_dir)):
                try:
                    ncfile = Dataset(os.path.join(self.obc_forcing_dir, file), 'r')
                    if "sossheig" in ncfile.variables or "ssh" in ncfile.variables or "zos" in ncfile.variables:
                        varSSH.write(os.path.join(self.obc_forcing_dir, file) + "\n")

                    if "votemper" in ncfile.variables or "temperature" in ncfile.variables or "thetao" in ncfile.variables:
                        varT.write(os.path.join(self.obc_forcing_dir, file) + "\n")

                    if "vosaliner" in ncfile.variables or "salinity" in ncfile.variables or "so" in ncfile.variables:
                        varS.write(os.path.join(self.obc_forcing_dir, file) + "\n")

                    if "u" in ncfile.variables or "uo" in ncfile.variables:
                        varU.write(os.path.join(self.obc_forcing_dir, file) + "\n")

                    if "v" in ncfile.variables or "vo" in ncfile.variables:
                        varV.write(os.path.join(self.obc_forcing_dir, file) + "\n")

                    if "depth" in ncfile.variables and not foundGridFile:
                        foundGridFile = True
                        gridT.write(os.path.join(self.obc_forcing_dir, file) + "\n")
                        gridU.write(os.path.join(self.obc_forcing_dir, file) + "\n")
                        gridV.write(os.path.join(self.obc_forcing_dir, file) + "\n")

                    ncfile.close()

                except OSError as ex:
                    logging.debug("'" + str(os.path.join(self.obc_forcing_dir, file)) + "' is not a NetCDF file")

            varT.close()
            varS.close()
            varU.close()
            varV.close()
            varSSH.close()
            gridT.close()
            gridU.close()
            gridV.close()

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
            raise ConfigIntegrityError(SwanConfig.MODEL,
                                       "No restart file", 1005)

        restart_file = os.path.join(self.config_dir, files[nearest_t_index])

        if os.path.isfile(restart_file):
            shutil.copy2(restart_file, save_file)
        else:
            raise ConfigIntegrityError(SwanConfig.MODEL,
                                       "No restart file", 1005)

    def find_restart_file(self, value):

        if not self.inp_files["ww3_shel"]:
            raise ConfigIntegrityError(SwanConfig.MODEL,
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
            raise ConfigIntegrityError(SwanConfig.MODEL,
                                       "No restart file found in 'restart' directory",
                                       1005)

        nearest_t_index = (np.abs(np.asarray(times) - value)).argmin()
        if abs(value - times[nearest_t_index]) != timedelta(seconds=0):
            raise ConfigIntegrityError(SwanConfig.MODEL,
                                       "No restart file found for time '" + str(
                                           value) + "'",
                                       1005)

        shutil.copy2(os.path.join(self.restart_dir, files[nearest_t_index]),
                     os.path.join(self.config_dir, "restart.ww3"))

    def clean_wind_forcing_dir(self):

        for filename in os.listdir(self.wind_forcing_dir):
            file_path = os.path.join(self.wind_forcing_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as ex:
                raise FileError(SwanConfig.MODEL, ex, 1005)

    def clean_config_restart(self):

        try:
            for file in sorted(glob.glob(os.path.join(self.config_dir, "restart*.ww3"))):
                if os.path.isfile(os.path.join(self.config_dir, file)):
                    os.unlink(os.path.join(self.config_dir, file))
        except Exception as ex:
            raise FileError(SwanConfig.MODEL, ex, 1005)

    def generate(self):

        if os.listdir(self.output_config_dir):
            raise DirectoryError(SwanConfig.MODEL,
                                 "[Output configuration directory] '" + str(self.output_config_dir) + "' is not empty",
                                 1005)

        if self.base_config_dir is None:
            raise DirectoryError(SwanConfig.MODEL,
                                 "[Model base directory] Attribute 'base_config_dir' is not initiliazed",
                                 1005)

        if len(self.makefiles) == 0:
            raise MakeError(SwanConfig.MODEL,
                            "[Makefile] No makefiles are settled",
                            1005)

        logging.info("Create directory and copy source code...")

        # 1. Copie du modèle
        copytree(self.base_config_dir, self.output_config_dir)

        # 2. Création de l'arborescence de la config
        os.mkdir(self.config_dir)
        os.mkdir(self.bathy_dir)
        os.mkdir(self.graphique_dir)
        os.mkdir(self.restart_dir)

        self.update()

    def update(self):

        if self.exists():

            self.make_grid()

            logging.info("Generate files...")

            # SWN  files
            for nb in self.swn_files.values():
                logging.info("Making " + nb.template_filename + " ...")
                nb.generate(self.config_dir)

            # Tweaks
            for tw in self.tweaks:
                logging.info("Making " + tw.template_filename + " ...")
                tw.generate(self.ftn_dir)

            # Interpolate forcings
            self.make_wind_forcing()
            # self.make_obc_list()

            self.clean_config_restart()

            if self.initial_mode == 1:
                self.find_restart_file(self.inp_files["ww3_shel"].start_time)

    def build(self):

        if self.exists():

            if "macro.inc" not in self.makefiles:
                raise ConfigIntegrityError(SwanConfig.MODEL,
                                           "Build file 'macro.inc' has to be initialized", 1005)

            # On trouve le path de nc-config
            res = [i for i in os.environ['PATH'].split(':') if "netcdf" in i]
            nc_config = [i for i in res if "/fortran/" in i]

            print(nc_config[0][0:len(nc_config[0]) - 3])

            self.makefiles["macro.inc"].set_netcdf_dir(nc_config[0][0:len(nc_config[0]) - 3])

            # Makefile
            for mk in self.makefiles:
                logging.info("Making " + self.makefiles[mk].template_filename + " ...")
                self.makefiles[mk].generate(self.model_dir)

            logging.info("Build executable...")

            try:
                execute(["make", "mpi"], cwd=self.model_dir)
                execute(["chmod", "+x", "swanrun"], cwd=self.model_dir)

            except ExecutionError as ex:
                raise MakeError(SwanConfig.MODEL, str(ex), 1005)

            if not os.path.isfile(os.path.join(self.model_dir, "swan.exe")) or not os.path.isfile(
                    os.path.join(self.model_dir, "swanrun")):
                raise MakeError(SwanConfig.MODEL,
                                "No executable generated", 1005)

    def check_integrity(self):

        if self.exists():
            logging.info("Check integrity...")

    def run(self):

        if self.exists():

            logging.info("Run...")

            my_env = os.environ.copy()
            my_env["PATH"] = self.model_dir + ":" + my_env["PATH"]

            # 1. On teste si le notebook_time a été initialisé par la classe fille
            if "config" not in self.swn_files:
                raise ConfigIntegrityError(SwanConfig.MODEL,
                                           "Swn file 'config' has to be initialized", 1005)

            # 2. On teste si l'exécutable exists
            if not os.path.isfile(os.path.join(self.model_dir, "swanrun")):
                raise ConfigIntegrityError(SwanConfig.MODEL,
                                           "No executable exist", 1005)

            # 3. Save old end_time
            if self.next_restart_time is not None:
                end_time = self.inp_files["ww3_shel"].end_time
                self.inp_files["ww3_shel"].set_end_time(self.next_restart_time)
                self.inp_files["ww3_shel"].generate(self.config_dir)

                # 5. Run test
                execute("./ww3_shel", cwd=self.config_dir)

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
            execute([os.path.join(self.model_dir, "swanrun"), "-input", "config.swn"], cwd=self.config_dir, env=my_env)
