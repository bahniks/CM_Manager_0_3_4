"""
Copyright 2013 Štěpán Bahník

This file is part of Carousel Maze Manager.

Carousel Maze Manager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Carousel Maze Manager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Carousel Maze Manager.  If not, see <http://www.gnu.org/licenses/>.
"""

from math import radians, cos, sin


class SVG():
    "represents .svg file - text of the file is stored in self.content"
    def __init__(self, width, height, scale = 1):
        # dodelat scale tu a v save, odstranit jinde
        self.content = '<svg viewbox = "0 0 {} {}" xmlns="http://www.w3.org/2000/svg">\n'.format(
            width * scale, height * scale)
        self.content += '<g transform="scale({0},{0})">\n'.format(scale)
        self.content += '<rect style="stroke:white;fill:none" x="0" y="0" ' + \
                        'width="{}" height="{}" />\n'.format(width, height)
        
    
    def drawAAPA(self, cm, frame, startTime = 0, time = 20, origin = (0, 0), boundary = False,
                 sector = False, shocks = False, size = 300, skip = 3):
        "adds text into sefl.content corresponding to track from one frame of AAPA"

        self.content += '<g transform="translate{}">\n'.format(origin)

        if boundary:
            self.content += '<rect style="stroke:black;fill:none" x="0" y="0" ' + \
                            'width="{0}" height="{0}" />\n'.format(size)            

        start = cm.findStart(startTime)
        time = time * 60000
        r = cm.getComputedDiameter()

        self.content += '<g transform="translate({0},{0})">\n'.format((size / 2) - r)

        if sector:
            self.angle = cm.getCenterAngle()
            self.width = cm.getWidth()
            a1 = radians(self.angle - (self.width / 2))
            a2 = radians(self.angle + (self.width / 2))
            Sx1, Sy1 = r + (cos(a1) * r), r - (sin(a1) * r)
            Sx2, Sy2 = r + (cos(a2) * r), r - (sin(a2) * r)
            self.content += '<polyline fill="none" stroke="red" stroke-width="1.5" ' +\
                            'points="{},{} {},{} {},{}"/>\n'.format(Sx1, Sy1, r, r, Sx2, Sy2)              

        self.content += '<polyline points="'        
        if frame == "room":
            prev = (0, 0)
            shock = False
            shockPositions = []
            for line in cm.data[start:]:
                if line[1] > time:
                    break
                positions = line[2:4]
                if positions != prev:
                    self.content += ",".join(map(str, positions)) + " "
                if line[6] > 0:
                    if not shock:
                        shock = True
                        shockPositions.append(positions)
                else:
                    shock = False                        
                prev = positions
        elif frame == "arena":
            prev = (0, 0)
            for count, line in enumerate(cm.data[start:], skip):
                if line[1] > time:
                    break
                positions = line[7:9]
                if count % skip == 0 and positions != prev:
                    self.content += ",".join(map(str, positions)) + " "
                    prev = positions
        self.content += '" style = "fill:none;stroke:black"/>\n'

        if shocks and frame == "room": # u double avoidance odstranit frame podminku
            for position in shockPositions:
                self.content += '<circle fill="none" stroke="red" stroke-width="1.5" ' +\
                                'cx="{}" cy="{}" r="3" />\n'.format(*position)

        self.content += '<circle fill="none" stroke="black" ' +\
                        'cx="{0}" cy="{0}" r="{0}" />\n'.format(r)

        self.content += '</g>\n'
        
        self.content += '</g>\n'


    def drawGraph(self, points, furtherText = "", origin = (0, 0), boundary = False):
        "adds text containing information about graph in self.content"
        size = (600, 120)
        self.content += '<g transform="translate{0}">\n'.format(origin)
        if boundary:
            self.content += '<rect style="stroke:black;fill:none" x="0" y="0" ' + \
                            'width="{}" height="{}" />\n'.format(*size)  
        self.content += furtherText
        if points:
            self.content += '<polyline points="'
            for pair in points:
                self.content += ",".join(map(str, pair)) + " "      
            self.content += '" style = "fill:none;stroke:black"/>\n'
        self.content += '</g>\n'
        

    def save(self, file):
        "closes tags and saves self.content into a file"
        self.content += '</g>\n'
        self.content += "</svg>"
        infile = open(file, mode = "w")
        infile.write(self.content)
        infile.close()        




def main():
    from cm import CM
    import os
    import os.path
    svg = SVG(300, 300)
    cm = CM(os.path.join(os.getcwd(), "TestingFiles", "14rNO465_Arena.dat"))
    svg.drawAAPA(cm, "room", scale = 3, boundary = True, sector = True, shocks = True)
    svg.save("test.svg")
    os.startfile("test.svg")




if __name__ == "__main__": main()
