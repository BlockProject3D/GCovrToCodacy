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

from html.parser import HTMLParser

class GCovrHtmlReportParser(HTMLParser):
    def setup(self):
        self.tCount = 0
        self.inTr = False
        self.coverage = []
        self.curLine = {}
        self.inLineNo = False
        self.needData = False
        self.data = ""
    
    def getResult(self):
        return (self.coverage)

    def processTdInTr(self, attrs):
        for k in range(0, len(attrs)):
            name, val = attrs[k]
            if (name == "class" and "uncoveredLine" in val):
                self.curLine["covered"] = False
            elif (name == "class" and "coveredLine" in val):
                self.curLine["covered"] = True
            elif (name == "class" and "lineno" in val):
                self.inLineNo = True

    def handle_starttag(self, tag, attrs):
        if (tag == "table"):
            self.tCount = self.tCount + 1
        if (tag == "tr" and self.tCount >= 2):
            self.inTr = True
        if (tag == "td" and self.inTr):
            self.processTdInTr(attrs)
        if (tag == "pre" and self.inLineNo):
            self.needData = True

    def handle_data(self, data):
        if (self.inLineNo and self.needData):
            self.inLineNo = False
            self.needData = False
            self.curLine["number"] = data

    def handle_endtag(self, tag):
        if (tag == "tr"):
            self.inTr = False
            if (self.curLine != {} and ("covered" in self.curLine)):
                self.coverage.append(self.curLine)
                self.curLine = {}

def loadGCovrHTML(filename):
    parser = GCovrHtmlReportParser()
    parser.setup()
    data = ""
    with open(filename) as openfileobject:
        for line in openfileobject:
            data = data + line
        parser.feed(data)
    return (parser.getResult())
