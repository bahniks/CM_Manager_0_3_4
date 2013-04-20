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

from tkinter.filedialog import askopenfilenames, askdirectory, askopenfilename
from tkinter import *
from os.path import basename
from tkinter import ttk
import os.path
import os


from showtracks import ShowTracks
from optionget import optionGet
from window import placeWindow
from cm import CM


class FileStorage():
    "class for storing files for processing"  
    def __init__(self):
        self.arenafiles = []
        self.wrongfiles = []
        self.reflections = {}
        self.tagged = []
        self.pairedfiles = {}
        self.addedReflections = {}


    def addFiles(self, addedFiles):
        "adds new files into filestorage - sorted into wrong and valid files"
        newWrong, newFiles = addedFiles[0], addedFiles[1]

        # removes wrongfiles that are already added
        if self.wrongfiles:
            for fileOld in self.wrongfiles:
                for fileNew in newWrong:
                    if os.path.samefile(fileNew, fileOld):
                        newWrong.remove(fileNew)                    
        self.wrongfiles = self.wrongfiles + newWrong
        
        # removes arenafiles that are already added            
        if self.arenafiles:
            for fileOld in self.arenafiles:
                for fileNew in newFiles:
                    if os.path.samefile(fileNew, fileOld):
                        newFiles.remove(fileNew)                                      
        self.arenafiles = self.arenafiles + newFiles


    def saveReflections(self, file, points):
        """saves reflection points for a file in the argument
            self.reflections is None if the file was not controlled, empty set if it was controlled
            and no reflection was found, and set with reflection points otherwise
        """
        if not file in self.reflections:
            self.reflections[file] = set(points)


    def addReflections(self, file, points):
        "add reflection points from a set in the 'points' argument for a file in the argument"
        if file in self.addedReflections:
            self.addedReflections[file].update(points)
        else:
            self.addedReflections[file] = points

        if file in self.reflections:
            self.reflections[file].update(points)
        else:
            if file in self.pairedfiles:
                cm = CM(file, nameR = self.pairedfiles[file])
            else:
                cm = CM(file, nameR = "auto")
            reflections = cm.findReflections(results = "indices")
            self.reflections[file] = set(reflections[0]) | set(reflections[1]) | points


    def removeReflections(self, file, pointsSet):
        "removes previously added reflections"
        if file in self.addedReflections:
            self.addedReflections[file] -= pointsSet
            self.reflections[file] -= pointsSet


    def tag(self, file):
        "tags the file in argument"
        if file not in self.tagged:
            self.tagged.append(file)
        else:
            pass


    def pairFiles(self, files):
        "checks pairing of files and puts pairs in arenafiles and pairedfiles"
        if ("arena" in files[0] or "Arena" in files[0]) and\
           ("room" in files[1] or "Room" in files[1]):
            self.pairedfiles[files[0]] = files[1]
            self.wrongfiles.remove(files[0])
            self.wrongfiles.remove(files[1])
            self.arenafiles.append(files[0])
        elif ("arena" in files[1] or "Arena" in files[1]) and\
             ("room" in files[0] or "Room" in files[0]):
            self.pairedfiles[files[1]] = files[0]            
            self.wrongfiles.remove(files[0])
            self.wrongfiles.remove(files[1])
            self.arenafiles.append(files[1])
            
            
    def findPairs(self, files):
        "finds pairs of files based on date and time of creation and their length"
        fileStamp = {}
        pairs = []

        for file in files:
            infile = open(file)
            
            for line in infile:
                if "%Date.0" in line:
                    date = line.split()[2]
                elif "%Time.0" in line:
                    time = line.split()[2]
                elif "%ElapsedTime_ms.0" in line:
                    elapsed = line.split()[2]
                elif "%%END_HEADER" in line:
                    break
                
            stamp = (date, time, elapsed)
            if stamp in fileStamp:
                filepair = (fileStamp.pop(stamp), file)
                pairs.append(filepair)
            else:
                fileStamp[stamp] = file

        for pair in pairs:
            self.pairFiles(pair)


class ShowFiles(Toplevel):
    "window that shows files in fileStorage"
    def __init__(self, root, files):
        super().__init__(root)

        self.root = root
        self.fileStorage = self.root.root.root.fileStorage
        
        self["padx"] = 4
        self["pady"] = 4
        self.grab_set()
        self.focus_set()
        placeWindow(self, 758, 760)
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)

               
        if files == "arenafiles":
            self.title("Matched files")
            self.initfiles = self.fileStorage.arenafiles
        elif files == "wrongfiles":
            self.title("Non-matched files")
            self.initfiles = self.fileStorage.wrongfiles

        self.shownFiles = files

        # frame with files
        self.filesFrame = ttk.Frame(self)
        self.filesFrame.grid(column = 0, row = 0, sticky = (N, S, E, W))
        self.filesFrame.columnconfigure(1, weight = 1)
        self.filesFrame.rowconfigure(0, weight = 1)
        
        self.filesTree = ttk.Treeview(self.filesFrame, height = 35)
        self.filesTree.grid(column = 1, row = 0, sticky = (N, S, E, W))
        if files == "wrongfiles":
            self.filesTree["columns"] = ("directory")
            directoryWidth = 480
        else:
            self.filesTree["columns"] = ("directory", "tag")            
            self.filesTree.column("tag", width = 30, anchor = "center")
            self.filesTree.heading("tag", text = "Tag", command = self.orderByTag)            
            directoryWidth = 450
        self.filesTree.column("#0", width = 250, anchor = "w")
        self.filesTree.heading("#0", text = "Filename", command = self.orderByFilename)
        self.filesTree.column("directory", width = directoryWidth, anchor = "w")
        self.filesTree.heading("directory", text = "Directory", command = self.orderByDirectory)
          
        self.scrollbar = ttk.Scrollbar(self.filesFrame, orient = VERTICAL,
                                       command = self.filesTree.yview)
        self.scrollbar.grid(column = 2, row = 0, sticky = (N, S, E))
        self.filesTree.configure(yscrollcommand = self.scrollbar.set)

        # button frame
        self.buttonFrame = ttk.Frame(self)
        self.buttonFrame.grid(column = 0, row = 1, sticky = (E, W))
        self.buttonFrame.columnconfigure(3, weight = 1)
        self.buttonFrame.columnconfigure(6, weight = 1)

        self.removeBut = ttk.Button(self.buttonFrame, text = "Remove Files",
                                    command = self.removeFun)
        self.removeBut.grid(column = 0, row = 0)

        self.cropBut = ttk.Button(self.buttonFrame, text = "Crop Files", command = self.cropFun)
        self.cropBut.grid(column = 1, row = 0)

        self.selectAllBut = ttk.Button(self.buttonFrame, text = "Select All",
                                       command = self.selectAllFun)
        self.selectAllBut.grid(column = 2, row = 0)

        self.closeBut = ttk.Button(self.buttonFrame, text = "Close", command = self.closeFun)
        self.closeBut.grid(column = 8, row = 0)

        if files == "wrongfiles":
            self.pairSelectedBut = ttk.Button(self.buttonFrame, text = "Pair Selected",
                                              command = self.pairSelectedFun)
            self.pairSelectedBut.grid(column = 4, row = 0)

            self.findPairsBut = ttk.Button(self.buttonFrame, text = "Find Pairs",
                                           command = self.findPairsFun)
            self.findPairsBut.grid(column = 5, row = 0)
            
            self.showArenafilesBut = ttk.Button(self.buttonFrame, text = "Show Matched Files",
                                                command = self.showArenafilesFun)
            self.showArenafilesBut.grid(column = 7, row = 0)
        else:
            self.tagFilesBut = ttk.Button(self.buttonFrame, text = "Tag Files",
                                          command = self.tagFilesFun)
            self.tagFilesBut.grid(column = 4, row = 0)
            self.untagFilesBut = ttk.Button(self.buttonFrame, text = "Untag Files",
                                            command = self.untagFilesFun)
            self.untagFilesBut.grid(column = 5, row = 0)
            self.showWrongfilesBut = ttk.Button(self.buttonFrame, text = "Show Non-matched Files",
                                                command = self.showWrongfilesFun)
            self.showWrongfilesBut.grid(column = 7, row = 0)


        self.filesTree.bind("<3>", lambda e: self.popUp(e))
        self.filesTree.bind("<Double-1>", lambda e: self.doubleClick(e))

        self.protocol("WM_DELETE_WINDOW", lambda: self.closeFun())

        self.initialize()



    def initialize(self):
        "initializes the treeview containing files"
        for file in self.initfiles:
            splitfile = os.path.split(file)
            if self.shownFiles == "arenafiles":
                if file in self.fileStorage.tagged:
                    tag = "X"
                else:
                    tag = ""
                values = (splitfile[0].replace(" ", "_").replace("\\", "/"), tag)
            else:
                values = splitfile[0].replace(" ", "_").replace("\\", "/")
            self.filesTree.insert("", "end", file, text = splitfile[1], values = values)


    def removeFun(self):
        "removes selected files"
        for file in self.filesTree.selection():
            if self.shownFiles == "arenafiles":
                self.fileStorage.arenafiles.remove(file)
            elif self.shownFiles == "wrongfiles":
                self.fileStorage.wrongfiles.remove(file)
            self.filesTree.delete(file)
        self.root.root.fileStorageFrame.update()
            

    def cropFun(self):
        "removes all unselected files"
        self.filesTree.selection_toggle(self.filesTree.get_children(""))
        self.removeFun()
        self.filesTree.selection_toggle(self.filesTree.get_children(""))        
        
            
    def selectAllFun(self):
        "selects all files"
        self.filesTree.selection_set(self.filesTree.get_children("")) 


    def closeFun(self):
        "closes the window"
        self.root.root.checkProcessing()
        self.destroy()


    def pairSelectedFun(self):
        "finds pairs in selected files"
        selected = self.filesTree.selection()
        if len(selected) < 2:
            self.bell()             
        else:
            self.fileStorage.findPairs(selected)
            self.refresh()


    def findPairsFun(self):
        "calls method of FileStorage finding pairs of data files"
        self.config(cursor = "wait")
        self.update()
        self.fileStorage.findPairs(self.fileStorage.wrongfiles)
        self.refresh()
        self.config(cursor = "")


    def forcePair(self):
        "pairs the two selected files"
        self.fileStorage.pairFiles(self.filesTree.selection())
        self.refresh()
        

    def refresh(self):
        "refreshes the window - i.e. redraws the tree"
        for item in self.filesTree.get_children(""):
            self.filesTree.delete(item)
        if self.shownFiles == "arenafiles":
            self.initfiles = self.fileStorage.arenafiles
        else:
            self.initfiles = self.fileStorage.wrongfiles            
        self.initialize()           
        self.root.root.fileStorageFrame.update()
        

    def showWrongfilesFun(self):
        "shows matched files"
        ShowFiles(root = self.root, files = "wrongfiles")
        self.destroy()


    def showArenafilesFun(self):
        "shows non-matched files"
        ShowFiles(root = self.root, files = "arenafiles")
        self.destroy()


    def popUp(self, event):
        "called when tree item is right-clicked on"
        item = self.filesTree.identify("item", event.x, event.y)
        menu = Menu(self, tearoff = 0)
        if item and self.shownFiles == "arenafiles":
            if item in self.fileStorage.tagged:
                menu.add_command(label = "Remove tag", command = lambda: self.untagFun(item))
            else:
                menu.add_command(label = "Add tag", command = lambda: self.tagFun(item))
            if self.filesTree.identify("column", event.x, event.y) == "#0":
                menu.add_command(label = "Open room file",
                                 command = lambda: self.openRoomFile(item))
            menu.add_command(label = "Show track", command = lambda: self.showTracks(item))
        if item and self.shownFiles == "wrongfiles" and len(self.filesTree.selection()) == 2:
            menu.add_command(label = "Pair selected", command = lambda: self.forcePair())
        menu.post(event.x_root, event.y_root)        


    def showTracks(self, item):
        "opens ShowTracks widget"
        showTracks = ShowTracks(self, self.fileStorage.arenafiles, item)
        self.focus_set()
        self.grab_set()


    def untagFun(self, file):
        "untags the file in the argument"
        self.fileStorage.tagged.remove(file)
        self.filesTree.set(file, "tag", "")


    def tagFun(self, file):
        "tags the file in the argument"
        self.fileStorage.tag(file)
        self.filesTree.set(file, "tag", "X")


    def untagFilesFun(self):
        "untags selected files"
        for file in self.filesTree.selection():
            if file in self.fileStorage.tagged:
                self.untagFun(file)


    def tagFilesFun(self):
        "tags selected files"
        for file in self.filesTree.selection():
            if file not in self.fileStorage.tagged:
                self.tagFun(file)
                

    def openRoomFile(self, arenafile):
        "opens room file corresponding to the arenafile"
        if arenafile in self.fileStorage.pairedfiles:
            roomfile = self.fileStorage.pairedfiles[arenafile]
        else:
            if "Arena" in basename(arenafile):
                splitName = os.path.split(arenafile)
                roomfile = os.path.join(splitName[0], splitName[1].replace("Arena", "Room"))                    
            elif "arena" in basename(arenafile):
                splitName = os.path.split(arenafile)
                roomfile = os.path.join(splitName[0], splitName[1].replace("arena", "room"))
        if roomfile:
            os.startfile(roomfile)
        else:
            self.bell()
                

    def doubleClick(self, event):
        """opens either the file or the directory containing the file based on the
            column double-clicked"""
        item = self.filesTree.identify("item", event.x, event.y)
        if item:
            column = self.filesTree.identify("column", event.x, event.y)
            if column == "#0":
                os.startfile(item)
            elif column == "#1":
                os.startfile(os.path.split(item)[0])


    def orderByTag(self):
        "orders files by presence of tag"
        self.fileStorage.arenafiles.sort(key = lambda i: (i in self.fileStorage.tagged),
                                         reverse = True)
        self.refresh()
            

    def orderByFilename(self):
        "orders files by filename"
        if self.shownFiles == "arenafiles":
            self.fileStorage.arenafiles.sort(key = lambda i: basename(i))
        else:
            self.fileStorage.wrongfiles.sort(key = lambda i: basename(i))
        self.refresh()


    def orderByDirectory(self):
        "orders files by name of the parent directory"
        if self.shownFiles == "arenafiles":
            self.fileStorage.arenafiles.sort(key = lambda i: os.path.split(i)[0])
        else:
            self.fileStorage.wrongfiles.sort(key = lambda i: os.path.split(i)[0])
        self.refresh()            
            
        
    
            

class FileStorageFrame(ttk.Frame):
    "frame containing buttons for adding and removing files from FileStorage class"
    def __init__(self, root, parent = ""):
        super().__init__(root)

        self.root = root
        self.parent = parent
        self.fileStorage = self.root.root.fileStorage

        # variables        
        self.chosenVar = IntVar()
        self.nonMatchingVar = IntVar()

        self.chosenVar.set(len(self.fileStorage.arenafiles))
        self.nonMatchingVar.set(len(self.fileStorage.wrongfiles))

        # buttons
        self.addFilesBut = ttk.Button(self, text = "Add Files", command = self.addFilesFun)
        self.addDirectoryBut = ttk.Button(self, text = "Add Directory",
                                          command = self.addDirectoryFun)
        self.removeFiles = ttk.Button(self, text = "Remove All Files",
                                      command = self.removeFilesFun)
        self.loadFromLogBut = ttk.Button(self, text = "Load from Log",
                                         command = self.loadFromLogFun)

        # labels
        self.filesChosen = ttk.Label(self, text = "Number of selected files: ")
        self.nonMatching = ttk.Label(self, text = "Number of non-matching files: ")
        self.nonMatchingNum = ttk.Label(self, textvariable = self.nonMatchingVar, width = 4)
        self.filesChosenNum = ttk.Label(self, textvariable = self.chosenVar, width = 4)

        self.removeFiles.state(["disabled"])
               
        # adding to grid
        self.addFilesBut.grid(column = 6, row = 0, sticky = (N, S, E, W), padx = 4, pady = 2)
        self.addDirectoryBut.grid(column = 6, row = 1, sticky = (N, S, E, W), padx = 4, pady = 2)
        self.removeFiles.grid(column = 6, row = 3, sticky = (N, S, E, W), padx = 4)
        self.loadFromLogBut.grid(column = 6, row = 2, sticky = (N, S, E, W), padx = 4, pady = 2)

        self.filesChosen.grid(column = 4, row = 0, sticky = (N, E, S))
        self.nonMatching.grid(column = 4, row = 1, sticky = (N, E, S))
        self.filesChosenNum.grid(column = 5, row = 0, sticky = (N, W, S), padx = 4)
        self.nonMatchingNum.grid(column = 5, row = 1, sticky = (N, W, S), padx = 4)

        # event binding
        self.filesChosen.bind("<Double-1>", lambda e: self.showArenafiles(e))
        self.nonMatching.bind("<Double-1>", lambda e: self.showWrongfiles(e))
        self.filesChosenNum.bind("<Double-1>", lambda e: self.showArenafiles(e))
        self.nonMatchingNum.bind("<Double-1>", lambda e: self.showWrongfiles(e))
        self.filesChosen.bind("<3>", lambda e: self.popUp(e))
        self.filesChosenNum.bind("<3>", lambda e: self.popUp(e))

        
    def showArenafiles(self, event):
        "opens ShowFiles window"
        ShowFiles(self, files = "arenafiles")

    def showWrongfiles(self, event):
        "opens ShowFiles window"
        ShowFiles(self, files = "wrongfiles")
        

    def addFiles(self, addedFiles):
        """adds new files (tuple of non-matching files and arenafiles) to two corresponding
        lists"""
        self.fileStorage.addFiles(addedFiles)        
        self.root.checkProcessing()
        if self.parent == "explorer":
            self.root.initialize()
        

    def update(self):
        "updates fileStorageFrame when fileStroage content is changed"
        self.root.checkProcessing()
        if self.parent == "explorer":
            self.root.initialize()

    
    def addFilesFun(self):
        "asks uset to select files and adds them to filestorage (via addFiles)"
        self.root.root.config(cursor = "wait")
        self.root.root.update()
        self.addFiles(getFiles())
        self.root.root.config(cursor = "")
        

    def addDirectoryFun(self):
        """asks user to select directory and adds files from the directory to the list of files
        for processing"""
        self.root.root.config(cursor = "wait")
        self.root.root.update()
        self.addFiles(getDirectory())
        self.root.root.config(cursor = "")


    def loadFromLogFun(self):
        """asks user to select file with a log, loads files from the log and adds them to
        fileStorage"""
        self.root.root.config(cursor = "wait")
        self.root.root.update()
        
        filename = str(askopenfilename(initialdir = optionGet("LogDirectory",
                                                              os.path.join(os.getcwd(), "Stuff",
                                                                           "Logs"), "str"),
                                       filetypes = [("Text files", "*.txt")]))
        if not filename:
            self.root.root.config(cursor = "")
            return
        
        # processing file
        infile = open(filename)
        files = {}
        toTag = []
        for line in infile:
            if "Files processed" in line:
                for line in infile:
                    if "Paired with:" in line:
                        files[arenafile] = line.split("Paired with:")[1].strip()
                    else:
                        words = line.strip().split("\t")
                        arenafile = words[0]
                        files[arenafile] = ""
                        if len(words) >= 2 and words[1] == "Tagged":
                            toTag.append(arenafile)
            else:
                continue

        infile.close()

        arenafiles = []
        wrongfiles = []
        for file in files:
            # finding room- and arena- files' names
            if files[file]:
                arenafile = file
                roomfile = files[file]
            else:
                arenafile = file
                if "Arena" in basename(arenafile):
                    splitName = os.path.split(arenafile)
                    roomfile = os.path.join(splitName[0], splitName[1].replace("Arena", "Room"))                    
                elif "arena" in basename(arenafile):
                    splitName = os.path.split(arenafile)
                    roomfile = os.path.join(splitName[0], splitName[1].replace("arena", "room"))  
            # sorting existing and non-existing files
            if os.path.isfile(arenafile):
                if os.path.isfile(roomfile):
                    arenafiles.append(arenafile)
                    if arenafile in toTag:
                        self.fileStorage.tag(arenafile)
                    if files[file]:
                        self.fileStorage.pairedfiles[arenafile] = roomfile
                else:
                    wrongfiles.append(arenafile)
            else:
                if os.path.isfile(roomfile):
                    wrongfiles.append(roomfile)

        if not (wrongfiles or arenafiles):
            self.bell()
            self.root.status.set("No existing file found in the log.")
                                 
        self.addFiles([wrongfiles, arenafiles])
        
        self.root.root.config(cursor = "")
             

    def removeFilesFun(self):
        "removes files from file containers (two lists)"
        self.fileStorage.arenafiles = []
        self.fileStorage.wrongfiles = []
        self.root.checkProcessing()
        self.chosenVar.set(len(self.fileStorage.arenafiles))
        self.nonMatchingVar.set(len(self.fileStorage.wrongfiles))
        self.removeFiles.state(["disabled"])


    def checkProcessing(self):
        "called from ShowTracks if entered via ShowFiles"
        self.root.checkProcessing()


    def popUp(self, event):
        "called when matched files are right-clicked on"
        menu = Menu(self, tearoff = 0)
        if self.fileStorage.arenafiles:
            menu.add_command(label = "Show tracks", command = lambda: self.showTracks())
        menu.post(event.x_root, event.y_root)

    def showTracks(self):
        "opens ShowTracks widget"
        showTracks = ShowTracks(self, self.fileStorage.arenafiles, self.fileStorage.arenafiles[0])




def recognizeFiles(filenames):
    """from list of filenames provided by parameter recognizes matching files and returns two lists
    - first containing names of non-matching files and second containing list of arenafiles with
    matching room files counterparts
    matching files are those for which other file with the same name except from 'room' 'Arena'
    etc. exists in the same directory"""
    filenames.sort()
    filenames = [os.path.join(tupl[0], tupl[1]) for tupl in
                 [os.path.split(file) for file in filenames]]
    arenaFiles = []
    nonmatchingFiles = []
    while filenames:
        if "Arena" in basename(filenames[0]):
            splitName = os.path.split(filenames[0])
            roomName = os.path.join(splitName[0], splitName[1].replace("Arena", "Room"))
            if roomName in filenames:
                arenaFiles.append(filenames[0])
                filenames = filenames[1:]
                filenames.remove(roomName)
                continue
            elif os.path.exists(roomName):
                arenaFiles.append(filenames[0])
                filenames = filenames[1:]
                continue
            else:
                nonmatchingFiles.append(filenames[0])
                filenames = filenames[1:]
                continue
        elif "arena" in basename(filenames[0]):
            splitName = os.path.split(filenames[0])
            roomName = os.path.join(splitName[0], splitName[1].replace("arena", "room"))
            if roomName in filenames:
                arenaFiles.append(filenames[0])
                filenames = filenames[1:]
                filenames.remove(roomName)
                continue
            elif os.path.exists(roomName):
                arenaFiles.append(filenames[0])
                filenames = filenames[1:]
                continue
            else:
                nonmatchingFiles.append(filenames[0])
                filenames = filenames[1:]
                continue
        elif "Room" in basename(filenames[0]):
            splitName = os.path.split(filenames[0])
            arenaName = os.path.join(splitName[0], splitName[1].replace("Room", "Arena"))
            if arenaName in filenames:
                arenaFiles.append(arenaName)
                filenames = filenames[1:]
                filenames.remove(arenaName)
                continue
            elif os.path.exists(arenaName):
                arenaFiles.append(arenaName)
                filenames = filenames[1:]
                continue
            else:
                nonmatchingFiles.append(filenames[0])
                filenames = filenames[1:]
                continue                
        elif "room" in basename(filenames[0]):
            splitName = os.path.split(filenames[0])
            arenaName = os.path.join(splitName[0], splitName[1].replace("room", "arena"))
            if arenaName in filenames:
                arenaFiles.append(arenaName)
                filenames = filenames[1:]
                filenames.remove(arenaName)
                continue
            elif os.path.exists(arenaName):
                arenaFiles.append(arenaName)
                filenames = filenames[1:]
                continue
            else:
                nonmatchingFiles.append(filenames[0])
                filenames = filenames[1:]
                continue
        else:
            nonmatchingFiles.append(filenames[0])
            filenames = filenames[1:]
    return nonmatchingFiles, arenaFiles 


def getFiles():
    """asks to select files and returns list of files that doesn't contain 'arena' or 'room'
    in their names and another list of files containing 'arena' in their name"""
    filenames = str(askopenfilenames(initialdir = optionGet("FileDirectory", os.getcwd(), "str"),
                                     filetypes = [("Data files", "*.dat")]))
    if filenames == "":
        return [], []
    if "}" in filenames and "{" in filenames:
        filenames = filenames[1:-1].split("} {")
    else:
        filenames = [x + ".dat" for x in filenames.split(".dat ")]
        if filenames[-1].endswith(".dat.dat"):
            filenames[-1] = filenames[-1][:-4]
    return recognizeFiles(filenames)


def getDirectory():
    "recognizes all .dat files in a directory and calls recognizeFiles function"
    cmfiles = []
    for directory in os.walk(askdirectory(initialdir = optionGet("FileDirectory", os.getcwd(),
                                                                 "str"))):
        for file in directory[2]:
            if os.path.splitext(file)[1] == ".dat":
                cmfiles.append(os.path.join(directory[0], file))
    return recognizeFiles(cmfiles)



def main():
    class Root():
        def __init__(self, root):
            if root:
                self.root = root
            else:
                self.fileStorage = FileStorage()
    testGUI = Tk()
    testGUI.root = Root(Root(False))
    testingDir = os.path.join(os.getcwd(), "TestingFiles")
    files = recognizeFiles([os.path.join(testingDir, file) for file in os.listdir(testingDir)])
    testGUI.root.root.fileStorage.addFiles(files)
    testGUI.root.root.fileStorage.tag(files[1][1])
    testGUI.showfiles = ShowFiles(testGUI, "wrongfiles")
    testGUI.showfiles.grid()
    testGUI.wm_withdraw()
    testGUI.mainloop()





if __name__ == "__main__": main()

