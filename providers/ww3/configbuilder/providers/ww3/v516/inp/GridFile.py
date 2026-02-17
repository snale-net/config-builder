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
from configbuilder.builder.exception.FileError import FileError


class GridFile(FileTemplate):

    def __init__(self, base_dir,
                 config_name,
                 global_time_step,
                 spatial_time_step,
                 spectral_time_step,
                 source_time_step,
                 bathy_dir,
                 obc_forcing_points,
                 x_size=None,
                 y_size=None,
                 incr_freq=1.1,
                 start_freq=0.0625,
                 nb_freq=30,
                 nb_angle_section=24,
                 ):

        FileTemplate.__init__(self,base_dir,"ww3_grid.inp");

        self.config_name=config_name
        self.global_time_step=global_time_step
        self.spatial_time_step=spatial_time_step
        self.spectral_time_step=spectral_time_step
        self.source_time_step=source_time_step

        self.incr_freq=incr_freq
        self.start_freq=start_freq
        self.nb_freq=nb_freq
        self.nb_angle_section=nb_angle_section

        self.bathy_dir = bathy_dir
        self.obc_forcing_points = obc_forcing_points

        self.x_size=None
        self.set_x_size(x_size)

        self.y_size=None
        self.set_y_size(y_size)

    def set_x_size(self,value):
        self.x_size=value

    def set_y_size(self,value):
        self.y_size=value







