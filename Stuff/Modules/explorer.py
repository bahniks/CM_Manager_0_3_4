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
from time import time
from math import cos, sin, radians, degrees, atan2, floor

import os
import os.path


from cm import CM
from filestorage import FileStorageFrame
from commonframes import TimeFrame, returnName
from image import SVG
from processor import ProgressWindow
from optionget import optionGet
from graphs import getGraphTypes, Graphs, SvgGraph, SpeedGraph, DistanceFromCenterGraph, AngleGraph



class Explorer(ttk.Frame):
    "represents ''Explore' page in the main window notebook"
    def __init__(self, root):
        super().__init__(root)
        
        self["padding"] = (10, 10, 12, 12)

        self.animate = "stop"
        self.initialized = False
        self.root = root
        self.fileStorage = self.root.fileStorage

        # variables
        self.status = StringVar()
        self.curTime = DoubleVar()
        self.speed = DoubleVar()
        self.graphTypeVar = StringVar()
        self.distanceVar = StringVar()
        self.entrancesVar = StringVar()
        self.timeVar = StringVar()
        self.totDistanceVar = StringVar()
        self.totEntrancesVar = StringVar()
        self.showTrackVar = BooleanVar()
        self.removeReflectionsVar = BooleanVar()
        self.showShocksVar = BooleanVar()
        self.saveWhatVar = StringVar()
        self.saveWhichFilesVar = StringVar()

        self.curTime.set(0)
        self.speed.set(1.0)
        self.graphTypeVar.set("SpeedGraph(self)")
        self.showTrackVar.set(False)
        self.removeReflectionsVar.set(False)
        self.showShocksVar.set(True)
        self.saveWhatVar.set("both frames")
        self.saveWhichFilesVar.set("current")
        
        
        # frames
        self.controlsLF = ttk.Labelframe(self, text = "Controls")
        self.graphLF = ttk.Labelframe(self, text = "Graph")
        self.fileStorageFrame = FileStorageFrame(self, parent = "explorer")
        self.fileFrame = FileFrame(self)
        self.parametersLF = ttk.LabelFrame(self, text = "Parameters")
        self.timeLabFrame = ttk.Labelframe(self, text = "Time")
        self.timeLabFrame.root = self
        self.timeFrame = TimeFrame(self.timeLabFrame, onChange = True)
        self.arenaFrame = ttk.LabelFrame(self, text = "Arena frame")
        self.roomFrame = ttk.LabelFrame(self, text = "Room frame")
        self.speedScaleFrame = ttk.Frame(self)
        self.speedScaleFrame.rowconfigure(0, weight = 1)
        self.optionsLF = ttk.LabelFrame(self, text = "Options")
        self.saveImagesLF = ttk.LabelFrame(self, text = "Save image(s)")
        
        # canvases
        self.arenaCanv = Canvas(self.arenaFrame, background = "white", height = 300, width = 300)
        self.roomCanv = Canvas(self.roomFrame, background = "white", height = 300, width = 300)

        # buttons
        self.playBut = ttk.Button(self.controlsLF, text = "Play", command = self.playFun,
                                  state = "disabled")
        self.pauseBut = ttk.Button(self.controlsLF, text = "Pause", command = self.pauseFun,
                                   state = "disabled")
        self.stopBut = ttk.Button(self.controlsLF, text = "Stop", command = self.stopFun,
                                  state = "disabled")
        self.saveBut = ttk.Button(self.saveImagesLF, text = "Save", command = self.saveImages,
                                  state = "disabled")

        # checkbuttons
        self.removeReflections = ttk.Checkbutton(self.optionsLF, text = "Remove reflections",
                                                 variable = self.removeReflectionsVar,
                                                 command = self.toggleReflections)
        self.showShocks = ttk.Checkbutton(self.optionsLF, text = "Show shocks",
                                          variable = self.showShocksVar,
                                          command = self.toggleShocks)

        # radiobutton
        self.showTrack = ttk.Radiobutton(self.optionsLF, text = "Show track",
                                         variable = self.showTrackVar, value = True,
                                         command = self.toggleAnimation)
        self.showAnimation = ttk.Radiobutton(self.optionsLF, text = "Show animation",
                                             variable = self.showTrackVar, value = False,
                                             command = self.toggleAnimation)
        
        
        # label
        self.statusBar = ttk.Label(self, textvariable = self.status)
        self.distance = ttk.Label(self.parametersLF, textvariable = self.distanceVar, width = 10,
                                  anchor = "e")
        self.entrances = ttk.Label(self.parametersLF, textvariable = self.entrancesVar, width = 10,
                                   anchor = "e")
        self.timePar = ttk.Label(self.parametersLF, textvariable = self.timeVar, width = 10,
                                 anchor = "e")
        self.totDistance = ttk.Label(self.parametersLF, textvariable = self.totDistanceVar,
                                     width = 10, anchor = "e")
        self.totEntrances = ttk.Label(self.parametersLF, textvariable = self.totEntrancesVar,
                                     width = 10, anchor = "e")
        self.distanceLab = ttk.Label(self.parametersLF, text = "Distance [m]", width = 11,
                                     anchor = "w")
        self.entrancesLab = ttk.Label(self.parametersLF, text = "Entrances", width = 11,
                                      anchor = "w")
        self.timeLab = ttk.Label(self.parametersLF, text = "Time", width = 11, anchor = "w")
        self.currentLab = ttk.Label(self.parametersLF, text = "Current", width = 10,
                                    anchor = "e")
        self.totalLab = ttk.Label(self.parametersLF, text = "Total", width = 10,
                                  anchor = "e")
        self.saveWhatLab = ttk.Label(self.saveImagesLF, text = "Save")
        self.saveWhichFilesLab = ttk.Label(self.saveImagesLF, text = "File(s)")

        # scales
        self.timeSc = ttk.Scale(self, orient = HORIZONTAL, from_ = 0, to = 100,
                                variable = self.curTime, command = self.changedTime)
        self.speedSc = ttk.Scale(self.speedScaleFrame, orient = VERTICAL, from_ = 50, to = 0.5,
                                 variable = self.speed, command = self.changedSpeed)
        
        # entry
        self.speedEntry = ttk.Entry(self.speedScaleFrame, textvariable = self.speed, width = 4,
                                    justify = "right", state = "readonly")
        
        # graph
        self.graph = eval(self.graphTypeVar.get())
        self.graph.bind("<Button-1>", self.graphClick)
        self.graph.bind("<Button-3>", self.graphPopUp)

        # combobox
        self.saveWhatCombo = ttk.Combobox(self.saveImagesLF, textvariable = self.saveWhatVar,
                                          justify = "center", width = 15, state = "readonly")
        self.saveWhatCombo["values"] = ("arena frame", "room frame", "both frames",
                                        "graph", "all")
        self.saveWhichFilesCombo = ttk.Combobox(self.saveImagesLF, textvariable =
                                                self.saveWhichFilesVar, justify = "center",
                                                width = 15, state = "readonly")
        self.saveWhichFilesCombo["values"] = ("current", "tagged", "untagged", "all")

        # adding to grid        
        self.controlsLF.grid(column = 0, row = 3, columnspan = 2, sticky = (N, W), pady = 2,
                             padx = 2)
        self.graphLF.grid(column = 0, row = 5, columnspan = 1, pady = 2, padx = 2, sticky = (N, W))
        self.fileStorageFrame.grid(column = 8, row = 0, pady = 2, padx = 3, sticky = (N, W))
        self.fileFrame.grid(column = 8, row = 1, rowspan = 4, padx = 3, sticky = (N, S))
        self.parametersLF.grid(column = 3, row = 3, columnspan = 3)
        self.timeLabFrame.grid(column = 2, row = 5, columnspan = 3, sticky = (W, N), pady = 2)        
        self.timeFrame.grid(column = 0, row = 0)
        self.arenaFrame.grid(column = 0, row = 0, rowspan = 2, columnspan = 3,
                             sticky = (N, S, E, W), padx = 2, pady = 2)
        self.roomFrame.grid(column = 3, row = 0, rowspan = 2, columnspan = 4,
                            sticky = (N, S, E, W), padx = 2, pady = 2)
        self.speedScaleFrame.grid(column = 7, row = 0, rowspan = 2, sticky = (N, S), padx = 4,
                                  pady = 2)
        self.optionsLF.grid(column = 5, row = 5, columnspan = 2, sticky = (N, W), pady = 2)
        self.saveImagesLF.grid(column = 8, row = 5, sticky = (S), pady = 5)
        
        self.arenaCanv.grid(column = 0, row = 0, padx = 1, pady = 1)
        self.roomCanv.grid(column = 0, row = 0, padx = 1, pady = 1)
        self.graph.grid(column = 0, row = 4, columnspan = 7, padx = 2, pady = 5, sticky = (E, W))
        
        self.playBut.grid(column = 0, row = 0, sticky = (N, S), padx = 2, pady = 2)
        self.pauseBut.grid(column = 1, row = 0, sticky = (N, S), padx = 2, pady = 2)
        self.stopBut.grid(column = 2, row = 0, sticky = (N, S), padx = 2, pady = 2)
        self.saveBut.grid(column = 1, row = 2, sticky = E)

        self.removeReflections.grid(column = 0, row = 2, padx = 2, pady = 2, sticky = (N, W))
        self.showShocks.grid(column = 0, row = 3, padx = 2, pady = 2, sticky = (N, W))

        self.showAnimation.grid(column = 0, row = 0, padx = 2, pady = 1, sticky = (N, W))
        self.showTrack.grid(column = 0, row = 1, padx = 2, pady = 1, sticky = (N, W))
        
        self.speedEntry.grid(column = 0, row = 1)

        self.statusBar.grid(column = 0, row = 6, columnspan = 7, sticky = (S, E, W), padx = 2,
                       pady = 2)
        self.distance.grid(column = 1, row = 1, sticky = E)
        self.entrances.grid(column = 1, row = 2, sticky = E)
        self.timePar.grid(column = 1, row = 3, sticky = E)
        self.totDistance.grid(column = 2, row = 1, sticky = E, padx = 4)
        self.totEntrances.grid(column = 2, row = 2, sticky = E, padx = 4)
        self.distanceLab.grid(column = 0, row = 1, sticky = E)
        self.entrancesLab.grid(column = 0, row = 2, sticky = E)
        self.timeLab.grid(column = 0, row = 3, sticky = E)
        self.currentLab.grid(column = 1, row = 0, sticky = E, padx = 2, pady = 2)
        self.totalLab.grid(column = 2, row = 0, sticky = E, padx = 4, pady = 2)
        self.saveWhatLab.grid(column = 0, row = 0, padx = 2, sticky = E)
        self.saveWhichFilesLab.grid(column = 0, row = 1, padx = 2, sticky = E)

        self.timeSc.grid(column = 0, row = 2, columnspan = 7, sticky = (E, W), pady = 4, padx = 2)
        self.speedSc.grid(column = 0, row = 0, sticky = (N, S, E, W), pady = 3)

        self.saveWhatCombo.grid(column = 1, row = 0)
        self.saveWhichFilesCombo.grid(column = 1, row = 1)


        # checkbuttons for graph
        for number, gType in enumerate(getGraphTypes()):
            ttk.Radiobutton(self.graphLF, text = gType[0], variable = self.graphTypeVar,
                            command = self.changedGraph, value = gType[1])\
                            .grid(row = number, pady = 2, padx = 1, sticky = (W))


    def saveImages(self):
        "saves images for selected files"
        files = self._returnSelectedFiles()

        if len(files) > 1:
            progress = ProgressWindow(self, len(files), text = "saved")
        elif len(files) == 1:
            self.root.config(cursor = "wait")
            self.root.update()
        elif len(files) == 0:
            self.status.set("No file selected.")
            self.bell()
            return

        problems = 0
        for filename in files:
            try:
                if filename in self.fileStorage.pairedfiles:
                    cm = CM(filename, nameR = self.fileStorage.pairedfiles[filename])
                else:
                    cm = CM(filename, nameR = "auto")
                if self.removeReflectionsVar.get():
                    cm.removeReflections(points = self.fileStorage.reflections.get(filename, None))
                self.saveOneImage(cm, filename)               
            except Exception:
                problems += 0

            if len(files) > 1:
                progress.addOne()

        if len(files) > 1:
            progress.destroy()
            if problems > 1:
                self.status.set("{} problems occured!".format(problems))
                self.bell()
            elif problems == 1:
                self.status.set("One problem occured!")
                self.bell()
            else:
                self.status.set("Images were saved.")
        else:
            if problems:
                self.status.set("A problem occured!")
                self.bell()
            else:
                self.status.set("Image was saved.")
            self.root.config(cursor = "")


    def saveOneImage(self, cm, filename):
        "saves image for one file"
        directory = optionGet("ImageDirectory", os.getcwd(), "str")
        # pridat moznost scale u vsech SVG
        
        what =  self.saveWhatVar.get()    

        if what == "both frames":
            self.svg = SVG(600, 300)
            self.saveArenaFrame(cm)
            self.saveRoomFrame(cm, origin = (300, 0))
        elif what == "arena frame":
            self.svg = SVG(300, 300) 
            self.saveArenaFrame(cm)
        elif what == "room frame":
            self.svg = SVG(300, 300)
            self.saveRoomFrame(cm)
        elif what == "graph":
            self.svg = SVG(600, 120)
            self.saveGraph(cm)
        elif what == "all":
            self.svg = SVG(600, 420)
            self.saveArenaFrame(cm)
            self.saveRoomFrame(cm, origin = (300, 0))
            self.saveGraph(cm, origin = (0, 300))
            
        self.svg.save(os.path.join(directory, os.path.splitext(os.path.basename(filename))[0] +
                                   "_" + what.replace(" ", "_") + ".svg")) # upravit
            

    def saveArenaFrame(self, cm, origin = (0, 0)):
        "saves info about arena frame in self.svg"
        self.svg.drawAAPA(cm, frame = "arena", startTime = int(self.timeFrame.startTimeVar.get()),
                         time = int(self.timeFrame.timeVar.get()), boundary = True,
                         sector = False, shocks = False, origin = origin) # dat do options


    def saveRoomFrame(self, cm, origin = (0, 0)):
        "saves info about room frame in self.svg"
        self.svg.drawAAPA(cm, frame = "room", startTime = int(self.timeFrame.startTimeVar.get()),
                         time = int(self.timeFrame.timeVar.get()), boundary = True,
                         sector = True, shocks = True, origin = origin)


    def saveGraph(self, cm, origin = (0, 0)):
        "saves info about graph in self.svg"
        size = (600, 120)
        graph = eval(self.graphTypeVar.get()[:-1] + ', cm, purpose = "svg")')
        yCoordinates, maxY, furtherText = graph.saveGraph(cm)
        points = []
        if yCoordinates:
            length = len(yCoordinates) - 1
            for count, y in enumerate(yCoordinates):       
                points.append(((count * size[0]) / length, size[1] - ((y * size[1]) / maxY)))
        self.svg.drawGraph(points, furtherText = furtherText, origin = origin, boundary = True)


    def _returnSelectedFiles(self):
        "returns files that are chosen for creating of images"
        which = self.saveWhichFilesVar.get()
        
        files = []
        if which == "all":
            files.extend(self.fileStorage.arenafiles)
        elif which == "tagged":
            files.extend(self.fileStorage.tagged)
        elif which == "untagged":
            files.extend([file for file in self.fileStorage.arenafiles if file not in
                          self.fileStorage.tagged])
        elif which == "current":
            files = [self.fileFrame.selected]

        return files
            

    def toggleAnimation(self):
        "called when checkbutton for showing tracks is toggled"
        if self.initialized:          
            self.initializeFile(self.fileFrame.selected, new = False, timeReset = False)


    def toggleReflections(self):
        "called when reflections removal is changed - just refreshes canvases"
        if self.initialized:          
            if self.removeReflectionsVar.get():
                self.cm.removeReflections(points = self.fileStorage.reflections.get(self.cm.nameA,
                                                                                    None))
                self.data = self.cm.getData()
                self.initializeFile(self.fileFrame.selected, new = False, timeReset = False)
            else:
                self.initializeFile(self.fileFrame.selected, new = True, timeReset = False)


    def toggleShocks(self):
        "called when checkbutton for showing shocks is toggled"
        if self.initialized and self.showTrackVar.get():
            self.initializeFile(self.fileFrame.selected, new = False, timeReset = False)                    
            

    def playFun(self):
        "starts animation"        
        self.timeFrame.changeState("disabled")
        self.showTrack["state"] = "disabled"
        self.saveBut.state(["disabled"])
        self.animate = "" # status of the animation - '', 'pause', 'stop'
        
        prevTime = time()
        while not self.animate:
            # finds current time
            nowTime = time()
            difTime = (nowTime - prevTime) * 1000
            playTime = difTime * self.speed.get() + (
                self.curTime.get() * (self.maxTime - self.minTime) / 100) + self.minTime

            if playTime > self.maxTime:
                self.curTime.set(100)
                self.timeVar.set(self._timeFormat(self.maxTime))  
                self.animate = "stop"
                self.timeFrame.changeState("!disabled")
                self.showTrack["state"] = "!disabled"
                self.saveBut.state(["!disabled"])
                break

            self.changedTime(playTime, unit = "ms")

            prevTime = nowTime


    def changedTime(self, value, unit = "0-100"):
        "called when time is changed"
        if not self.initialized or self.minTime > self.maxTime or self.maxTime < self.minTime:
            return
        
        if unit == "ms":
            value = value
        else:
            value = ((float(value) * (self.maxTime - self.minTime)) / 100) + self.minTime
        
        # finds current line in data and computes current distance and entrances            
        x0, y0 = self.data[0][7:9] 
        dist = 0
        entrances = 0
        prev = 0
        skip = 25 # z options
        start = self.cm.findStart(self.minTime / 60000)
        for row, content in enumerate(self.data[start:]):
            if content[1] < value:
                # distance
                if row % skip == 0:
                    x1, y1 = content[7:9]
                    diff = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
                    dist += diff
                    x0, y0 = x1, y1
                # entrances
                if content[5] != 2 and prev != 2:
                    continue
                elif content[5] != 2 and prev == 2:
                    if content[5] == 0: 
                        prev = 0
                    continue
                elif content[5] == 2 and prev == 2:
                    continue
                elif content[5] == 2 and prev != 2:
                    entrances += 1
                    prev = 2
                    continue
            else:
                curLine = content
                break
        dist = dist / (self.cm.trackerResolution * 100) # conversion from pixels to metres
        self.distanceVar.set("{:.1f}".format(dist))
        self.entrancesVar.set(entrances)

        Rx, Ry = curLine[2:4]
        Ax, Ay = curLine[7:9]                              

        # changes position of 'the rat'
        self.arenaCanv.coords("ratA", (Ax + self.ld, Ay + self.ld,\
                                Ax + self.ur, Ay + self.ur))
        self.roomCanv.coords("ratR", (Rx + self.ld, Ry + self.ld,\
                                Rx + self.ur, Ry + self.ur))

        # changes color of 'the rat' in case of shock
        if curLine[6] > 0:
            self.roomCanv.itemconfigure("ratR", fill = "red", outline = "red")
            self.shock = True
        elif self.shock and curLine[6] <= 0:
            self.roomCanv.itemconfigure("ratR", fill = "black", outline = "black")
            self.shock = False       

        self.graph.changedTime(value)

        # changes position of a time scale               
        if value < self.maxTime:
            self.curTime.set(((value - self.minTime) * 100) / (self.maxTime - self.minTime))
            self.timeVar.set(self._timeFormat(value))  
        else:
            self.curTime.set(100)
            self.timeVar.set(self._timeFormat(self.maxTime))          

        self.update()

            
    def setTime(self):
        "called when maximum or minimum time is set"
        if self.initialized:
            nowTime = (self.curTime.get() / 100) * (self.maxTime - self.minTime) + self.minTime
            self.initializeFile(self.fileFrame.selected, new = False)
            if self.minTime <= nowTime <= self.maxTime:
                self.graph.changedTime(nowTime)
                self.changedTime(nowTime, unit = "ms")
            elif self.minTime > nowTime:
                self.graph.changedTime(self.minTime)
                self.changedTime(self.minTime, unit = "ms")
            else:
                self.graph.changedTime(self.maxTime)
                self.changedTime(self.maxTime, unit = "ms")
            

    def pauseFun(self):
        "pauses and unpauses animation"
        if self.animate == "pause":
            self.timeFrame.changeState("disabled")
            self.showTrack["state"] = "disabled"
            self.saveBut.state(["disabled"])
            self.playFun()
        else:
            self.animate = "pause"
            self.timeFrame.changeState("!disabled")        
            self.showTrack["state"] = "!disabled"
            self.saveBut.state(["!disabled"])
            

    def stopFun(self):
        "stops animation"
        self.animate = "stop"
        self.changedTime(0)
        self.timeFrame.changeState("!disabled")          
        self.showTrack["state"] = "!disabled"
        self.saveBut.state(["!disabled"])
        

    def initializeFile(self, filename, new = True, timeReset = True):
        "initializes canvases, graph, etc."
        if new:
            try:
                if filename in self.fileStorage.pairedfiles:
                    self.cm = CM(filename, nameR = self.fileStorage.pairedfiles[filename])
                else:
                    self.cm = CM(filename, nameR = "auto")
                if self.removeReflectionsVar.get():
                    self.cm.removeReflections(points = self.fileStorage.reflections.get(filename,
                                                                                        None))
                self.data = self.cm.getData()
            except Exception as e:
                if optionGet("Developer", False, 'bool'):
                    print(e)
                self.status.set("File failed to load!")
                self.bell()
                return

  
        # initialization of canvases
        self.arenaCanv.delete("all")
        self.roomCanv.delete("all")
        
        d = self.cm.getComputedDiameter()
        self.arenaCanv.create_oval(150 - d, 150 - d, 150 + d, 150 + d, outline = "black",\
                                   width = 2, tags = "arenaAF")
        self.roomCanv.create_oval(150 - d, 150 - d, 150 + d, 150 + d, outline = "black",\
                                  width = 2, tags = "arenaRF")

       
        # creates lines depicting the shock sector
        if self.cm.getCenterAngle():
            self.angle = self.cm.getCenterAngle()
            self.width = self.cm.getWidth()

            a1 = radians(self.angle - (self.width / 2))
            a2 = radians(self.angle + (self.width / 2))

            Sx1, Sy1 = 150 + (cos(a1) * d), 150 - (sin(a1) * d)
            Sx2, Sy2 = 150 + (cos(a2) * d), 150 - (sin(a2) * d)
            
            self.roomCanv.create_line((Sx1, Sy1, 150, 150, Sx2, Sy2), fill = "red", width = 2,\
                                       tags = "shockZone")


        # minimal and maximal time
        self.maxTime = min([self.cm.data[-1][1], eval(self.timeFrame.timeVar.get()) * 60000])
        self.minTime = max([self.cm.data[0][1], eval(self.timeFrame.startTimeVar.get()) * 60000])

        # initial position
        for line in self.data:
            if line[1] < self.minTime:
                continue                       
            else:
                curLine = line
                break
        else:
            self.status.set("Invalid start time set.")
            self.bell()
            return

        
        if self.showTrackVar.get():
            # draws tracks        
            data = [line[2:4] + line[6:9] for count, line in enumerate(self.data) if
                    self.minTime <= line[1] <= self.maxTime]
            arena = []
            room = []
            prev = [-100, -100, 0, -100, -100]
            last = [0, 0]
            for count, line in enumerate(data):
                if abs(line[0] - prev[0]) + abs(line[1] - prev[1]) > 2 or count - last[0] == 15 or\
                   line[2] > 0:
                    room.append(line[0:2])
                    last[0] = count
                if abs(line[3] - prev[3]) + abs(line[4] - prev[4]) > 2 or count - last[1] == 15:
                    arena.append(line[3:5])
                    last[1] = count
                prev = line
                    
            self.arenaCanv.create_line(([item + 150 - d for line in arena for item in line]),
                                       fill = "black", width = 2)
            self.roomCanv.create_line(([item + 150 - d for line in room for item in line]),
                                      fill = "black", width = 2)
            # draws shocks
            if self.showShocksVar.get():
                shocks = [line[2:4] for count, line in enumerate(self.data) if
                          self.minTime <= line[1] <= self.maxTime and line[6] > 0 and
                          self.data[count - 1][6] <= 0]
                self.ld = 150 - d - 4
                self.ur = 150 - d + 4
                for shock in shocks:
                    self.roomCanv.create_oval(shock[0] + self.ld, shock[1] + self.ld,
                                              shock[0] + self.ur, shock[1] + self.ur,
                                              outline = "red", width = 3)
        else:
            # makes 'the rat' (i.e. two black points)
            self.ld = 150 - d - 4 # 4 is size of the rat dot
            self.ur = 150 - d + 4
            
            Rx, Ry = curLine[2:4]
            Ax, Ay = curLine[7:9]
            self.arenaCanv.create_oval(Ax + self.ld, Ay + self.ld, Ax + self.ur, Ay + self.ur,\
                                       fill = "black", tags = "ratA")
            self.roomCanv.create_oval(Rx + self.ld, Ry + self.ld, Rx + self.ur, Ry + self.ur,\
                                       fill = "black", tags = "ratR")
            
            # shock
            if curLine[6] > 0:
                self.roomCanv.itemconfigure("ratR", fill = "red", outline = "red")
                self.shock = True   
            else:
                self.shock = False


        # initializes distance and entrances displays
        self.totDistanceVar.set(round(self.cm.getDistance(time = self.maxTime / 60000,
                                                          startTime = self.minTime / 60000), 1))
        self.totEntrancesVar.set(self.cm.getEntrances(time = self.maxTime / 60000,
                                                      startTime = self.minTime / 60000))
        if timeReset:
            self.distanceVar.set("0.0")
            self.entrancesVar.set("0")


        # drawing of the graph
        self.graph.delete("all")
        if timeReset:
            self.graph.CM_loaded(self.cm, minTime = self.minTime, maxTime = self.maxTime)
        else:
            self.graph.CM_loaded(self.cm, minTime = self.minTime, maxTime = self.maxTime,
                                 initTime = (self.curTime.get() * (self.maxTime - self.minTime) /
                                             100 + self.minTime))

    
        # changing buttons' statuses
        if not self.showTrackVar.get():
            self.playBut.state(["!disabled"])
            self.pauseBut.state(["!disabled"])
            self.stopBut.state(["!disabled"])
            self.timeSc.state(["!disabled"])
        else:
            self.playBut.state(["disabled"])
            self.pauseBut.state(["disabled"])
            self.stopBut.state(["disabled"])
            self.timeSc.state(["disabled"])


        self.initialized = True


        if new and timeReset:
            self.curTime.set(0)
            self.timeVar.set(self._timeFormat(self.minTime))  


        
    def changedGraph(self):
        "called when the graph is changed"
        self.graph.delete("all")
        drawnParameter = self.graph.drawnParameter
        self.graph = eval(self.graphTypeVar.get())
        self.graph.drawnParameter = drawnParameter
        self.graph.grid(column = 0, row = 4, columnspan = 7, padx = 2, pady = 5, sticky = (E, W))
        self.graph.bind("<Button-1>", self.graphClick)
        self.graph.bind("<Button-3>", self.graphPopUp)
        if self.initialized:
            self.graph.CM_loaded(self.cm, minTime = self.minTime, maxTime = self.maxTime,
                                 initTime = ((self.curTime.get() * (self.maxTime - self.minTime) /
                                              100) + self.minTime))
            

    def graphClick(self, event):
        "changes time when the graph is clicked upon"
        if self.initialized and not self.showTrackVar.get():
            self.graph.coords("timeMeasure", (event.x, 0, event.x, self.graph.height))
            time = (event.x * 100) / self.graph.width
            if time > 100:
                time = 100           
            self.changedTime(time)


    def graphPopUp(self, event):
        "shows menu for selection of parameter to be shown in graph"
        if not self.initialized:
            return
        
        menu = Menu(self, tearoff = 0)
        menu.add_command(label = "Show periodicity",
                         command = lambda: self.graph.drawParameter(self.cm, "periodicity"))
        menu.add_command(label = "Show mobility",
                         command = lambda: self.graph.drawParameter(self.cm, "mobility"))
        menu.add_command(label = "Show immobility",
                         command = lambda: self.graph.drawParameter(self.cm, "immobility"))
        menu.add_command(label = "Show entrances",
                         command = lambda: self.graph.drawParameter(self.cm, "entrances"))
        menu.add_command(label = "Show shocks",
                         command = lambda: self.graph.drawParameter(self.cm, "shocks"))
        menu.add_command(label = "Show bad points",
                         command = lambda: self.graph.drawParameter(self.cm, "bad points"))
        menu.add_command(label = "Show thigmotaxis",
                         command = lambda: self.graph.drawParameter(self.cm, "thigmotaxis"))
        menu.add_command(label = "Don't show anything",
                         command = lambda: self.graph.drawParameter(self.cm, None))
        menu.post(event.x_root, event.y_root)        


    def unDraw(self):
        "clears canvases, graph etc."
        if self.initialized:
            self.arenaCanv.delete("all")
            self.roomCanv.delete("all")
            self.graph.delete("all")
            self.initialized = False
            self.playBut.state(["disabled"])
            self.pauseBut.state(["disabled"])
            self.stopBut.state(["disabled"])
            self.fileFrame.previousBut.state(["disabled"])
            self.fileFrame.nextBut.state(["disabled"])
            self.fileFrame.tagBut.state(["disabled"])
            self.saveBut.state(["disabled"])
            

    def checkProcessing(self):
        "called when content of fileStorage is changed"
        if self.fileStorage.arenafiles or self.fileStorage.wrongfiles:
            self.fileStorageFrame.removeFiles.state(["!disabled"])
        else:
            self.fileStorageFrame.removeFiles.state(["disabled"])
        self.fileStorageFrame.chosenVar.set(len(self.fileStorage.arenafiles))
        self.fileStorageFrame.nonMatchingVar.set(len(self.fileStorage.wrongfiles))

        self.fileFrame.files = [] + self.fileStorage.arenafiles
        
        if not self.fileFrame.files or not self.fileFrame.selected in self.fileFrame.files:
            self.unDraw()

        if self.fileFrame.files:
            self.fileFrame.previousBut.state(["!disabled"])
            self.fileFrame.nextBut.state(["!disabled"])
            self.fileFrame.tagBut.state(["!disabled"])
            self.saveBut.state(["!disabled"])
            if not self.fileFrame.selected in self.fileFrame.files:
                self.fileFrame.selected = None
        else:
            self.fileFrame.selected = None
            
        self.fileFrame.drawTree(self.fileFrame.selected)


    def initialize(self):
        """initializes the canvases etc. if files were added to fileStorage and file from
            fileStorage is not initialized"""
        if self.fileFrame.files:
            if not self.fileFrame.selected in self.fileFrame.files:
                self.initializeFile(self.fileFrame.files[0])
                self.fileFrame.selected = self.fileFrame.files[0]


    def _timeFormat(self, time):
        "formats time from miliseconds to minutes:seconds"
        minutes = time // 60000
        seconds = (time % 60000) // 1000
        return "{:d}:{:0>2d}".format(int(minutes), int(seconds))

         
    def changedSpeed(self, value):
        "rounds speed set by scale"
        if eval(value) <= 1.0:
            self.speed.set(round(self.speed.get(), 1))
        elif eval(value) < 2.0:
            self.speed.set(round(self.speed.get() * 5, 0) / 5)
        elif eval(value) < 5.0:
            self.speed.set(round(self.speed.get() * 2, 0) / 2)
        elif eval(value) < 10.0:
            self.speed.set(round(self.speed.get(), 0))
        else:
            self.speed.set(round(self.speed.get() * 5, -1) / 5)
        

                

class FileFrame(ttk.Frame):
    "displays files in ShowTracks class"
    def __init__(self, root):
        super().__init__(root)

        self.rowconfigure(0, weight = 1)

        self.root = root
        self.fileStorage = self.root.fileStorage
        self.index = 0 # which file is selected when the FileTree is initialized
        self.files = []
        self.selected = None


        # tree
        self.treeFrame = ttk.Frame(self)
        self.treeFrame.grid(column = 0, row = 0, columnspan = 3, sticky = (N, S, E, W))
        self.treeFrame.rowconfigure(0, weight = 1)
        self.treeFrame.columnconfigure(0, weight = 1)
        
        self.tree = ttk.Treeview(self.treeFrame, selectmode = "browse", height = 20)
        self.tree.grid(column = 0, row = 0, sticky = (N, S, E, W))
        
        columns = ("tag")
        self.tree["columns"] = columns

        self.tree.column("#0", width = 250, anchor = "w")        
        self.tree.heading("#0", text = "File", command = self.orderByNames)

        self.tree.column("tag", width = 40, anchor = "center")
        self.tree.heading("tag", text = "Tag", command = self.orderByTag)
            
        self.scrollbar = ttk.Scrollbar(self.treeFrame, orient = VERTICAL,
                                       command = self.tree.yview)
        self.scrollbar.grid(column = 1, row = 0, sticky = (N, S, E))
        self.tree.configure(yscrollcommand = self.scrollbar.set)

        self.tree.bind("<1>", lambda e: self.click(e))
        self.tree.bind("<3>", lambda e: self.popUp(e))


        # previous and next buttons
        self.fileLabFrame = ttk.Labelframe(self, text = "File")
        self.fileLabFrame.grid(column = 0, row = 1, columnspan = 3, sticky = (N, W, E), pady = 2)
        self.fileLabFrame.columnconfigure(2, weight = 1)
        
        self.previousBut = ttk.Button(self.fileLabFrame, text = "Previous",
                                      command = self.previousFun, state = "disabled")
        self.previousBut.grid(column = 0, row = 0, padx = 2)
        
        self.nextBut = ttk.Button(self.fileLabFrame, text = "Next", command = self.nextFun,
                                  state = "disabled")
        self.nextBut.grid(column = 1, row = 0, padx = 2)


        # tag buttons       
        self.tagBut = ttk.Button(self.fileLabFrame, text = "Tag file", command = self.tagFun,
                                 state = "disabled")
        self.tagBut.grid(column = 3, row = 0, padx = 2)
      

    def tagFun(self, index = "none"):
        "tags the selected file"
        selected = self.files[eval(self.tree.selection()[0])]
        if index != "none":
            self.index = index
        else:
            self.tagBut["text"] = "Remove tag"
            self.tagBut["command"] = self.untagFun
        self.fileStorage.tag(self.files[self.index])
        self.drawTree(selected = selected)

    def untagFun(self, index = "none"):
        "untags the selected file"
        selected = self.files[eval(self.tree.selection()[0])]
        if index != "none":
            self.index = index
        else:
            self.tagBut["text"] = "Tag file"
            self.tagBut["command"] = self.tagFun 
        self.fileStorage.tagged.remove(self.files[self.index])
        self.drawTree(selected = selected)              

    def checkTag(self):
        "checks the state of tag button"
        if self.files[self.index] in self.fileStorage.tagged:
            command = self.untagFun
            text = "Remove tag"
        else:
            command = self.tagFun
            text = "Tag file"            
        self.tagBut["text"] = text
        self.tagBut["command"] = command


    def click(self, event):
        "called when item in tree is clicked"
        item = self.tree.identify("item", event.x, event.y)
        if item:
            self.tree.selection_set(item)
            self.index = int(item)
            self.checkTag()
            self.selected = self.files[self.index]
            self.root.initializeFile(self.files[self.index])
            if not self.root.animate:
                self.root.stopFun()
                self.root.playFun()
            
        
    def previousFun(self):
        "shows previous file"
        if self.index != 0:
            self.prevIndex = self.index
            self.index -= 1
            self.tree.selection_set(str(self.index))
            self.tree.see(str(self.index))
            self.selected = self.files[self.index]
            self.checkTag()
            self.root.initializeFile(self.files[self.index])
            if not self.root.animate:
                self.root.stopFun()
                self.root.playFun()


    def nextFun(self):
        "shows next file"
        if self.index != len(self.files) - 1:
            self.prevIndex = self.index
            self.index += 1
            self.tree.selection_set(str(self.index))
            self.tree.see(str(self.index))
            self.selected = self.files[self.index]
            self.checkTag()
            self.root.initializeFile(self.files[self.index])
            if not self.root.animate:
                self.root.stopFun()
                self.root.playFun()           
            

    def orderByNames(self):
        "orders files by names"
        selected = self.files[eval(self.tree.selection()[0])]
        self.files.sort()
        self.drawTree(selected = selected)

    def orderByTag(self):
        "order files by tags"
        selected = self.files[eval(self.tree.selection()[0])]
        self.files.sort(key = lambda i: (i in self.fileStorage.tagged),
                        reverse = True)
        self.drawTree(selected = selected)


    def drawTree(self, selected = None):
        "initializes (or refreshes) tree"
        for child in self.tree.get_children():
            self.tree.delete(child)
            
        for count, file in enumerate(self.files):
            if file in self.fileStorage.tagged:
                tag = "x"
            else:
                tag = ""                
            values = (tag)   
            self.tree.insert("", "end", str(count), text = returnName(
                file, self.files), values = values)

        if selected:
            self.index = self.files.index(selected)
        elif self.files:
            self.index = 0            

        if self.files:
            self.tree.selection_set(str(self.index))            
            self.tree.see(str(self.index))
            

    def popUp(self, event):
        "called when tree item is clicked on"
        item = self.tree.identify("item", event.x, event.y)
        menu = Menu(self, tearoff = 0)
        if item:
            if self.files[int(item)] in self.fileStorage.tagged:
                menu.add_command(label = "Remove tag", command = lambda: self.untagFun(index =
                                                                                       int(item)))
            else:
                menu.add_command(label = "Add tag", command = lambda: self.tagFun(index =
                                                                                  int(item)))

            menu.post(event.x_root, event.y_root)



def main():
    testGUI = Tk()
    explorer = Explorer(testGUI)
    explorer.grid()
    explorer.selectFileFun()
    explorer.speed.set(30)
    explorer.graphTypeVar.set("DistanceFromCenterGraph(self)")
    explorer.changedGraph()
    explorer.playFun()
    testGUI.mainloop()
    

if __name__ == "__main__": main()
