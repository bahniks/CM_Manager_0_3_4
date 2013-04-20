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

from math import degrees, atan2, sin, cos, pi, radians, sqrt
from collections import deque
import os.path
import os


from optionget import optionGet
from statistics import median



class CM:

    def __init__(self, nameA, nameR = "auto"):
        "class CM represents data from carousel maze"

        self.nameA = nameA
        
        # automatic room frame filename creation
        if nameR == "auto":
            splitname = os.path.split(nameA)
            if splitname[1].count("Arena") > 0:
                self.nameR = os.path.join(splitname[0], splitname[1].replace("Arena", "Room"))
            elif splitname[1].count("arena") > 0:
                self.nameR = os.path.join(splitname[0], splitname[1].replace("arena", "room"))
            else:
                raise IOError


        data = []

        # processing data from room frame    
        infile = open(self.nameR, "r")


        # processing header
        for line in infile:
            if line.count("TrackerVersion") > 0:
                if "iTrack" in line:
                    self.tracker = "iTrack"
                elif "Tracker" in line:
                    self.tracker = "Tracker"
                else:
                    self.tracker = "Unknown"
            elif line.count("ArenaCenterXY") > 0:
                strg = line.split()
                for i in range(len(strg)):
                    if strg[i] == "(":
                        pos = i
                self.centerX = eval(strg[pos+1])      
                self.centerY = eval(strg[pos+2])
            elif line.count("TrackerResolution_PixPerCM") > 0:
                strg = line.split()
                for i in range(len(strg)):
                    if strg[i] == "(":
                        pos = i
                self.trackerResolution = eval(strg[pos+1])  
            elif line.count("%ReinforcedSector") > 0 and line.count("//") == 0:
                # needs to be updated for double avoidance
                strg = line.split()
                for i in range(len(strg)):
                    if strg[i] == "(":
                        pos = i
                self.centerAngle = eval(strg[pos+1])   
                self.width = eval(strg[pos+2])         
                self.innerRadius = eval(strg[pos+3])
                self.outerRadius = eval(strg[pos+4])
            elif line.count("ArenaDiameter") > 0:
                strg = line.split()
                for i in range(len(strg)):
                    if strg[i] == "(":
                        pos = i
                self.arenaDiameter = eval(strg[pos+1])
            elif line.count("END_HEADER") > 0:
                break


        missing = []
        self.interpolated = set()

        count = -1
        for line in infile:
            count += 1
            line = list(map(int, line.split()[:7]))
            data.append(line)
           
            # missing points
            if count + 1 != line[0]:
                i = 2
                while True:
                    if data[-i][2] or data[-i][3]:
                        break
                    else:
                        i += 1
                before = data[-i][2:4]
                prev = data[-2]
                number = line[0] - count
                for row in range(1, number):
                    timeStamp = ((line[1] - prev[1]) / (number)) * row + prev[1]
                    filling = [count + 1, timeStamp, 0, 0] + prev[4:]
                    missing.append(count)
                    self.interpolated.add(count)
                    data.insert(-1, filling)
                    count += 1
                                     
            # wrong points
            if (line[2] != 0 or line[3] != 0) and missing == []:
                continue
            elif line[2] == 0 and line[3] == 0 and missing == []:
                if count != len(missing):
                    before = data[count - 1][2:4]
                    missing.append(count)
                    self.interpolated.add(count)
                else:
                    before = []
                    missing.append(count)
                    self.interpolated.add(count)
            elif line[2] == 0 and line[3] == 0 and missing != []:
                missing.append(count)
                self.interpolated.add(count)
            elif (line[2] != 0 or line[3] != 0) and missing != []:
                after = line[2:4]
                if before != []:
                    for missCounter, missLines in enumerate(missing, start=1):
                        data[missLines][2] = ((after[0] - before[0]) / (len(missing) + 1)) \
                                               * missCounter + before[0]
                        data[missLines][3] = ((after[1] - before[1]) / (len(missing) + 1)) \
                                               * missCounter + before[1]
                missing = []

        
        if missing != []:
            for missLines in missing:
                data[missLines][2:4] = before


        infile.close()

    
        # processing data from arena frame
        infile = open(nameA, "r")
      
        for line in infile:
            if line.count("END_HEADER") > 0:
                break


        missing = []

        count = -1
        for line in infile:
            count += 1
            line = list(map(int, line.split()[:7]))

            # missing points
            if count + 1 != line[0]:
                i = 1
                while True:
                    if data[count - i][7] or data[count - i][8]:
                        break
                    else:
                        i += 1
                before = data[count - i][7:9]
                prev = data[count - 2][9:]
                number = line[0] - count
                for row in range(1, number):
                    filling = [0, 0] + prev
                    missing.append(count)
                    self.interpolated.add(count)
                    data[count] += filling
                    count += 1
            

            data[count] += line[2:]

            # wrong points
            if (line[2] != 0 or line[3] != 0) and missing == []:
                 continue
            elif line[2] == 0 and line[3] == 0 and missing == []:
                if count != len(missing):
                    before = data[count - 1][7:9]
                    missing.append(count)
                    self.interpolated.add(count)
                else:
                    before = []
                    missing.append(count)
                    self.interpolated.add(count)
            elif line[2] == 0 and line[3] == 0 and missing != []:
                missing.append(count)
                self.interpolated.add(count)
            elif (line[2] != 0 or line[3] != 0) and missing != []:
                after = line[2:4]
                if before != []:
                    for missCounter, missLines in enumerate(missing, start=1):
                        data[missLines][7] = ((after[0] - before[0]) / (len(missing) + 1)) \
                                               * missCounter + before[0]
                        data[missLines][8] = ((after[1] - before[1]) / (len(missing) + 1)) \
                                               * missCounter + before[1]
                missing = []

        if missing != []:
            for missLines in missing:
                data[missLines][7:9] = before


        
        beginMiss = 0
        
        for line in data:
            if (line[2] == 0 and line [3] == 0) or (line[7] == 0 and line[8] == 0):
                beginMiss += 1
            else:
                if beginMiss != 0:
                    data = data[beginMiss:]
                    for i in range(len(data)):
                        data[i][0] -= beginMiss
                break

        infile.close()

        
        # exception used for example when all lines are wrong (all positions are 0, 0)
        if not data:
            raise Exception("Failure in data initialization.")

 


        # if some line is missing, it is skipped
        # if file begins with missing points, they are deleted
        # if file ends with missing points, position is imputed by the last available position
        # missing points inside file are imputed by linear approximation
        self.data = data

        

    def getCenterX(self):
        "returns x-coordinate of the center of the arena"
        return self.centerX
    
    def getCenterY(self):
        "returns y-coordinate of the center of the arena"
        return self.centerY
    
    def getCenterAngle(self):
        "returns angle of the center of the shock sector"
        try:
            angle = self.centerAngle
        except Exception:
            angle = None
        return angle
    
    def getWidth(self):
        "returns width of the shock sector"
        return self.width
    
    def getInnerRadius(self):
        "returns inner radius of the shock sector"
        return self.innerRadius
    
    def getOuterRadius(self):
        "returns outer radius of the shock sector"
        return self.outerRadius
    
    def getArenaDiameter(self):
        "returns diameter of the arena"
        return self.arenaDiameter

    def getTrackerResolution(self):
        "returns resolution of track in pixels per centimeter"
        return self.trackerResolution

    def getData(self):
        """returns data as a list - each row of a data file is represented by a list within
            the returned list
            each row contains following information:
            FrameCount(0) msTimeStamp(1) RoomX(2) RoomY(3) Sectors(4) State(5) CurrentLevel(6)...
                ...ArenaX(7) ArenaY(8) Sectors(9) State(10) CurrentLevel(11)
                - indexes are in parentheses
                - first two items are relevant to both arena and room frame
                    following 5 items are related to room frame and final 5 items are related
                    to arena frame
                - state info: OutsideSector = 0, EntranceLatency = 1, Shock = 2,
                              InterShockLatency = 3, OutsideRefractory = 4, BadSpot = 5
                - RoomX/Y, ArenaX/Y are coordinates in respective frames (in pixels)
                - sectors: 0 - no, 1 - room, 2 - arena, 3 - both
                - current level is in miliamperes
                - time stamp is in miliseconds
        """
        return self.data


    def getDistance(self, skip = 25, time = 20, startTime = 0, minDifference = 0):
        """computes total distance travelled (in metres),
        argument 'skip' controls how many rows are skipped in distance computation,
        argument 'time' is time of the session,
        """
        dist = 0
        time = time * 60000 # conversion from minutes to miliseconds
        start = self.findStart(startTime)
        x0, y0 = self.data[start][7:9] 
        for content in self.data[(start + skip)::skip]:
            if content[1] <= time:
                x1, y1 = content[7:9]
                diff = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
                if diff > minDifference:
                    dist += diff
                x0, y0 = x1, y1
        dist = dist / (self.trackerResolution * 100) # conversion from pixels to metres
        return round(dist, 2)

                
    def getMaxT(self, time = 20, startTime = 0, lastTime = "fromParameter"):
        """computes maximum time avoided (in seconds),
        argument 'time' is time of the session
        argument 'lastTime' decides whether the last time point is obtained from 'time' parameter
            or data
        """
        maxT = 0
        prev = 0
        start = self.findStart(startTime)
        timePrev = self.data[start][1]
        time = time * 60000 # conversion from minutes to miliseconds
        for content in self.data[start:]:
            if content[5] != 2 and prev != 2 and content[1] <= time:
                continue
            elif content[5] != 2 and prev == 2 and content[1] <= time:
                if content[5] == 4 or content[5] == 0:
                    prev = content[5]
                    timePrev = content[1]
                continue
            elif content[5] == 2 and prev == 2 and content[1] <= time:
                continue
            elif content[5] == 2 and prev != 2 and content[1] <= time:
                maxT = max(content[1] - timePrev, maxT)
                prev = 2
                continue
            elif content[1] > time:
                finalTime = content[1]
                break
        else:
            finalTime = self.data[-1][1]

        if lastTime == "fromData": # not used - may be added as an option in the future
            maxT = max(min(finalTime - timePrev, time - startTime), maxT)
        elif lastTime == "fromParameter":
            maxT = max(time - timePrev, maxT)

        maxT = maxT / 1000 # conversion from miliseconds to seconds
        return round(maxT, 1)

            
    def getT1(self, time = 20, startTime = 0, lastTime = "fromParameter"):
        """computes time to first shock (in seconds),
        argument 'time' is time of the session
        argument 'lastTime' decides whether the last time point is obtained from 'time' parameter
            or data
        """
        time = time * 60000 # conversion from minutes to miliseconds
        startTime = startTime * 60000
        start = self.findStart(startTime)
        T1 = 0
        for content in self.data[start:]:
            if content[5] != 2:
                continue
            elif content[5] == 2:
                T1 = content[1] - startTime
                break
            
        if T1 == 0 or T1 > time - startTime:
            if lastTime == "fromData": # not used - may be added as an option in the future
                T1 = min(time, self.data[-1][1]) - startTime
            elif lastTime == "fromParameter":
                T1 = time - startTime
                
        T1 = T1 / 1000 # conversion from miliseconds to seconds
        return round(T1, 1)


    def getShocks(self, time = 20, startTime = 0):
        """computes number of shocks,
        argument 'time' is time of the session
        """
        time = time * 60000 # conversion from minutes to miliseconds
        start = self.findStart(startTime)
        shocks = 0
        prev = 0
        for content in self.data[start:]:
            if content[5] != 2 and prev != 2 and content[1] <= time:
                continue
            elif content[5] != 2 and prev == 2 and content[1] <= time:
                if content[5] != 5:
                    prev = content[5]
                continue
            elif content[5] == 2 and prev == 2 and content[1] <= time:
                continue
            elif content[5] == 2 and prev != 2 and content[1] <= time:
                shocks += 1
                prev = 2
                continue
            elif content[1] > time:
                break
        return shocks


    def getEntrances(self, time = 20, startTime = 0):
        """computes number of entrances,
        argument 'time' is time of the session
        """
        time = time * 60000 # conversion from minutes to miliseconds
        start = self.findStart(startTime)
        entrances = 0
        prev = 0
        for content in self.data[start:]:
            if content[5] != 2 and prev != 2 and content[1] <= time:
                continue
            elif content[5] != 2 and prev == 2 and content[1] <= time:
                if content[5] == 0: 
                    prev = 0
                continue
            elif content[5] == 2 and prev == 2 and content[1] <= time:
                continue
            elif content[5] == 2 and prev != 2 and content[1] <= time:
                entrances += 1
                prev = 2
                continue
            elif content[1] > time:
                break
        return entrances


    def getComputedDiameter(self):
        """returns radius (sic!) of the arena in pixels computed as a maximum of center coordinates
            [misnamed]"""
        return max([self.centerX, self.centerY])


    def getThigmotaxis(self, time = 20, startTime = 0, percentSize = 20):
        """returns proportion of time that rat spent in the periphery of arena
            periphery is defined as 'percentSize' of radius
            argument 'time' is time of the session
            argument startTime is beginning of the analyzed time - it may be helpful to set it to
                different time then 0 in order to not confound the parameter by initial placement
        """
        border = self.getComputedDiameter() * (1 - (percentSize / 100))
        time = time * 60000
        start = self.findStart(startTime)
        
        periphery = 0
        center = 0
        
        for content in self.data[start:]:
            if content[1] <= time: 
                distance = ((content[2] - self.centerX)**2 + (content[3] - self.centerY)**2)**0.5
                if distance >= border:
                    periphery += 1
                else:
                    center += 1

        return round(periphery / (center + periphery), 3)


    def getAngleBoxes(self, time = 20, startTime = 0, boxWidth = "default", results = "condensed",
                      center = "target"):
        """returns proportion of time spent in angle boxes of width 'boxWidth' (provided in
                degreess)
            first item is centered in center of shock zone - by default it means that
                the first item represents proportion of time spent in the shock zone
            when boxWidth is not divisor of 360, last box corresponds to the degrees that are
                unaccounted for
        """
        if boxWidth == "default":
            boxWidth = self.width

        time = time * 60000
        start = self.findStart(startTime)

        if center == "target":
            sectorCenterAngle = self.centerAngle
        elif center == "opposite":
            sectorCenterAngle = self.centerAngle + 180
        else:
            sectorCenterAngle = self.centerAngle + center
  
        angles = [0] * int(360 / boxWidth)
        for content in self.data[start:]:
            if content[1] <= time:
                angle = (degrees(self._angle(content[2], content[3])) - sectorCenterAngle +
                         (boxWidth / 2) + 360) % 360
                angles[int(angle // boxWidth)] += 1

        boxes = [round((box / sum(angles)), 3) for box in angles]

        if results == "condensed":
            return ("|".join(map(str, boxes)))
        elif results == "list":
            return boxes


    def getTimeInTarget(self, time = 20, startTime = 0, width = "default"):
        "returns proportion of time spent in the target sector" 
        return self.getAngleBoxes(time = time, startTime = startTime, boxWidth = "default",
                             results = "list")[0]

        
    def getTimeInOpposite(self, time = 20, startTime = 0, width = "default"):
        "returns proportion of time spent in sector opposite to the target" 
        return self.getAngleBoxes(time = time, startTime = startTime, boxWidth = "default",
                             results = "list", center = "opposite")[0]


    def getTimeInChosenSector(self, width, center, time = 20, startTime = 0):
        """returns proportion of time spent in a chosen sector
            parameter width is the sector width
            parameter center is angle of the chosen sector relative to center of the target sector
        """
        return self.getAngleBoxes(time = time, startTime = startTime, boxWidth = width,
                             results = "list", center = center)[0]


    def _angle(self, x, y):
        "returns angle relative to center in radians"
        return atan2(self.centerY - y, x - self.centerX + 0.000001)


    def getDirectionalMean(self, time = 20, startTime = 0):
        "returns directional mean angle in room frame"
        time = time * 60000
        start = self.findStart(startTime)

        num = sum([sin(self._angle(content[2], content[3])) for content in self.data[start:] if
                   content[1] < time])
        den = sum([cos(self._angle(content[2], content[3])) for content in self.data[start:] if
                   content[1] < time])

        if den == 0:
            den = 0.000000001
            
        result = (degrees(atan2(num, den)) + 360) % 360

        return round(result, 2)


    def getCircularVariance(self, time = 20, startTime = 0):
        "return circular variance of angle in room frame (has values between 0 and 1 inclusive)"
        circMean = radians(self.getDirectionalMean(time, startTime))
        
        time = time * 60000
        start = self.findStart(startTime)

        R = sum([cos(self._angle(content[2], content[3]) - circMean) for content in
                 self.data[start:] if content[1] < time])
        
        circVar = 1 - R / len([1 for content in self.data[start:] if content[1] < time])

        return round(circVar, 2)


    def getMaxTimeOfImmobility(self, time = 20, startTime = 0, minSpeed = 10, skip = 12,
                               smooth = 2, forGraph = False):
        """returns maximum continuous time that the rat was immobile
            minSpeed argument is in cm/s, smooth and skip are represented in data points"""
        time = time * 60000
        start = self.findStart(startTime)
        t0 = startTime
        x0, y0 = self.data[start][7:9]
        speeds = deque()

        prev = t0
        maxIm = 0
        immobility = []
        
        for content in self.data[start+skip::skip]:
            if content[1] > time:
                break
            x1, y1 = content[7:9]
            t1 = content[1]
            speeds.append((sqrt(((x1 - x0)**2 + (y1 - y0)**2)) / self.trackerResolution) /
                          ((t1 - t0) / 1000))

            if len(speeds) == smooth:
                if sum(speeds) / len(speeds) > minSpeed:
                    maxIm = max(maxIm, t0 - prev)
                    if forGraph:
                        immobility.append((prev, t0))
                    prev = t1
                speeds.popleft()
                            
            x0, y0, t0 = x1, y1, t1
        
        maxIm = max(maxIm, t0 - prev)
        immobility.append((prev, t0))


        if forGraph:
            return immobility
        else:
            return round(maxIm / 60000, 2)


    def getPeriodicity(self, time = 20, startTime = 0, minSpeed = 10, skip = 12, smooth = 2,
                       minTime = 9, forGraph = False):
        """returns periodicity, which is computed as a median time between two consecutive
            moments when a rat was mobile - times where its speed was higher than minSpeed
            ... additionally only periods more than minTime seconds are counted in a result
            ... this parameter is probably useful only in cases where a rat is moving and learned
                the task properly
            // minTime may be a list of values
        """
        time = time * 60000
        start = self.findStart(startTime)
                
        result = []
        
        if type(minTime) != list:
            minTime = [minTime]

        moves = []
            
        for minT in minTime:
            t0 = startTime * 60000
            x0, y0 = self.data[start][7:9]
            minT *= 1000
            speeds = deque()
        
            prev = False
            periods = []
            for content in self.data[start+skip::skip]:
                if content[1] > time:
                    break
                x1, y1 = content[7:9]
                t1 = content[1]
                speeds.append((sqrt(((x1 - x0)**2 + (y1 - y0)**2)) / self.trackerResolution) /
                              ((t1 - t0) / 1000))

                if len(speeds) == smooth:
                    if sum(speeds) / len(speeds) > minSpeed:
                        if t0 - prev > minT and prev:
                            periods.append(t0 - prev)
                            if forGraph:
                                moves.append((prev, t0))
                        prev = t1
                    speeds.popleft()

                x0, y0, t0 = x1, y1, t1

            if len(periods) > 1:
                periodicity = round((median(periods) / 1000), 2)
            else:
                periodicity = "NA"

            result.append(periodicity)

            if forGraph:
                return moves

        return "|".join(map(str, result))


    def getPercentOfMobility(self, time = 20, startTime = 0, minSpeed = 5, skip = 12, smooth = 2):
        """returns proportion of time that the rat was moving
            minSpeed argument is in cm/s, smooth and skip are represented in data points"""
        time = time * 60000
        start = self.findStart(startTime)
        t0 = startTime
        x0, y0 = self.data[start][7:9]
        speeds = deque()

        mobile = 0
        immobile = 0
        
        for content in self.data[start+skip::skip]:
            if content[1] > time:
                break
            x1, y1 = content[7:9]
            t1 = content[1]
            speeds.append((sqrt(((x1 - x0)**2 + (y1 - y0)**2)) / self.trackerResolution) /
                          ((t1 - t0) / 1000))
            x0, y0, t0 = x1, y1, t1

            if len(speeds) == smooth:
                if sum(speeds) / len(speeds) > minSpeed:
                    mobile += 1
                else:
                    immobile += 1
                speeds.popleft()


        result = mobile / (mobile + immobile)

        return round(result, 3)


    def getMeanDistanceFromCenter(self, time = 20, startTime = 0):
        "returns mean distance from center in centimeters"
        time = time * 60000
        start = self.findStart(startTime)

        distances = [sqrt((content[7] - self.centerX)**2 + (content[8] - self.centerY)**2)
                     for content in self.data[start:] if content[1] < time]
        result = (sum(distances) / self.trackerResolution) / len(distances)

        return round(result, 2)


    def getSpeedAfterShock(self, time = 20, startTime = 0, after = 25):
        "returns direction that the rat travelled 'after' points after shock"
        time = time * 60000
        start = self.findStart(startTime)

        shocks = [content[0] for content in self.data[start:] if
                  content[5] == 2 and content[1] < time]
        if shocks:
            selected = [shocks[0]]
            prev = shocks[0]
            for shock in shocks[1:]:
                if shock - prev > after:
                    selected.append(shock)
                prev = shock
        else:
            return "NA"

        angles = []
        cx, cy = self.centerX, self.centerY
        for shock in selected:
            x1, y1 = self.data[shock][7:9]
            if len(self.data) <= shock + after:
                break
            x2, y2 = self.data[shock + after][7:9]
            angle = ((degrees(atan2(x2 - cx, y2 - cy + 0.0000001)) -
                      degrees(atan2(x1 - cx, y1 - cy + 0.0000001)) + 180) % 360) - 180
            angles.append(angle)
            
        return round(median(angles), 2)

        

    def findReflections(self, time = 20, startTime = 0, results = "both"):
        """finds possible reflections and returns either number of possible reflection points
        or their indices - which is true depends on 'results' argument ('summary' for the former
        and 'indices' for the latter)"
        both possible results are returned divided into points of concern and problematic points        
        """
        if time == "max":
            time = self.data[-1][1]
        else:
            time = time * 60000
        startTime = startTime * 60000

        x0, y0 = self.data[0][7:9]
        x1, y1 = self.data[1][7:9]
        t1 = self.data[1][1]
        angle1 = degrees(atan2(x1 - x0, y1 - y0 + 0.0000001)) + 180

        #reflectionInfo = []
        problem = []
        concern = []
        problemNum = 0
        concernNum = 0

        for content in self.data[2:]:
            x2, y2 = content[7:9]
            t2 = content[1]
            angle2 = degrees(atan2(x2 - x1, y2 - y1 + 0.0000001)) + 180

            speed = ((x2 - x1)**2 + (y2 - y1)**2)**0.5 / \
                    (self.trackerResolution * (t2 - t1) / 1000)

            angleDif = 180 - abs(abs(angle2 - angle1) - 180)

            info = (content[0], speed, angleDif) # speed (cm/s), angleDif (degrees)
                        
            if ((7/9) * abs(90 - info[2]) + (5/9) * info[2] - info[1]) < -180:
                problem.append(info[0])
                if startTime <= content[1] <= time:
                    problemNum += 1
            elif ((19/18) * abs(90 - info[2]) + (17/18) * info[2] - info[1]) < -155:
                concern.append(info[0])
                if startTime <= content[1] <= time:
                    concernNum += 1

            x0, y0 = x1, y1 # to tu asi neni potreba
            x1, y1 = x2, y2
            t1 = t2
            angle1 = angle2

        if results == "summary":
            return concernNum, problemNum
        elif results == "indices":
            return concern, problem
        elif results == "both":
            return concernNum, problemNum, concern, problem


    def _computeSpeed(self, row1, row2):
        speed = ((row1[7] - row2[7])**2 + (row1[8] - row2[8])**2)**0.5 / \
                ((abs(row2[1] - row1[1]) / 1000) * self.trackerResolution)
        return speed # cm/s

    def removeReflections(self, points = None, deleteSame = True):
        "removes reflections - hopefully"       
        # finding reflection points
        if points == None:
            points = self.findReflections(time = "max", startTime = 0, results = "indices")
            points = points[0] + points[1]

        rows = {point - 1 for point in points}

        # finds data points that share coordinates with more than two points with reflections      
        if deleteSame:
            # Arena
            occurences = set()
            toDeleteArena = set()
            for row in rows:
                position = tuple(self.data[row][7:9])
                if position in occurences:
                    toDeleteArena.add(position)
                    occurences.remove(position)
                elif position not in toDeleteArena:
                    occurences.add(position)
            # Room
            occurences = set()
            toDeleteRoom = set()
            for row in rows:
                position = tuple(self.data[row][2:4])
                if position in occurences:
                    toDeleteRoom.add(position)
                    occurences.remove(position)
                elif position not in toDeleteRoom:
                    occurences.add(position)

            addMissing = {row[0] - 1 for row in self.data if tuple(row[2:4]) in toDeleteRoom or\
                          tuple(row[7:9]) in toDeleteArena}
                 
        missing = sorted(rows | addMissing)

        # 'removal' itself
        while missing:           
            row = missing[0]

            j = 1
            while row - j in self.interpolated:
                if row - j not in missing:
                    missing.append(row - j)
                j += 1
            
            before = self.data[row - j]
            beforeID = row - j
            reflection = self.data[row]

            i = 1
            last = len(self.data)
            if row + i < last - 1:
                while row + i in missing or\
                      self._computeSpeed(self.data[row + i], before) > 250 or\
                      self.data[row + i][2:4] == self.data[row][2:4] or\
                      self.data[row + i][7:9] == self.data[row][7:9] or\
                      self._computeSpeed(reflection, self.data[row + i]) * 30 < \
                      self._computeSpeed(before, self.data[row + i]) or \
                      row + i in self.interpolated:
                      # conditions in order of appearance:
                      # large speed between the row and before row
                      # same position as in the reflection row
                      # we should expect the position to be closer to before row than to the
                      #    reflection row - determined by speed
                      # wrong points in the row
                    if row + i not in missing:
                        missing.append(row + i)
                    i += 1
                    # when the row-to-remove is the last one
                    if row + i == last - 1:
                        afterID = row + i
                        for count in range(1, afterID - beforeID):
                            rw = beforeID + count
                            self.data[rw][2:4] = before[2:4]           
                            self.data[rw][7:9] = before[7:9]
                            missing.remove(rw)
                        return
                after = self.data[row + i]
                afterID = row + i
            else:
                # when the row-to-remove is the last one
                for count, content in enumerate(self.data[row + i:]):
                    self.data[row + i + count][2:4] = before[2:4]
                    self.data[row + i + count][7:9] = before[7:9]
                return

            # the actual replacement of positions
            for count in range(1, afterID - beforeID):
                rw = beforeID + count
                self.data[rw][2] = ((after[2] - before[2]) / (afterID - beforeID)) \
                                    * (rw - beforeID) + before[2]
                self.data[rw][3] = ((after[3] - before[3]) / (afterID - beforeID)) \
                                    * (rw - beforeID) + before[3]                
                self.data[rw][7] = ((after[7] - before[7]) / (afterID - beforeID)) \
                                    * (rw - beforeID) + before[7]            
                self.data[rw][8] = ((after[8] - before[8]) / (afterID - beforeID)) \
                                    * (rw - beforeID) + before[8]
                missing.remove(rw)
    

    def countBadPoints(self, time = 20, startTime = 0):
        time *= 60000
        startTime *= 60000

        start = self.findStart(startTime)
        
        count = 0
        bad = 0
        for content in self.data[start:]:
            if content[1] > time:
                break
            else:
                count += 1
                if content[0] in self.interpolated:
                    bad += 1

        proportion = (bad / count) * 100
        
        return round(proportion, 2)


    def findJumpers(self, time = 20, startTime = 0):
        "returns number of data points where an animal was outside the arena"
        time = time * 60000
        start = self.findStart(startTime)

        diameter = self.getComputedDiameter()
        Cx, Cy = self.centerX, self.centerY        

        outside = 0
        for content in self.data[start:]:
            dist = ((content[7] - Cx)**2 + (content[8] - Cy)**2)**0.5
            if dist > diameter + 1 and content[1] <= time: # + 1 je o kolik pixelu musi byt dal
                                                           # ... dat to options
                outside += 1

        return outside


    def realMinimumTime(self):
        return self.data[0][1]


    def realMaximumTime(self):
        return self.data[-1][1]


    def roomFrameFilename(self):
        return self.nameR
            

        # self.data description
        """
        each row contains following information:
        FrameCount(0) msTimeStamp(1) RoomX(2) RoomY(3) Sectors(4) State(5) CurrentLevel(6)...
            ...ArenaX(7) ArenaY(8) Sectors(9) State(10) CurrentLevel(11)
            - indexes are in parentheses
            - first two items are relevant to both arena and room frame
                following 5 items are related to room frame and final 5 items are related
                to arena frame
            - state info: OutsideSector = 0, EntranceLatency = 1, Shock = 2,
                          InterShockLatency = 3, OutsideRefractory = 4, BadSpot = 5
            - RoomX/Y, ArenaX/Y are coordinates in respective frames (in pixels)
            - sectors: 0 - no, 1 - room, 2 - arena, 3 - both
            - current level is in miliamperes
            - time stamp is in miliseconds
        """
        

    def findStart(self, startTime):
        "help function for finding starting position for computing parameters"
        startTime = startTime * 60000

        for content in self.data:
            if content[1] < startTime:
                continue
            else:
                start = content[0] - 1
                break
        return start



class Parameters(list):
    "class containing list of parameters, their methods and options"
    def __init__(self):
        self.parameters = [["Total distance", """cm.getDistance(time = time, startTime = startTime,
                            skip = optionGet('StrideParTotalDistance', 25, 'int'), minDifference =
                            optionGet('MinDiffParTotalDistance', 0, ['int', 'float']))""",
                            "basic", optionGet("DefParDistance", True, "bool"), "DefParDistance"],
                      ["Maximum time avoided", "cm.getMaxT(time = time, startTime = startTime)",
                       "basic", optionGet("DefParMaxT", True, "bool"), "DefParMaxT"],
                      ["Entrances", "cm.getEntrances(time = time, startTime = startTime)", "basic",
                       optionGet("DefParEntrances", False, "bool"), "DefParEntrances"],
                      ["Time to first", "cm.getT1(time = time, startTime = startTime)", "basic",
                       optionGet("DefParT1", False, "bool"), "DefParT1"],
                      ["Shocks", "cm.getShocks(time = time, startTime = startTime)", "basic",
                       optionGet("DefParShocks", False, "bool"), "DefParShocks"],
                      ["Time in target sector", """cm.getTimeInTarget(time = time, startTime =
                        startTime)""", "basic", optionGet("DefParTimeInTarget", False, "bool"),
                       "DefParTimeInTarget"],
                      ["Time in opposite sector", """cm.getTimeInOpposite(time = time, startTime =
                        startTime)""", "basic", optionGet("DefParTimeInOpposite", False, "bool"),
                       "DefParTimeInOpposite"],
                      ["Time in chosen sector", """cm.getTimeInChosenSector(time = time,
                        startTime = startTime, width = optionGet('WidthParTimeInChosen', 'default',
                        ['int', 'float']), center = optionGet('AngleParTimeInChosen', 0, ['int',
                        'float']))""", "advanced", optionGet("DefParTimeInChosen", False, "bool"),
                       "DefParTimeInChosen"],
                      ["Time in sectors", """cm.getAngleBoxes(time = time, startTime = startTime,
                        results = 'condensed', boxWidth = optionGet('WidthParTimeInSectors',
                        'default', ['int', 'float']))""", "advanced",
                       optionGet("DefParSectors", False, "bool"), "DefParSectors"],
                      ["Thigmotaxis", """cm.getThigmotaxis(time = time, startTime = startTime,
                        percentSize = optionGet("ThigmotaxisPercentSize", 20,
                        ["int", "float"]))""", "advanced",
                       optionGet("DefParThigmotaxis", False, "bool"), "DefParThigmotaxis"],
                        ["Directional mean", """cm.getDirectionalMean(time = time, startTime =
                        startTime)""", "advanced", optionGet("DefParDirectionalMean", False,
                                                             "bool"), "DefParDirectionalMean"],
                        ["Circular variance", """cm.getCircularVariance(time = time, startTime =
                        startTime)""", "advanced", optionGet("DefParCircularVariance", False,
                                                             "bool"), "DefParCircularVariance"],
                        ["Maximum time of immobility", """cm.getMaxTimeOfImmobility(time = time,
                        startTime = startTime, minSpeed = optionGet('MinSpeedMaxTimeImmobility',
                        10, ['int', 'float']), skip = optionGet('SkipMaxTimeImmobility', 12,
                        ['int']), smooth = optionGet('SmoothMaxTimeImmobility', 2,
                        ['int']))""", "experimental",
                         optionGet("DefParMaxTimeImmobility", False, "bool"),
                         "DefParMaxTimeImmobility"],
                        ["Periodicity", """cm.getPeriodicity(time = time, startTime = startTime,
                         minSpeed = optionGet('MinSpeedPeriodicity', 10, ['int', 'float']),
                         skip = optionGet('SkipPeriodicity', 12, ['int']),
                         smooth = optionGet('SmoothPeriodicity', 2, ['int']),
                         minTime = optionGet('MinTimePeriodicity', 9, ['int', 'float',
                         'list']))""", "experimental",
                         optionGet("DefParPeriodicity", False, "bool"), "DefParPeriodicity"],
                        ["Proportion of time moving", """cm.getPercentOfMobility(time = time,
                        startTime = startTime, minSpeed = optionGet('MinSpeedPercentMobility',
                        5, ['int', 'float']), skip = optionGet('SkipPercentMobility', 12,
                        ['int']), smooth = optionGet('SmoothPercentMobility', 2,
                        ['int']))""", "experimental",
                         optionGet("DefParPercentMobility", False, "bool"),
                         "DefParPercentMobility"],
                        ["Mean distance from center", """cm.getMeanDistanceFromCenter(time = time,
                        startTime = startTime)""", "advanced",
                         optionGet("DefParMeanDistanceFromCenter", False, "bool"),
                         "DefParMeanDistanceFromCenter"],                           
                        ["Angle of target sector", "cm.getCenterAngle()", "info",
                         optionGet("DefParCenterAngle", False, "bool"), "DefParCenterAngle"],    
                        ["Width of target sector", "cm.getWidth()", "info",
                         optionGet("DefParSectorWidth", False, "bool"), "DefParSectorWidth"],
                        ["Real minimum time", "cm.realMinimumTime()", "info",
                         optionGet("DefParRealMinTime", False, "bool"), "DefParRealMinTime"],
                        ["Real maximum time", "cm.realMaximumTime()", "info",
                         optionGet("DefParRealMaxTime", False, "bool"), "DefParRealMaxTime"],
                        ["Room frame filename", "cm.roomFrameFilename()", "info",
                         optionGet("DefParRoomFrameFilename", False, "bool"),
                         "DefParRoomFrameFilename"],
                        ["Median speed after shock", """cm.getSpeedAfterShock(time = time, 
                        startTime = startTime, after = optionGet('SkipSpeedAfterShock', 25,
                        ['int']))""", "experimental", optionGet("DefParSpeedAfterShock", False,
                                                                "bool"), "DefParSpeedAfterShock"]
                      ]
        
        self.options = {"Total distance": (("Computed from every [skip in rows]",
                                            optionGet('StrideParTotalDistance', 25, 'int')),
                                           ("Minimal distance counted [in pixels]",
                                            optionGet('MinDiffParTotalDistance', 0,
                                                      ['int', 'float']))),
                        "Thigmotaxis": [("Annulus width [percent of radius]",
                                         optionGet("ThigmotaxisPercentSize", 20,
                                                   ["int", "float"]))],
                        "Time in chosen sector": (("Center of sector relative to the target " +
                                                   "[in degrees]",
                                                   optionGet('AngleParTimeInChosen', 0,
                                                             ['int', 'float'])),
                                                  ("Width of sector ('default' if same as " +
                                                   "target; otherwise in degrees)",
                                                   optionGet('WidthParTimeInChosen', 'default',
                                                             ['int', 'float']))),
                        "Time in sectors": [("Width of sector ('default' if same as target; " +
                                             "otherwise in degrees)",
                                             optionGet('WidthParTimeInSectors', 'default',
                                                       ['int', 'float']))],
                        "Maximum time of immobility": [("Minimum speed counted [in cm/s]",
                                                        optionGet('MinSpeedMaxTimeImmobility',
                                                                  10, ['int', 'float'])),
                                                       ("Computed from every [skip in rows]",
                                                        optionGet('SkipMaxTimeImmobility', 12,
                                                                  ['int'])),
                                                       ("Averaged across [intervals]",
                                                        optionGet('SmoothMaxTimeImmobility', 2,
                                                                  ['int']))],
                        "Periodicity": [("Minimum speed counted [in cm/s]",
                                         optionGet('MinSpeedPeriodicity', 10, ['int', 'float'])),
                                        ("Computed from every [skip in rows]",
                                         optionGet('SkipPeriodicity', 12, ['int'])),
                                        ("Averaged across [intervals]",
                                         optionGet('SmoothPeriodicity', 2, ['int'])),
                                        ("Minimum time of interval [in seconds]",
                                         optionGet('MinTimePeriodicity', 9, ['int', 'float',
                                                                             'list']))],
                        "Proportion of time moving": [("Minimum speed counted [in cm/s]",
                                                        optionGet('MinSpeedPercentMobility',
                                                                  5, ['int', 'float'])),
                                                       ("Computed from every [skip in rows]",
                                                        optionGet('SkipPercentMobility', 12,
                                                                  ['int'])),
                                                       ("Averaged across [intervals]",
                                                        optionGet('SmoothPercentMobility', 2,
                                                                  ['int']))],
                        "Median speed after shock": [("Computed from every [skip in rows]",
                                                      optionGet('SkipSpeedAfterShock', 25,
                                                                ['int']))]                                                  
                        }

        self.findParameters()
        

    def findParameters(self):
        "finds custom written parameters"
        for file in os.listdir(os.path.join(os.getcwd(), "Stuff", "Parameters")):
            splitted = os.path.splitext(file)
            omit = ["__init__", "template"]
            if len(splitted) > 1 and splitted[1] == ".py" and splitted[0] not in omit:
                exec("from Stuff.Parameters import {}".format(splitted[0]))
                option = "DefParCustom{}".format(
                    eval("{}.name".format(splitted[0])).strip().replace(" ", ""))
                newParameter = [eval("{}.name".format(splitted[0])),
                                "{}.parameter(cm, time = time, startTime = startTime)".format(
                                    splitted[0]), "custom", optionGet(option, False, "bool"),
                                option, splitted[0]]
                self.parameters.append(newParameter)                                         
                        



def main():
    cm = CM("rd6r6_Arena.dat")
    cm.removeReflections()

    

if __name__ == "__main__": main()

