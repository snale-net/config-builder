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
import subprocess
from configbuilder.builder.exception.ExecutionError import ExecutionError

def execute(commands,cwd=None,env=None):

    try:
        if cwd is not None and env is not None:
            process = subprocess.Popen(commands,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       cwd=cwd,
                                       env=env,
                                       universal_newlines=True)
        elif cwd is not None:
            process = subprocess.Popen(commands,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       cwd=cwd,
                                       universal_newlines=True)
        elif env is not None:
            process = subprocess.Popen(commands,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       env=env,
                                       universal_newlines=True)

        finished=False
        errors=""

        while not finished:
            output = process.stdout.readline()
            print(output.strip())
            # Do something else
            return_code = process.poll()

            if "ERROR" in output or "STOP" in output:
                errors+=output.strip()+"\n"
                for line in process.stdout.readlines():
                    errors+=line.strip()+"\n"

                raise ExecutionError("Execution", errors.strip(), 1005)

            if return_code is not None:
                # Process has finished, read rest of the output
                for output in process.stdout.readlines():
                    print(output.strip())

                if return_code != 0 :
                    print(process.stderr.readlines())
                    raise ExecutionError("Execution", output.strip(), 1005)

                finished=True

    except FileNotFoundError as ex:
        raise ExecutionError("Execution","Commands not found :"+str(ex), 1005)

