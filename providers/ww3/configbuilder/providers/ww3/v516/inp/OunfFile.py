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
from configbuilder.builder.FileTemplate import FileTemplate
from configbuilder.builder.exception.DateValueError import DateValueError
from datetime import datetime

class OunfFile(FileTemplate):

    def __init__(self, base_dir,
                 start_time,
                 end_time,
                 x_size=None,
                 y_size=None,
                 ):

        FileTemplate.__init__(self,base_dir,"ww3_ounf.inp");

        self.start_time = None
        self.set_start_time(start_time)

        self.end_time = None
        self.set_end_time(end_time)

        self.check_time()

        self.x_size = None
        self.set_x_size(x_size)

        self.y_size = None
        self.set_y_size(y_size)

    def set_x_size(self, value):
        self.x_size = value

    def set_y_size(self, value):
        self.y_size = value

    def set_start_time(self, value):
        if type(value) == datetime:
            self.start_time = value
        else:
            datetimeFormat = '%Y-%m-%d %H:%M:%S'
            try:
                self.start_time = datetime.strptime(value, datetimeFormat)
            except ValueError:
                raise DateValueError("NotebookTime",
                                     "Start time '" + str(value) + "' does not match format '" + str(
                                         datetimeFormat) + "'",
                                     1005)

    def set_end_time(self, value):
        if type(value) == datetime:
            self.end_time = value
        else:
            datetimeFormat = '%Y-%m-%d %H:%M:%S'
            try:
                self.end_time = datetime.strptime(value, datetimeFormat)
            except ValueError:
                raise DateValueError("NotebookTime",
                                     "End time '" + str(value) + "' does not match format '" + str(
                                         datetimeFormat) + "'",
                                     1005)

    def check_time(self):

        if self.end_time < self.start_time:
            raise DateValueError("NotebookTime",
                                 "End time is before start time. Start time : '" + str(
                                     self.start_time) + "' / End time '" + str(self.end_time) + "'",
                                 1005)







