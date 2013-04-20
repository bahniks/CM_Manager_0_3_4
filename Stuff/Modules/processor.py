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
from time import time, localtime, strftime
import os.path
import os
import csv

from commonframes  import TimeFrame, SaveToFrame, returnName
from filestorage import FileStorageFrame
from cm import CM, Parameters
from optionget import optionGet
from version import version
from window import placeWindow


class Processor(ttk.Frame):
    "represents 'Process' page in the main window notebook"
    def __init__(self, root):
        super().__init__(root)

        self["padding"] = (10, 10, 12, 12)
        self.root = root # potreba pouze pro progressbar


        # variables    
        self.status = StringVar()
              
        # frames
        self.parametersF = ParameterFrame(self)
        self.fileStorageFrame= FileStorageFrame(self)
        self.saveToFrame = SaveToFrame(self, parent = "processor")
        self.timeFrame = TimeFrame(self)
        self.optionFrame = OptionFrame(self, text = "Options")
        
        # buttons
        self.process = ttk.Button(self, text = "Process Files", command = self.processFun,
                                  state = "disabled")

        # labels
        self.statusBar = ttk.Label(self, textvariable = self.status)

        
        # adding to grid
        self.parametersF.grid(column = 0, row = 3, columnspan = 4, sticky = (N, W), padx = 4)
        self.fileStorageFrame.grid(column = 3, row = 0, pady = 5, padx = 4)
        self.timeFrame.grid(column = 1, row = 5, padx = 30, pady = 15, sticky = (N, W))
        
        self.process.grid(column = 3, row = 7, sticky = (S, E), padx = 4, pady = 3)

        self.statusBar.grid(column = 0, row = 7, columnspan = 3, sticky = (N, S, E, W), padx = 6,
                            pady = 3)
       
        self.saveToFrame.grid(column = 1, row = 1, columnspan = 3, sticky = (N, S, E, W),
                              padx = 6, pady = 2)

        self.optionFrame.grid(column = 0, row = 5, sticky = (N, E), padx = 6)
  

        # what should be enlarged
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(2, weight = 3)
        self.rowconfigure(4, weight = 2)
        self.rowconfigure(6, weight = 2)


    def processCheck(self):
        "checks whether all inputs are valid - helper function for processFun"

        if self.saveToFrame.saveToVar.get() == "":
            raise Exception("You have to choose an output file!")
        
        if len(self.root.fileStorage.arenafiles) == 0:
            raise Exception("You haven't chosen any file!")

        try:
            startTime = float(self.timeFrame.startTimeVar.get())
        except Exception:
            raise Exception("Start time has to be a number!")
        try:
            time = float(self.timeFrame.timeVar.get())
        except Exception:
            raise Exception("Stop time has to be a number!")
        
        if startTime >= time:
            raise Exception("Start time must be smaller than stop time!")

        if time < 0 or startTime < 0:
            raise Exception("Time has to be set to a positive value")

        if not os.path.exists(os.path.split(self.saveToFrame.saveToVar.get())[0]):
            if os.path.split(self.saveToFrame.saveToVar.get())[0]:
                raise Exception("Pathname of the output file doesn't exist!")
      
        
    def processFun(self):
        "processes chosen files and saves the results in the save-to file"
        # checking for mistakes
        try:
            self.processCheck()
        except Exception as e:
            self.bell()
            self.status.set(e)
            return                   

        # files to be processed
        self.filesToProcess = [file for file in self.root.fileStorage.arenafiles if \
                               self.optionFrame.processFile(file)]

        # progressWindow and check for number of files for processing
        if len(self.filesToProcess) > 1:
            self.stoppedProcessing = False
            self.progressWindow = ProgressWindow(self, len(self.filesToProcess))
        elif len(self.filesToProcess) == 0:
            self.bell()
            self.status.set("There is no file selected for processing!")
            return

        # selected methods          
        methods = []
        for method in Parameters().parameters:
            if eval("self.parametersF.%sVar.get()" % (method[0].replace(" ", ""))):
                methods.append(method[0])
           
        output = self.saveToFrame.saveToVar.get()
        startTime = float(self.timeFrame.startTimeVar.get())
        time = float(self.timeFrame.timeVar.get())
        separator = optionGet("ResultSeparator", ",", "str")
        
        results = separator.join(["File"] + methods)
        
        if self.optionFrame.saveTags.get():
            results += separator + "Tags"

        self.log = Log(methods, startTime, time, self.filesToProcess, self.root.fileStorage,
                       self.optionFrame.removeReflectionsWhere.get(), output)
        self.someProblem = False

        developer = optionGet("Developer", False, 'bool')
        
        for file in self.filesToProcess:
            # loading of cm object
            if methods:
                try:
                    if file in self.root.fileStorage.pairedfiles:
                        cm = CM(file, nameR = self.root.fileStorage.pairedfiles[file])
                    else:
                        cm = CM(file, nameR = "auto")

                    if self.optionFrame.removeReflections(file):
                        cm.removeReflections(points = self.root.fileStorage.reflections.get(file,
                                                                                            None))
                except Exception as e:
                    if developer:
                        print(e)   
                    filename = returnName(filename = file, allFiles =
                                          self.root.fileStorage.arenafiles) 
                    results += "\n" + filename + "{}NA".format(separator) * len(methods)
                    self.log.failedToLoad.append(file)
                    self.someProblem = True
                    continue
                    
            
            result = []
            for method in Parameters().parameters:
                if method[0] in methods:
                    try:
                        if method[2] == "custom":
                            exec("from Stuff.Parameters import {}".format(method[5]))
                        result.append(eval(method[1]))
                    except Exception as e:
                        if developer:
                            print(e)   
                        result.append("NA")
                        self.log.methodProblems[method[0]].append(file)
                        self.someProblem = True


            result = separator.join(map(str, result))
            if methods:
                result = separator + result               
            filename = returnName(filename = file, allFiles = self.root.fileStorage.arenafiles)      
            results += "\n" + filename + result
            
            if self.optionFrame.saveTags.get(): # tag inclusion in results
                if file in self.root.fileStorage.tagged:
                    results += separator + "1"
                else:
                    results += separator + "0"
            
            if len(self.filesToProcess) > 1:
                if self.stoppedProcessing:
                    writeResults(output, results)
                    self.log.stopped = file
                    self.log.writeLog()
                    self.status.set("Processing stopped")
                    return
                else:
                    self.progressWindow.addOne()


        writeResults(output, results)
        self.log.writeLog()

        # change of status bar and closing of progressWindow
        if len(self.filesToProcess) > 1:
            if self.someProblem:
                self.status.set("Files were processed.")
            else:
                self.status.set("Files were processed successfully.")
            self.progressWindow.destroy()
        else:
            if self.someProblem:
                self.status.set("File was processed.")
            else:
                self.status.set("File was processed successfully.")

        # removal of files from fileStorage if selected
        if self.optionFrame.clearFilesAfterProcessing.get():
            for file in self.filesToProcess:
                self.root.fileStorage.arenafiles.remove(file)
            self.fileStorageFrame.chosenVar.set(len(self.root.fileStorage.arenafiles))
            if not self.root.fileStorage.arenafiles:
                self.fileStorageFrame.removeFiles.state(["disabled"]) 
                self.process.state(["disabled"])

        if self.someProblem:
            ProcessingProblemDialog(self, self.log.filename)


    def checkProcessing(self):
        "method updating page after change of notebook tab"
        if self.root.fileStorage.arenafiles and self.saveToFrame.saveToVar.get():
            self.process.state(["!disabled"])
        else:
            self.process.state(["disabled"])

        if self.root.fileStorage.arenafiles or self.root.fileStorage.wrongfiles:
            self.fileStorageFrame.removeFiles.state(["!disabled"])
        else:
            self.fileStorageFrame.removeFiles.state(["disabled"])        

        self.fileStorageFrame.chosenVar.set(len(self.root.fileStorage.arenafiles))
        self.fileStorageFrame.nonMatchingVar.set(len(self.root.fileStorage.wrongfiles))



class Log():
    "class representing log of processing"
    def __init__(self, methods, startTime, stopTime, files, fileStorage, removeReflections,
                 saveTo):
        self.failedToLoad = []
        self.methods = methods
        self.methodProblems = {method: [] for method in self.methods}
        self.startTime = startTime
        self.stopTime = stopTime
        self.files = files
        self.stopped = False
        self.fileStorage = fileStorage
        self.removeReflections = removeReflections
        self.saveTo = saveTo
    

    def writeLog(self):
        "writes the log"
        filepath = optionGet("LogDirectory", os.path.join(os.getcwd(), "Stuff", "Logs"), "str")
        writeTime = localtime()
        self.filename = os.path.join(filepath, strftime("%y_%m_%d_%H%M%S", writeTime) + ".txt")

        self.problem = False
        for method in self.methods:
            if self.methodProblems[method]:
                self.problem = True           
            
        with open(self.filename, mode = "w") as logfile:
            # version
            logfile.write("CM Manager version " + ".".join(version()) + "\n\n")
            # log time
            logfile.write("Date: " + strftime("%d %b %Y", writeTime) + "\n")
            logfile.write("Time: " + strftime("%H:%M:%S", writeTime) + "\n\n\n")
            # problems
            if self.failedToLoad or self.problem or self.stopped:
                logfile.write("Errors:\n" + "-" * 20 + "\n")
                if self.stopped:
                    logfile.write("Processing stopped after: " + file + "\n\n")
                if self.failedToLoad:
                    logfile.write("Failed to load:\n\t")
                    logfile.write("\n\t".join(self.failedToLoad))
                    logfile.write("\n\n")
                if self.problem:
                    logfile.write("Failed to compute:\n")
                    for method in self.methods:
                        if self.methodProblems[method]:
                            logfile.write("\t" + method + ":\n\t\t")
                            logfile.write("\n\t\t".join(self.methodProblems[method]))
                            logfile.write("\n")
                    logfile.write("\n")
                logfile.write("-" * 20 + "\n\n")
            # methods
            logfile.write("Methods used:")
            if self.methods:
                for method in self.methods:
                    logfile.write("\n\t" + method)
                    if method in Parameters().options:
                        for option in Parameters().options[method]:
                            logfile.write("\n\t\t" + option[0] + ": " + str(option[1]))
            else:
                logfile.write("\n\tNone")
            logfile.write("\n\n\n")
            # time set
            logfile.write("Time set:\n")
            logfile.write("\tStart: " + "{:5.1f}".format(self.startTime) + " minutes\n")
            logfile.write("\tStop : " + "{:5.1f}".format(self.stopTime) + " minutes\n")
            logfile.write("\n\n")
            # save in file
            file = self.saveTo
            if not os.path.splitext(file)[1]:
                file += optionGet("DefProcessOutputFileType", ".txt", "str")
            logfile.write("Results saved in:\n\t" + os.path.abspath(file) + "\n\n\n")
            # reflections
            logfile.write("Reflections removed in:\n\t" + self.removeReflections + "\n\n\n")
            # files
            logfile.write("Files processed:")
            if self.stopped:
                index = self.files.index(self.stopped)
                if index == len(self.files):
                    for file in self.files[:index]:
                        logfile.write("\n\t" + file)
                        if file in self.fileStorage.tagged:
                            logfile.write("\tTagged")                            
                        if file in self.fileStorage.pairedfiles:
                            logfile.write("\n\t\tPaired with: " +
                                          self.fileStorage.pairedfiles[file])
                    logfile.write("\nStopped before processing following files:\n\t")
                    for file in self.files[(index + 1):]:
                        logfile.write("\n\t" + file)
                        if file in self.fileStorage.tagged:
                            logfile.write("\tTagged")                            
                        if file in self.fileStorage.pairedfiles:
                            logfile.write("\n\t\tPaired with: " +
                                          self.fileStorage.pairedfiles[file])
                else:
                    for file in self.files:
                        logfile.write("\n\t" + file)
                        if file in self.fileStorage.tagged:
                            logfile.write("\tTagged")                            
                        if file in self.fileStorage.pairedfiles:
                            logfile.write("\n\t\tPaired with: " +
                                          self.fileStorage.pairedfiles[file])
            else:
                for file in self.files:
                    logfile.write("\n\t" + file)
                    if file in self.fileStorage.tagged:
                        logfile.write("\tTagged")                            
                    if file in self.fileStorage.pairedfiles:
                        logfile.write("\n\t\tPaired with: " +
                                      self.fileStorage.pairedfiles[file])         
            logfile.close()
    






class ProgressWindow(Toplevel):
    "opens new window with progressbar and disables actions on other windows"
    def __init__(self, root, number, text = "processed"):
        super().__init__(root)
        
        self.root = root
        self.number = number
        self.title("Progress")
        self.focus_set()
        self.grab_set()
        placeWindow(self, 404, 80)
        self.geometry("+500+300")
        self.text = text
        self.resizable(FALSE, FALSE)

        # progressbar
        self.progress = ttk.Progressbar(self, orient = HORIZONTAL, length = 400,
                                        mode = "determinate")
        self.progress.configure(maximum = number)
        self.progress.grid(column = 0, row = 1, columnspan = 2, pady = 3, padx = 2)

        # cancel button
        self.cancel = ttk.Button(self, text = "Cancel", command = self.close)
        self.cancel.grid(column = 0, columnspan = 2, row = 2, pady = 2)

        # number of files label
        self.numFiles = StringVar()
        self.processed = 0
        self.processedFilesText = "{} out of {} files {}".format("{}", self.number, self.text)
        self.numFiles.set(self.processedFilesText.format(self.processed))
        self.numFilesLab = ttk.Label(self, textvariable = self.numFiles)
        self.numFilesLab.grid(row = 0, column = 1, sticky = E, pady = 2, padx = 2)

        # expected time label
        self.begintime = time()
        self.timeText = "Remaining time: {}"
        self.timeVar = StringVar()
        self.timeLab = ttk.Label(self, textvariable = self.timeVar)
        self.timeLab.grid(row = 0, column = 0, sticky = W, pady = 2, padx = 2)        

        
        self.protocol("WM_DELETE_WINDOW", lambda: self.close())


    def addOne(self):
        "called after one file is processed"
        self.progress.step(1)
        self.processed += 1
        self.numFiles.set(self.processedFilesText.format(self.processed))
        expectedTime = round((self.number - self.processed) *\
                             ((time() - self.begintime) / self.processed))
        self.timeVar.set(self.timeText.format(self.formatTime(expectedTime)))
        self.update()


    def formatTime(self, seconds):
        "returns string with the remaining time given the number of seconds left as attribute"
        if seconds > 60:
            minutes = seconds // 60
            seconds = seconds % 60
            if minutes > 5:
                return "{} minutes".format(minutes)
            elif minutes == 1:
                return "1 minute {} seconds".format(min([int(round(seconds, -1)), 55]))
            else:
                return "{} minutes {} seconds".format(int(minutes),
                                                      min([int(round(seconds, -1)), 55]))
        else:
            if seconds < 5:
                return "5 seconds"
            else:
                return "{} seconds".format(min([int(round(seconds * 2, -1) / 2), 55]))


    def close(self):
        "called to cancel or exit"
        self.root.stoppedProcessing = True
        self.destroy()
                    



def writeResults(file, results):
    "writes 'results' in a 'file'"
    if not os.path.splitext(file)[1]:
        file = file + optionGet("DefProcessOutputFileType", ".txt", "str")
    if not os.path.dirname(file):
        file = os.path.join(optionGet("ResultDirectory", os.getcwd(), "str"), file)
    if os.path.splitext(file)[1] == ".csv":
        results = [[item for item in line.split(",")] for line in results.split("\n")]
        with open(file, mode = "w", newline = "") as f:
            writer = csv.writer(f, dialect = "excel")
            writer.writerows(results)
            f.close()    
    else:
        outfile = open(file, "w")
        outfile.write(results)
        outfile.close()



class ParameterFrame(ttk.Labelframe):
    "helper class for Options representing frame containing default settings of parameters"
    def __init__(self, root, text = "Parameters"):
        super().__init__(root, text = text)

        basic = ttk.Labelframe(self, text = "Basic")
        advanced = ttk.Labelframe(self, text = "Advanced")
        double = ttk.Labelframe(self, text = "Double Avoidance")
        info = ttk.Labelframe(self, text = "Information")
        experimental = ttk.Labelframe(self, text = "Experimental")
        custom = ttk.Labelframe(self, text = "Custom Written")
        basic.grid(column = 0, row = 0, sticky = (N, S, W), padx = 3, pady = 2)
        advanced.grid(column = 1, row = 0, sticky = (N, S, W), padx = 3, pady = 2)
        double.grid(column = 2, row = 0, sticky = (N, S, W), padx = 3, pady = 2)
        info.grid(column = 3, row = 0, sticky = (N, S, W), padx = 3, pady = 2)
        experimental.grid(column = 4, row = 0, sticky = (N, S, W), padx = 3, pady = 2)
        custom.grid(column = 5, row = 0, sticky = (N, S, W), padx = 3, pady = 2)

        basicNum = 0
        advancedNum = 0
        doubleNum = 0
        infoNum = 0
        experimentalNum = 0
        customNum = 0
        for parameter in Parameters().parameters:
            if parameter[2] == "basic":
                 rowNum = basicNum
                 basicNum += 1
            elif parameter[2] == "advanced":
                 rowNum = advancedNum
                 advancedNum += 1
            elif parameter[2] == "double":
                 rowNum = doubleNum
                 doubleNum += 1
            elif parameter[2] == "info":
                 rowNum = infoNum
                 infoNum += 1
            elif parameter[2] == "experimental":
                 rowNum = experimentalNum
                 experimentalNum += 1                       
            elif parameter[2] == "custom":
                 rowNum = customNum
                 customNum += 1                 
            exec("self.%s = BooleanVar()" % (parameter[0].replace(" ", "") + "Var"))
            exec("self.%sVar.set(%s)" % (parameter[0].replace(" ", ""), parameter[3]))
            exec("""self.%sBut = ttk.Checkbutton(%s, text = '%s', variable = self.%sVar,
                 onvalue = True)""" % (parameter[0].replace(" ", ""), parameter[2], parameter[0],\
                  parameter[0].replace(" ", "")))
            exec("self.%sBut.grid(column = 0, row = %i, sticky = (S, W), padx = 1, pady = 2)" %\
                 (parameter[0].replace(" ", ""), rowNum))



class OptionFrame(ttk.Labelframe):
    "contains options for processing"
    def __init__(self, root, text = "Options"):
        super().__init__(root, text = text)

        self.root = root
        if type(self.root) is Processor:
            self.fileStorage = self.root.root.fileStorage

        # variables
        self.processWhat = StringVar()
        self.removeReflectionsWhere = StringVar()
        self.saveTags = BooleanVar()
        self.clearFilesAfterProcessing = BooleanVar()

        self.processWhat.set(optionGet("ProcessWhat", "all files", "str"))
        self.removeReflectionsWhere.set(optionGet("RemoveReflectionsWhere", "no files", "str"))
        self.saveTags.set(optionGet("DefSaveTags", False, "bool"))
        self.clearFilesAfterProcessing.set(optionGet("DefClearFilesAfterProcessing", False,
                                                     "bool"))

        # labels
        self.processLabel = ttk.Label(self, text = "Process")
        self.removeReflectionsLabel = ttk.Label(self, text = "Remove reflections in")
        self.saveTagsLabel = ttk.Label(self, text = "Save tags")
        self.clearFilesLabel = ttk.Label(self, text = "Clear files after processing")

        self.processLabel.grid(column = 0, row = 0, sticky = E, padx = 3)
        self.removeReflectionsLabel.grid(column = 0, row = 1, sticky = E, padx = 3)
        self.saveTagsLabel.grid(column = 0, row = 2, sticky = E, padx = 3)
        self.clearFilesLabel.grid(column = 0, row = 3, sticky = E, padx = 3)

        # comboboxes
        self.processCombobox = ttk.Combobox(self, textvariable = self.processWhat,
                                            justify = "center", width = 15, state = "readonly")
        self.processCombobox["values"] = ("all files", "only tagged", "only untagged")

        self.removeReflectionsCombobox = ttk.Combobox(self, justify = "center", textvariable =
                                                      self.removeReflectionsWhere, width = 15,
                                                      state = "readonly")
        self.removeReflectionsCombobox["values"] = ("no files", "tagged files", "untagged files",
                                                    "all files")

        self.processCombobox.grid(column = 1, row = 0, sticky = W, padx = 2)
        self.removeReflectionsCombobox.grid(column = 1, row = 1, sticky = W, padx = 2)

        # checkbuttons
        self.saveTagsCheckbutton = ttk.Checkbutton(self, variable = self.saveTags, onvalue = True,
                                                   offvalue = False)
        self.saveTagsCheckbutton.grid(column = 1, row = 2)
        self.clearFilesCheckbutton = ttk.Checkbutton(self, onvalue = True, offvalue = False,
                                                     variable = self.clearFilesAfterProcessing)
        self.clearFilesCheckbutton.grid(column = 1, row = 3)
        

    def removeReflections(self, file):
        "returns True is reflections should be removed in the file in argument"
        where = self.removeReflectionsWhere.get()
        if where == "no files":
            return False
        elif where == "tagged files":
            if file in self.fileStorage.tagged:
                return True
            else:
                return False
        elif where == "untagged files":
            if file in self.fileStorage.tagged:
                return False
            else:
                return True
        elif where == "all files":
            return True
        else:
            raise Exception("Error in OptionFrame.removeReflections method") # odstranit


    def processFile(self, file):
        "returns True if the file in argument should be processed"
        if self.processWhat.get() == "all files":
            return True
        elif self.processWhat.get() == "only tagged":
            if file in self.fileStorage.tagged:
                return True
            else:
                return False
        elif self.processWhat.get() == "only untagged":
            if file in self.fileStorage.tagged:
                return False
            else:
                return True        
        else:
            raise Exception("Error in OptionFrame.processFile method") # odstranit



class ProcessingProblemDialog(Toplevel):
    "showed when some problem occured during processing"
    def __init__(self, root, logfile):
        super().__init__(root)
        
        self.root = root
        self.title("Warning")
        self.grab_set()
        self.focus_set()
        placeWindow(self, 250, 100)
        self.resizable(False, False)
        self.logfile = logfile
        self.minsize(250, 100)
        
        # buttons
        self.cancelBut = ttk.Button(self, text = "Cancel", command = self.cancelFun)
        self.cancelBut.grid(column = 0, row = 2, pady = 2)
        self.showBut = ttk.Button(self, text = "Open log", command = self.showFun)
        self.showBut.grid(column = 1, row = 2, pady = 2)

        # text
        self.label = ttk.Label(self, text = "Some problem occured during processing.\n" +\
                               "See log for details.", justify = "center")
        self.label.grid(column = 0, columnspan = 2, row = 0, padx = 8, pady = 5,
                        sticky = (N, S, E, W))
      
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 1)
        

    def cancelFun(self):
        "function of cancel button"
        self.destroy()

    def showFun(self):
        "function of open log function"
        os.startfile(self.logfile)



def main():
    from filestorage import FileStorage
    testGUI = Tk()
    testGUI.fileStorage = FileStorage()
    processor = Processor(testGUI)
    processor.grid()
    testGUI.mainloop()


if __name__ == "__main__": main()
