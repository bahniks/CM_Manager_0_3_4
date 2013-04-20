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

from tkinter import *
from tkinter import ttk
from math import degrees, atan2, floor

from optionget import optionGet


def getGraphTypes():
    "returns types of graphs used in Processor class as a list (with their respective methods)"
    types = [["Angle", "AngleGraph(self)"],
             ["Distance from center", "DistanceFromCenterGraph(self)"],
             ["Speed", "SpeedGraph(self)"]             
             ]
    return types



class Graphs(Canvas):
    "parent class for all 'wide' graphs in Explore page"
    def __init__(self, parent, width = 620, height = 120):
        super().__init__(parent)
        self["width"] = width
        self["height"] = height
        self["background"] = "white"
        self.height = height
        self.width = width
        self.parent = parent
        self.drawnParameter = None


    def changedTime(self, newTime):
        "changes position of a time measure on a graph"
        x = (newTime - self.minTime) * self.width / (self.maxTime - self.minTime)
        if x < 2:
            x = 2
        self.coords("timeMeasure", (x, 0, x, self.height))


    def CM_loaded(self, CM, minTime, maxTime, initTime):
        "basic method called when a file is loaded"
        # time measure
        self.create_line((2, 0, 2, self.height), fill = "red", tags = "timeMeasure")

        # maximum time in miliseconds
        if maxTime == "max":
            self.maxTime = CM.data[-1][1]
        else:
            self.maxTime = maxTime

        if minTime == "min":
            self.minTime = CM.data[0][1]
        else:
            self.minTime = minTime

        # set time measure
        self.changedTime(initTime)

        self.drawParameter(cm = CM, parameter = self.drawnParameter)


    def drawPeriods(self, periods):
        "draws selected parameter on top of the graph" 
        if not periods:
            return
        timeSpread = (self.maxTime - self.minTime)
        for period in periods:
            if period[0] > self.minTime and period[1] < self.maxTime:
                begin = period[0]
                end = period[1]
            elif self.minTime < period[1] < self.maxTime:
                begin = self.minTime
                end = period[1]
            elif self.minTime < period[0] < self.maxTime:
                begin = period[0]
                end = self.maxTime
            else:
                continue
            self.create_line(((begin - self.minTime) * self.width / timeSpread,
                              0.03 * self.height,
                              (end - self.minTime) * self.width / timeSpread,
                              0.03 * self.height),
                             fill = "red", width = 3, tags = "parameter")


    def drawTimes(self, times):
        "draws selected parameter on top of the graph"
        if not times:
            return
        timeSpread = (self.maxTime - self.minTime)
        for time in times:
            if self.minTime < time < self.maxTime:
                x = (time - self.minTime) * self.width / timeSpread
                self.create_line((x, 0.01 * self.height, x, 0.07 * self.height),
                                 fill = "red", width = 1, tags = "parameter")        


    def drawParameter(self, cm, parameter):
        "computes selected parameter to be drawn on top of the graph" 
        if self.drawnParameter:
            self.delete("parameter")

        self.drawnParameter = parameter

        if parameter == "periodicity":
            self.drawPeriods(cm.getPeriodicity(forGraph = True, time = self.maxTime / 60000,
                                               startTime = self.minTime / 60000,
                                               minSpeed = optionGet('MinSpeedPeriodicity',
                                                                    10, ['int', 'float']),
                                               skip = optionGet('SkipPeriodicity', 12, ['int']),
                                               smooth = optionGet('SmoothPeriodicity', 2, ['int']),
                                               minTime = optionGet('MinTimePeriodicity', 9,
                                                                   ['int', 'float', 'list'])))
        elif parameter == "immobility":
            self.drawPeriods(cm.getMaxTimeOfImmobility(forGraph = True,
                                                       time = self.maxTime / 60000,
                                                       startTime = self.minTime / 60000,
                                                       minSpeed = optionGet(
                                                           'MinSpeedMaxTimeImmobility', 10,
                                                           ['int', 'float']),
                                                       skip = optionGet('SkipMaxTimeImmobility',
                                                                        12, 'int'),
                                                       smooth = optionGet(
                                                           'SmoothMaxTimeImmobility', 2, 'int')))
        elif parameter == "mobility":
            immobility = cm.getMaxTimeOfImmobility(forGraph = True, time = self.maxTime / 60000,
                                                   startTime = self.minTime / 60000,
                                                   minSpeed = optionGet('MinSpeedPercentMobility',
                                                                        5, ['int', 'float']),
                                                   skip = optionGet('SkipPercentMobility', 12,
                                                                    'int'),
                                                   smooth = optionGet('SmoothPercentMobility', 2,
                                                                      'int'))
            mobility = []
            t0 = self.minTime
            for times in immobility:
                t1 = times[0]
                mobility.append((t0, t1))
                t0 = times[1]
            self.drawPeriods(mobility)
        elif parameter == "thigmotaxis":
            percentSize = optionGet("ThigmotaxisPercentSize", 20, ["int", "float"])
            border = cm.getComputedDiameter() * (1 - (percentSize / 100))
            start = cm.findStart(self.minTime / 60000)
            periods = []
            outside = False
            t0 = self.minTime
            for content in cm.data[start:]:
                if content[1] <= self.maxTime: 
                    distance = ((content[2] - cm.centerX)**2 +\
                                (content[3] - cm.centerY)**2)**0.5
                    if distance >= border:
                        if not outside:
                            t0 = content[1]
                        outside = True
                    elif outside:
                        outside = False
                        periods.append((t0, content[1]))
                else:
                    break
            if outside:
                periods.append((t0, self.maxTime))
            self.drawPeriods(periods)
        elif parameter == "shocks":
            shocks = []
            prev = 0
            for content in cm.data:
                if content[5] != 2 and prev != 2:
                    continue
                elif content[5] != 2 and prev == 2:
                    if content[5] != 5:
                        prev = content[5]
                elif content[5] == 2 and prev == 2:
                    continue
                elif content[5] == 2 and prev != 2:
                    shocks.append(content[1])
                    prev = 2
            self.drawTimes(shocks)
        elif parameter == "entrances":
            entrances = []
            prev = 0
            for content in cm.data:
                if content[5] != 2 and prev != 2:
                    continue
                elif content[5] != 2 and prev == 2:
                    if content[5] == 0: 
                        prev = 0
                elif content[5] == 2 and prev == 2:
                    continue
                elif content[5] == 2 and prev != 2:
                    entrances.append(content[1])
                    prev = 2
            self.drawTimes(entrances)
        elif parameter == "bad points":
            if cm.interpolated:
                sortd = sorted(cm.interpolated)
                wrongs = []              
                prev = sortd[0]
                start = sortd[0]                
                for wrong in sortd[1:]:
                    if wrong != prev + 1:
                        wrongs.append((start, prev))
                        start = wrong
                    prev = wrong
                wrongs.append((start, prev))
                self.drawPeriods([(cm.data[wrong[0] - 1][1], cm.data[wrong[1] - 1][1]) for\
                                  wrong in wrongs])
                
                
            
    def drawGraph(self, maxY, valueList):
        """draws lines on a canvas based on maxY and valueList parameters
        maxY parameter sets maximum value at y-axis
        valueList parameter must be a list containing successive values depicted in the graph
        """
        maxX = len(valueList)
        for i in range(maxX - 1):
            x0 = (i / (maxX - 1)) * self.width
            x1 = ((i + 1) / (maxX - 1)) * self.width
            y0 = (1 - (valueList[i] / maxY)) * self.height
            y1 = (1 - (valueList[i + 1] / maxY)) * self.height
            self.create_line((x0, y0, x1, y1))
        self.lift("timeMeasure")
 


class SvgGraph():
    "represents graph to be saved in .svg file"
    def __init__(self, parent, cm):
        self.parent = parent

    
    def saveGraph(self, cm):
        "returns information about graph for saving in .svg file"
        self.maxTime = eval(self.parent.timeFrame.timeVar.get()) * 60000
        self.minTime = eval(self.parent.timeFrame.startTimeVar.get()) * 60000
        self.compute(cm)
        self.writeFurtherText()
        return self.points, self.maxY, self.furtherText



class SpeedGraph(Graphs, SvgGraph):
    "graph depicting speed during the session"
    def __init__(self, parent, cm = None, purpose = "graph"):
        if purpose == "graph":
            Graphs.__init__(self, parent)
        else:
            SvgGraph.__init__(self, parent, cm)


    def writeFurtherText(self):
        "makes text for svg file representing horizontal lines for every 10cm/s"
        self.furtherText = ""
        for y in range(1, floor(self.maxY / 10)):
            text = '<line stroke="lightgray" stroke-width="0.5" ' +\
                   'x1="0" y1="{0}" x2="600" y2="{0}"/>\n'.format(y * 10 * 120 / self.maxY)
            self.furtherText += text       


    def compute(self, CM, skip = 12, smooth = 2):
        """computes speeds
           parameter skip controls how many lines should be skipped when computing speed
           parameter smooth controls how many speed data points should be averaged
           e.g. when skip = 12 and smooth = 2, speed is computed as an average of two speeds
               computed from lines separated by 11 lines
        """
        resolution = CM.getTrackerResolution()

        # saving speed between every 'skip' data point ... in centimeters per second
        start = CM.findStart(self.minTime / 60000)
        self.speed = []
        x0, y0 = CM.data[start][7:9]
        t0 = CM.data[start][1]
        for line in CM.data[(start + skip)::skip]:
            x1, y1 = line[7:9]
            t1 = line[1]
            speed = ((((x1 - x0)**2 + (y1 - y0)**2)**0.5) / resolution) / ((t1 - t0) / 1000)
            self.speed.append(speed)
            if t1 >= self.maxTime:
                break
            x0, y0, t0 = x1, y1, t1

        # averaging speed across 'smooth' speed data points
        self.points = []
        avgSpeed = 0
        for smoothCounter, point in enumerate(self.speed, 1):
            avgSpeed += point
            if smoothCounter % smooth == 0:
                self.points.append((avgSpeed / smooth))
                avgSpeed = 0
        else:
            if avgSpeed != 0:
                self.points.append((avgSpeed / (smoothCounter % smooth)))

        # computing maximum speed depicted on y-axis
        maxSpeed = max(self.points)
        if round(maxSpeed, -1) <= maxSpeed:
            self.maxY = round(maxSpeed, -1) + 10
        else:
            self.maxY = round(maxSpeed, -1)

 
    def CM_loaded(self, CM, initTime = 0, minTime = 0, maxTime = "max"):
        """creates graph when CM file is loaded
           parameter initTime is the time of the player when the graph is initialized
        """
        super().CM_loaded(CM, minTime, maxTime, initTime)
        self.compute(CM)

        for y in range(1, floor(self.maxY / 10)):
            self.create_line((0, y*10 * self.height / self.maxY, self.width,
                              y*10 * self.height / self.maxY),  fill = "gray86")
        
        self.drawGraph(maxY = self.maxY, valueList = self.points)



class DistanceFromCenterGraph(Graphs, SvgGraph):
    "graph depicting distance from center of arena during the session"
    def __init__(self, parent, cm = None, purpose = "graph"):
        if purpose == "graph":
            Graphs.__init__(self, parent)
        else:
            SvgGraph.__init__(self, parent, cm)


    def writeFurtherText(self):
        "makes text for svg file containing info about line representing border of the arena"
        y = ((self.maxY - self.radius) / self.maxY) * 120
        self.furtherText = '<line stroke="gray" stroke-width="0.5" x1="0" ' +\
                           'y1="{0}" x2="600" y2="{0}"/>\n'.format(y)


    def compute(self, CM, smooth = 10):
        """computes distances from center of the graph
           parameter smooth controls how many data points should be averaged
        """
        start = CM.findStart(self.minTime / 60000)

        self.radius = CM.getComputedDiameter()
        Cx, Cy = CM.getCenterX(), CM.getCenterY()

        dists = [((line[2] - Cx)**2 + (line[3] - Cy)**2)**0.5 for line in CM.data[start:] if
                 line[1] <= self.maxTime]
        self.points = [(sum(dists[(i * smooth):((i * smooth) + smooth)]) / smooth) for i
                       in range(len(dists) // smooth)]       

        self.maxY = self.radius + 10
        

    def CM_loaded(self, CM, initTime = 0, minTime = 0, maxTime = "max"):
        """creates graph when CM file is loaded
           parameter initTime is the time of the player when the graph is initialized
        """
        super().CM_loaded(CM, minTime, maxTime, initTime)
        self.compute(CM)
        
        self.create_line((0, 10, self.width, 10), fill = "grey")

        self.drawGraph(maxY = self.maxY, valueList = self.points)
      


class AngleGraph(Graphs, SvgGraph):
    "graph depicting angle relative to the center of shock zone during the session"
    def __init__(self, parent, cm = None, purpose = "graph"):
        if purpose == "graph":
            Graphs.__init__(self, parent)
        else:
            SvgGraph.__init__(self, parent, cm)
            self.maxTime = eval(self.parent.timeFrame.timeVar.get()) * 60000
            self.minTime = eval(self.parent.timeFrame.startTimeVar.get()) * 60000
            

    def compute(self, cm):
        "computes angles of position relative to center"        
        start = cm.findStart(self.minTime / 60000)
        Cx, Cy = cm.getCenterX(), cm.getCenterY()
        CA = cm.getCenterAngle()

        # saving angles to a list        
        self.angles = []
        nxt = False
        prev = 180
        self.crosses = 0
        for line in cm.data[start:]:
            if line[1] > self.maxTime:
                break
            else:
                angle = (degrees(atan2(Cy - line[3], line[2] - Cx + 0.000001)) + 720 - CA) % 360
                if prev > 270 and angle < 90:
                    self.angles.append(360)
                    self.angles.append(0)
                    self.crosses += 1
                elif prev < 90 and angle > 270:
                    self.angles.append(0)
                    self.angles.append(360)
                    self.crosses += 1
                else:
                    self.angles.append(angle)                
                prev = angle        


    def CM_loaded(self, cm, initTime = 0, minTime = 0, maxTime = "max"):
        """creates graph when CM file is loaded
           parameter initTime is the time of the player when the graph is initialized
        """
        super().CM_loaded(cm, minTime, maxTime, initTime)
        
        self.compute(cm)

        wid = cm.getWidth()
        # drawing lines representing the sector
        y1 = ((360 - (wid / 2)) / 360) * self.height
        y2 = ((wid / 2) / 360) * self.height

        self.create_line((0, y1, self.width, y1), fill = "red")
        self.create_line((0, y2, self.width, y2), fill = "red")

        # drawing the graph
        maxX = len(self.angles) - self.crosses

        i = 0
        prev = self.angles[0]
        for angle in self.angles[1:]:
            x0 = (i / (maxX - 1)) * self.width
            x1 = ((i + 1) / (maxX - 1)) * self.width
            y0 = (1 - (prev / 360)) * self.height
            y1 = (1 - (angle / 360)) * self.height
            if (prev == 0 and angle == 360) or (prev == 360 and angle == 0):
                prev = angle
                continue
            prev = angle
            self.create_line((x0, y0, x1, y1))
            i += 1
            
        self.lift("timeMeasure")


    def saveGraph(self, cm):
        "returns information about graph for saving to .svg file"
        self.compute(cm)
        wid = cm.getWidth()

        size = (600, 120)

        maxX = len(self.angles) - self.crosses
        text = ""
        for i in (360 - (wid / 2), wid / 2):
            text += '<line stroke="red" stroke-width="0.5" ' +\
                    'x1="0" y1="{1}" x2="{0}" y2="{1}"/>\n'.format(size[0], i * size[1] / 360)
        
        points = []
        width = size[0]
        height = size[1]
        i = 0
        prev = self.angles[0]
        x0 = (i / (maxX - 1)) * width        
        y0 = (1 - (prev / 360)) * height
        points.append((x0, y0))
        for angle in self.angles[1:]:
            x0 = (i / (maxX - 1)) * width
            x1 = ((i + 1) / (maxX - 1)) * width
            y0 = (1 - (prev / 360)) * height
            y1 = (1 - (angle / 360)) * height
            if (prev == 0 and angle == 360) or (prev == 360 and angle == 0):
                prev = angle
                text += self._addLine(points)
                points = []
                points.append((x1, y1))
                continue
            prev = angle
            points.append((x1, y1))
            i += 1
        text += self._addLine(points)

        return None, None, text


    def _addLine(self, points):
        "returns line in a svg format joining points given as an argument"
        text = '<polyline points="'
        for pair in points:
            text += ",".join(map(str, pair)) + " "      
        text += '" style = "fill:none;stroke:black"/>\n'
        return text

