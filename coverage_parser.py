# Copyright (c) 2018, BlockProject
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of BlockProject nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import re
import sys
from html_gcovr import loadGCovrHTML
from codacy_sender import sendToCodacy

# Commands :
#  - mkdir cout
#  - gcovr -r . --html --html-details -o cout/index.html
#  - gcovr -r . -o cout/main.txt

class GCovrReport:
    def __init__(self, filename):
        self.fileName = filename
        self.nextFileName = None
        self.report = []
        self.totalLines = 0
        self.totalExecs = 0
        self.parseCoverageFile(filename + "/main.txt")
    
    def processFileName(self, filename):
        filename = filename.replace("/", "_")
        return (self.fileName + "/index." + filename + ".html")

    def onSourceFound(self, filename, coverage):
        html = self.processFileName(filename)
        htmlres = loadGCovrHTML(html)
        obj1 = {}
        for o in htmlres:
            if (o["covered"]):
                obj1[o["number"]] = 1
            else:
                obj1[o["number"]] = 0
        obj = {
            "filename": filename,
            "total": int(coverage),
            "coverage": obj1
        }
        self.report.append(obj)

    def parseLine(self, line):
        data = list(filter(None, line.split(' ')))
        if (data[0] == "File" or data[0] == "GCC"):
            return
        if (len(data) > 2):
            if (data[0] == "TOTAL"):
                return
            if (self.nextFileName != None):
                percent = float(data[1]) * 100.0 / float(data[0])
                self.totalExecs = self.totalExecs + float(data[1])
                self.totalLines = self.totalLines + float(data[0])
                self.onSourceFound(self.nextFileName, percent)
                self.nextFileName = None
            else:
                percent = float(data[2]) * 100.0 / float(data[1])
                self.totalExecs = self.totalExecs + float(data[2])
                self.totalLines = self.totalLines + float(data[1])
                self.onSourceFound(data[0], percent)
        else:
            self.nextFileName = data[0]

    def parseCoverageFile(self, filename):
        with open(filename) as f:
            content = f.readlines()
            content = [x.strip() for x in content]
            for ln in content:
                self.parseLine(ln)
    
    def genFinalJSON(self):
        obj = {
            "total": int(self.totalExecs * 100.0 / self.totalLines),
            "fileReports": self.report
        }
        return (obj)

report = GCovrReport(sys.argv[1])
