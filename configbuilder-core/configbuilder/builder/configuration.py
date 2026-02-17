# -*- coding: utf-8 -*-
from abc import ABC

from configbuilder.exception import *
import os
import re

class Configuration(ABC):

    def __init__(self,modelDir,name,outputDir):

        self.model_source_dir = None
        self.set_model_source_dir(modelDir)

        self.output_config_dir = None
        self.set_output_config_dir(outputDir)

        self.config_name = None
        self.set_config_name(name)

    def set_model_source_dir(self, value):

        if (os.path.isdir(value)):
            self.model_source_dir = value
        else:
            raise DirectoryError("Configuration",
                                 "[Model directory] No such directory: '"+value + "'", 1005)

        self.check_model_source_dir();

    def set_output_config_dir(self, value):

        if (os.path.isdir(value)):
            self.output_config_dir = value
        else:
            raise DirectoryError("Configuration",
                                 "[Output configuration directory] No such directory: '"+value + "'", 1005)

    def set_config_name(self,value):

        regex = re.compile(r'[^A-Za-z0-9_\-\\]')

        if (regex.search(value) == None):
            self.config_name = value
        else:
            raise ConfigNameError("Configuration","Name '"+value + "' contains special characters",1005)

    def exists(self):
        if len(os.listdir(self.output_config_dir)) == 0:
            raise DirectoryError("Configuration","No configuration exists in '" + str(self.output_config_dir) + "'",
                                 1005)

        return True

    def check_model_source_dir(self):
        raise NotImplementedError(str(type(self)) + " don't have implemented the function 'check_model_source_dir()'.")

    def generate(self):
        raise NotImplementedError(str(type(self))+" don't have implemented the function 'generate()'.")

    def build(self):
        raise NotImplementedError(str(type(self))+" don't have implemented the function 'build()'.")

    def update(self):
        raise NotImplementedError(str(type(self)) + " don't have implemented the function 'update()'.")

    def check_integrity(self):
        raise NotImplementedError(str(type(self)) + " don't have implemented the function 'check_integrity()'.")








