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

from showtracks import ShowTracks
from commonframes  import TimeFrame, SaveToFrame, returnName
from filestorage import FileStorageFrame
from cm import CM
from optionget import optionGet
from processor import writeResults, ProgressWindow


class ControlSelection(ttk.Checkbutton):
    "class representing checkbutton for selection of methods in Controller"
    def __init__(self, root, text):
        self.onVar = BooleanVar()
        self.onVar.set(True)
        super().__init__(root, text = text, variable = self.onVar)


class Controls(list):
    "class containing list of controls, their methods and options"
    def __init__(self):
        self.controls = [["Reflections", "findReflections"],
                         ["Outside Points", "findJumpers"],
                         ["Bad Points", "countBadPoints"]
                         ]
        # pridavat vzdy do FileTree.popUp !
        

class ControlFrame(ttk.Labelframe):
    "class contatining checkbuttons for selection of methods in Controller"
    def __init__(self, root):
        super().__init__(root, text = "Controls")

        self.controls = Controls()
        for count, control in enumerate(self.controls.controls):
            exec("self.{} = ControlSelection(self, text = '{}')".\
                 format(control[0].replace(" ", "_"), control[0]))
            exec("self.{}.grid(column = 0, row = {}, padx = 2, pady = 2, sticky = W)"\
                 .format(control[0].replace(" ", "_"), count))

    def controlsGet(self):
        "returns selected methods in a list"
        selected = []
        for control in self.controls.controls:
            if eval("self.{}.onVar.get()".format(control[0].replace(" ", "_"))):
                selected.append((control[0], control[1]))
        return selected
            
                             

class ControlReport():
    "represents results of Controller processing"
    def __init__(self):
        self.controls = []
        self.results = {}
        self.key = {"Problem": 15, "Warning": 3, "Concern": 1, "OK": 0} # weights of results
        self.order = []
        self.files = []
        self.orderedBy = "importance"

    def addFile(self, fileResults):
        """takes 'fileResults' (results of one method for one file) and appends them to
            self.results; add filename to self.files (if it is not already contained there)
        """
        self.results[fileResults[0]].append(fileResults[1])
        if not fileResults[1][0] in self.files:
            self.files.append(fileResults[1][0])


    def _orderResults(self):
        "orders results for diplaying in the caller's tree"
        self.order = []
        for control in self.controls:
            controlResults = self.results[control]
            if self.orderedBy == "importance":
                controlResults.sort(key = lambda i: self.key[i[2]], reverse = True)
            elif self.orderedBy == "description":
                controlResults.sort(key = lambda i: i[3], reverse = True)
            elif self.orderedBy == "name":
                controlResults.sort(key = lambda i: i[0])
            self.results[control] = controlResults
            self.order.append((control, sum([self.key[result[2]] for result in controlResults])))
        self.order.sort(key = lambda i: i[1], reverse = True)

    def _giveFirst(self, controlName):
        "returns value of the description column for method items"
        problems = sum([1 for result in self.results[controlName] if result[2] == "Problem"])
        warnings = sum([1 for result in self.results[controlName] if result[2] == "Warning"])
        concerns = sum([1 for result in self.results[controlName] if result[2] == "Concern"])
        if problems or warnings or concerns:
            return "{} problems, {} warnings, {} concerns".format(problems, warnings, concerns)
        else:
            return "All files are OK"

    def _giveSecond(self, importanceValue):
        "returns value of the imoprtance column for method items"
        if importanceValue > 15:
            return "Problem"
        elif importanceValue > 6:
            return "Warning"
        elif importanceValue > 3:
            return "Concern"
        else:
            return "OK"       
                 
    def updateTree(self, caller, deleteExisting = False):
        """updates caller's tree when all files are processed
            calls orderResults, giveFirst and giveSecond in the process
        """
        self._orderResults()

        toOpen = 0
        toOpenOK = 0

        # method items
        for count, control in enumerate(self.order):
            caller.contentTree.insert("", count, control[0], text = control[0],
                                      values = (self._giveFirst(control[0]),
                                                self._giveSecond(control[1])))
            toOpen += 1

            # file items
            countOK = 0
            for result in self.results[control[0]]:
                if result[2] != "OK":
                    caller.contentTree.insert(control[0], "end", result[0] + str(count),
                                              text = returnName(filename = result[0],
                                                                allFiles = self.files),
                                              values = result[1:3],
                                              tag = "file")
                    toOpen += 1
                else:
                    countOK += 1
                    
            # OK items
            if countOK:
                caller.contentTree.insert(control[0], "end", "OkFiles" + str(count),
                                          text = "Rest of files",
                                          values = ("{} files".format(countOK), "OK"))
                if self._giveFirst(control[0]) == "All files are OK":
                    caller.contentTree.see("OkFiles" + str(count))
                toOpen += 1
                for result in self.results[control[0]]:
                    if result[2] == "OK":
                        caller.contentTree.insert("OkFiles" + str(count), "end",
                                                  result[0] + str(count),
                                                  text = returnName(filename = result[0],
                                                                    allFiles = self.files),
                                                  values = result[1:3], tag = "file")
                        toOpenOK += 1

        # opens items
        if toOpen + toOpenOK <= 28:
            for control in self.controls:
                for child in caller.contentTree.get_children(control):
                    caller.contentTree.see(child)
                    for posterity in caller.contentTree.get_children(child):
                        caller.contentTree.see(posterity)
        elif toOpen <= 28:
            for control in self.controls:
                caller.contentTree.item(control, open = True)                
                                              

    def addControls(self, controls): # upravit aby slo pridavat
        """adds control methods in ControlReport - needed for self.controls and self.results
            initialization
        """
        self.controls = [control[0] for control in controls]
        self.results = {control: [] for control in self.controls}


    def clear(self, caller):
        "clears content of the caller's tree and of ControlReport"
        for item in caller.contentTree.get_children():
            caller.contentTree.delete(item)
        self.controls = []
        self.results = {}
        self.order = []
        self.files = []

    
class Controller(ttk.Frame):
    "represents 'Control' page in the main window notebook"
    def __init__(self, root):
        super().__init__(root)

        self["padding"] = (7, 7, 9, 9)

        self.root = root
        self.fileStorage = self.root.fileStorage

        # file selection
        self.saveToVar = StringVar()
        self.saveToVar.set(True)
        self.fileStorageFrame = FileStorageFrame(self)
        self.fileStorageFrame.grid(column = 1, row = 0, columnspan = 2, sticky = (N, S, E, W),
                                   pady = 5, padx = 2)

        # statusbar
        self.status = StringVar()
        
        self.statusBar = ttk.Label(self, textvariable = self.status)
        self.statusBar.grid(column = 0, row = 4, columnspan = 2, sticky = (S, E, W))
        
        # control button
        self.process = ttk.Button(self, text = "Control", command = self.controlFun)
        self.process.grid(column = 2, row = 4, sticky = E)
        self.process.state(["disabled"])
        
        # report
        self.reportFrame = ttk.LabelFrame(self, text = "Report")
        self.reportFrame.grid(column = 0, row = 0, rowspan = 4, sticky = (N, S, E, W), padx = 5)
        self.reportFrame.columnconfigure(0, weight = 1)
        self.reportFrame.rowconfigure(0, weight = 1)

        self.upFrame = ttk.Frame(self.reportFrame)
        self.upFrame.grid(column = 0, row = 0, columnspan = 2, sticky = (N, S, E, W))
        self.upFrame.columnconfigure(0, weight = 1)
        self.upFrame.rowconfigure(0, weight = 1)
        
        self.contentTree = ttk.Treeview(self.upFrame, selectmode = "none")
        self.contentTree.grid(column = 0, row = 0, sticky = (N, S, E, W))
        self.contentTree["columns"] = ("description", "importance")
        self.contentTree.column("#0", width = 250, anchor = "w")
        self.contentTree.heading("#0", text = "Problem",
                                 command = self.orderReportByNames)
        self.contentTree.column("description", width = 200, anchor = "e")
        self.contentTree.heading("description", text = "Description",
                                 command = self.orderReportByResults)
        self.contentTree.column("importance", width = 60, anchor = "e")
        self.contentTree.heading("importance", text = "Importance",
                                 command = self.orderReportByImportance)      
        self.scrollbar = ttk.Scrollbar(self.upFrame, orient = VERTICAL,
                                       command = self.contentTree.yview)
        self.scrollbar.grid(column = 1, row = 0, sticky = (N, S, E))
        self.contentTree.configure(yscrollcommand = self.scrollbar.set)
        
        self.saveToFrame = SaveToFrame(self.reportFrame, label = False)
        self.saveToFrame.grid(column = 0, row = 1, sticky = (E, W))

        self.saveBut = ttk.Button(self.reportFrame, text = "Save", command = self.saveFun)
        self.saveBut.grid(column = 1, row = 1, sticky = E, padx = 2)
    
        self.controlReport = ControlReport() #!
                       
        self.contentTree.tag_bind("file", "<Double-1>", lambda e: self.treeDoubleClick(e))
        
        # method selection frame                
        self.controlFrame = ControlFrame(self)
        self.controlFrame.grid(column = 1, row = 1, columnspan = 2, sticky = (N, W), padx = 10,
                               pady = 55)


        # time frame
        self.timeFrame = TimeFrame(self)
        self.timeFrame.grid(column = 1, row = 2, columnspan = 2, sticky = (N, W), padx = 10)


        self.columnconfigure(0, weight = 1)
        self.rowconfigure(2, weight = 1)


    def orderReportByNames(self):
        opened = {}
        for child in self.contentTree.get_children():
            opened[child] = self.contentTree.item(child, "open")
            self.contentTree.delete(child)
        self.controlReport.orderedBy = "name"
        self.controlReport.updateTree(self, deleteExisting = True)
        for child in self.contentTree.get_children():
            if child in opened:
                self.contentTree.item(child, open=opened[child])

    def orderReportByResults(self):
        opened = {}
        for child in self.contentTree.get_children():
            opened[child] = self.contentTree.item(child, "open")
            self.contentTree.delete(child)
        self.controlReport.orderedBy = "description"
        self.controlReport.updateTree(self, deleteExisting = True)
        for child in self.contentTree.get_children():
            if child in opened:
                self.contentTree.item(child, open=opened[child])

    def orderReportByImportance(self):
        opened = {}
        for child in self.contentTree.get_children():
            opened[child] = self.contentTree.item(child, "open")
            self.contentTree.delete(child)
        self.controlReport.orderedBy = "importance"
        self.controlReport.updateTree(self, deleteExisting = True)        
        for child in self.contentTree.get_children():
            if child in opened:
                self.contentTree.item(child, open=opened[child])
                
        
    def treeDoubleClick(self, event):
        "shows tracks in a ShowTracks toplevel window"
        item = self.contentTree.identify("item", event.x, event.y)
        name = item.rstrip("0123456789")
        tracks = self.controlReport.files # <- zmenit aby zobrazovalo serazene
        if item:
            time = (self.timeFrame.startTimeVar.get(), self.timeFrame.timeVar.get())
            showTracks = ShowTracks(self, nameA = name, tracks = tracks, time = time,
                                    controlled = True)


    def controlFun(self):
        "processes selected files, clears report, shows results in a report"

        # progressbar
        if len(self.root.fileStorage.arenafiles) > 1:
            self.stoppedProcessing = False
            self.progressWindow = ProgressWindow(self, len(self.root.fileStorage.arenafiles),
                                                 text = "controlled")

        # initialization
        controls = self.controlFrame.controlsGet() # selected controls
        self.controlReport.clear(self)  # clears report
        self.controlReport.addControls(controls) # adds selected controls to ControlReport

        self.problemOccured = False
        # processing      
        for file in self.root.fileStorage.arenafiles:
            try:
                if file in self.root.fileStorage.pairedfiles:
                    cm = CM(file, nameR = self.root.fileStorage.pairedfiles[file])
                else:
                    cm = CM(file, nameR = "auto")
            except Exception:
                self.problemOccured = True
                for control in controls:
                    self.controlReport.addFile((control[0], (file, "Failed to load!", "Problem",
                                                             9999999)))
            else:
                for control in controls:
                    try:
                        assessment = self.assessImportance(cm = cm, control = control, file = file)
                    except Exception:
                        self.problemOccured = True
                        assessment = (control[0], (file, "Failed to compute!", "Problem",
                                                   9999998))
                    self.controlReport.addFile(assessment)
                     
            if len(self.root.fileStorage.arenafiles) > 1:
                if self.stoppedProcessing:
                    return
                else:
                    self.progressWindow.addOne()
                    
        self.controlReport.updateTree(self)

        # progressbar and status
        if len(self.root.fileStorage.arenafiles) > 1:
            self.progressWindow.destroy()
            if self.problemOccured:
                self.status.set("Files were not processed successfully!")
                self.bell()
            else:
                self.status.set("Files were processed successfully.")
        else:
            if self.problemOccured:
                self.status.set("File was not processed successfully!")
                self.bell()
            else:
                self.status.set("File was processed successfully.")          
        

    def assessImportance(self, cm, control, file):
        "method needed for evaluation of importance of results from CM class' control methods"
        method = control[0]
        results = eval("cm.{}()".format(control[1]))
        description = ""
        importance = ""
        value = 0
        
        if method == "Reflections":
            if results[1] * 3 + results[0] > 5:
                importance = "Problem"
            elif results[1] * 3 + results[0] > 2:
                importance = "Warning"
            elif results[0] > 0:
                importance = "Concern"
            else:
                importance = "OK"
            if results[1] != 1:
                description = "{} points problematic, {} of concern".format(results[1], results[0])
            else:
                description = "{} point problematic, {} of concern".format(results[1], results[0])
            value = results[1]

            self.root.fileStorage.saveReflections(file = file, points = results[2] + results[3])
            
        elif method == "Outside Points":
            if results > 250:
                importance = "Problem"
            elif results > 50:
                importance = "Warning"
            elif results > 5:
                importance = "Concern"
            else:
                importance = "OK"
            if results != 1:
                description = "{} points outside of arena".format(results)
            else:
                description = "1 point outside of arena"
            value = results

        elif method == "Bad Points":
            if results > 10:
                importance = "Problem"
            elif results > 5:
                importance = "Warning"
            elif results > 2:
                importance = "Concern"
            else:
                importance = "OK"
            description = "{0:.2f}% bad points".format(results)
            value = results            
                    
        return (method, (cm.nameA, description, importance, value))

            
    def saveFun(self):
        "writes results from controlReport to selected file"
        output = self.saveToFrame.saveToVar.get()
        if not self.controlReport.files:
            self.bell()
            self.status.set("No results prepared for saving.")
            return
        if not output:
            self.bell()
            self.status.set("You have to select a name of a file.")
            return
        
        separator = optionGet("ResultSeparator", ",", "str")
        results = separator.join(["File"] + self.controlReport.controls)
        for file in self.controlReport.files:
            filename = returnName(filename = file, allFiles = self.controlReport.files)
            result = [filename]
            for control in self.controlReport.controls:
                result += [i[3] for i in self.controlReport.results[control] if i[0] == file]
            results += "\n" + separator.join(map(str, result))
     
        writeResults(output, results)
        self.status.set("Results were saved.")
        

    def checkProcessing(self):
        "method updating page after change of notebook tab"        
        if self.root.fileStorage.arenafiles:
            self.process.state(["!disabled"])
        else:
            self.process.state(["disabled"])

        if self.root.fileStorage.arenafiles or self.root.fileStorage.wrongfiles:
            self.fileStorageFrame.removeFiles.state(["!disabled"])
        else:
            self.fileStorageFrame.removeFiles.state(["disabled"])

        self.fileStorageFrame.chosenVar.set(len(self.root.fileStorage.arenafiles))
        self.fileStorageFrame.nonMatchingVar.set(len(self.root.fileStorage.wrongfiles))



def main():
    "most probably does not work"
    from filestorage import FileStorage
    import os.path
    import os
    testGUI = Tk()
    testGUI.fileStorage = FileStorage()
    testingDir = os.path.join(os.getcwd(), "TestingFiles")
    from filestorage import recognizeFiles
    testGUI.fileStorage.addFiles(recognizeFiles([os.path.join(testingDir, file) for file in
                                                 os.listdir(testingDir)]))
    controller = Controller(testGUI)
    controller.grid()
    controller.controlFun()
    controller.saveToFrame.saveToVar.set(os.path.join(os.getcwd(), "Results.txt"))
    controller.saveFun()
    testGUI.mainloop()


if __name__ == "__main__": main()
