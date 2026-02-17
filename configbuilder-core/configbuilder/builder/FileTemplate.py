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
import os
from jinja2 import Environment, FileSystemLoader
from configbuilder.builder.exception import DirectoryError
from configbuilder.builder.exception.FileError import FileError

class FileTemplate():

    def __init__(self,templateDir, template,output_name=None):
        self.base_template_dir = None
        self.set_base_template_dir(templateDir)

        self.template_filename = None
        self.set_template_filename(template)

        self.output_name=output_name

    def set_base_template_dir(self, value):

        if (os.path.isdir(value)):
            self.base_template_dir = value
        else:
            raise DirectoryError("FileTemplate","[Template base directory] No such directory :'" + value + "'", 1005)

    def set_template_filename(self,value):
        if os.path.isfile(os.path.join(self.base_template_dir, value)):
            self.template_filename = value
        else:
            raise FileError("FileTemplate","[Template file] No such file: '" + os.path.join(self.base_template_dir, value) + "'", 1005)

    def generate(self, outputDir):

        file_loader = FileSystemLoader(self.base_template_dir)
        env = Environment(loader=file_loader)

        template = env.get_template(self.template_filename)
        output = template.render(candidate=self)

        filename = self.template_filename
        if self.output_name is not None:
            filename = self.output_name

        with open(os.path.join(outputDir, filename), 'w') as f:
            f.write(output+"\n")
