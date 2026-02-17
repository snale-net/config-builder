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
from configbuilder.builder.exception.CompilatorError import CompilatorError

class CompFile(FileTemplate):

    def __init__(self,
                 base_dir,
                 include,
                 compiler,
                 mpi_lib,
                 debug_mode=False
                 ):

        if compiler.lower() == "gnu":
            FileTemplate.__init__(self, base_dir, "comp.gnu");

            if mpi_lib.lower() != "openmpi":
                raise CompilatorError("CompFile",
                                      "Only 'openmpi' is accepted. Current value : '" + str(mpi_lib) + "'", 1005)

        elif compiler.lower() == "intel":
            FileTemplate.__init__(self, base_dir, "comp.intel");

            if mpi_lib.lower() != "intelmpi":
                raise CompilatorError("CompFile",
                                      "Only 'intelmpi' is accepted. Current value : '" + str(mpi_lib) + "'", 1005)
        else:
            raise CompilatorError("CompFile",
                                  "Compilator '" + compiler.lower() + "' doesn't exist", 1005)

        self.include = include
        self.debug_mode = debug_mode





