#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
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
from configbuilder.builder.exception import *
import os
import re

class Configuration():

    def __init__(self,outputDir,name):

        self.output_config_dir = None
        self.set_output_config_dir(outputDir)

        self.config_name = None
        self.set_config_name(name)

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

    def set_base_config_dir(self, value):

        if (os.path.isdir(value)):

            if os.listdir(value):
                self.base_config_dir = value
            else:
                raise DirectoryError("Configuration",
                                     "[Model base directory] '" + value + "' is empty", 1005)
        else:
            raise DirectoryError("Configuration",
                                 "[Model base directory] No such directory: '" + value + "'", 1005)

    def exists(self):
        if len(os.listdir(self.output_config_dir)) == 0:
            raise DirectoryError("Configuration","No configuration exists in '" + str(self.output_config_dir) + "'",
                                 1005)

        return True

    def generate(self):
        raise NotImplementedError(str(type(self))+" don't have implemented the function 'generate()'.")

    def build(self):
        raise NotImplementedError(str(type(self))+" don't have implemented the function 'build()'.")

    def update(self):
        raise NotImplementedError(str(type(self)) + " don't have implemented the function 'update()'.")

    def check_integrity(self):
        raise NotImplementedError(str(type(self)) + " don't have implemented the function 'check_integrity()'.")








