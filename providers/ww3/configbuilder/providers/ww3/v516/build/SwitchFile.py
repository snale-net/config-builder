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

class SwitchFile(FileTemplate):

    def __init__(self,
                 base_dir,
                 ST1=False,
                 ST2=False,
                 ST3=False,
                 ST4=True,
                 ST5=False,
                 ST6=False,
                 STAB2=False,
                 STAB0=False,
                 STAB3=True,
                 OASOCM=False,
                 OASACM = False
                 ):
        FileTemplate.__init__(self, base_dir, "switch_current");

        self.ST1=ST1
        self.ST2=ST2
        self.ST3=ST3
        self.ST4=ST4
        self.ST5=ST5
        self.ST6=ST6

        if self.ST1 and self.ST2 and self.ST3 and self.ST4 and self.ST5 and self.ST6:
            raise CompilatorError("SwitchFile",
                                  "You must choise betwen ST1, ST2, ST3,ST3,ST5 or ST6", 1005)

        self.STAB0 = STAB0
        self.STAB2= STAB2
        self.STAB3=STAB3

        if self.STAB0 and self. STAB2 and self.STAB3 :
            raise CompilatorError("SwitchFile",
                                  "You must choise betwen STAb0, STAB2 or STAB3", 1005)

        self.COU = False
        self.OASIS = False
        self.OASOCM = OASOCM
        self.OASACM = OASACM

        if self.OASOCM or self.OASACM:
            self.COU=True
            self.OASIS=True






