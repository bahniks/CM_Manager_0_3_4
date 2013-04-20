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

from tkinter.filedialog import askdirectory
from tkinter import *
from tkinter import ttk, messagebox
import os.path
import os


from optionget import optionGet
from processor import ParameterFrame, OptionFrame
from cm import Parameters
from commonframes  import TimeFrame
from window import placeWindow


def optionWrite(option, newValue):
    """writes newValue as an option into file Option.txt located in directory 'Stuff' in working
    directory"""
    if not os.path.exists(os.path.join(os.getcwd(), "Stuff")):
        raise Exception("Working directory doesn't contain Stuff directory")

    optionFile = os.path.join(os.getcwd(), "Stuff", "Options.txt")

    if not os.path.exists(optionFile):
        open(optionFile, mode = "w").close()

    optString = "%|" + option + "|%"
    outfile = open(optionFile, mode = "r")
    tempfile = open(os.path.join(os.getcwd(), "Stuff", "~Options.txt"), mode = "w")

    optionExists = False
    for line in outfile:
        if optString in line:
            tempfile.write(optString + " " + str(newValue) + "\n")
            optionExists = True
        else:
            tempfile.write(line)
    if not optionExists:
        tempfile.write(optString + " " + str(newValue) + "\n")

    outfile.close()
    tempfile.close()
    os.remove(optionFile)
    os.rename(os.path.join(os.getcwd(), "Stuff", "~Options.txt"), optionFile)
    


def doBool(value):
    "method to change string to bool in options write function"
    return bool(eval(value))


class RadioFrame(ttk.Labelframe):
    "class containing radiobuttons for setting options"
    def __init__(self, root, text, optionName, default, options):
        super().__init__(root, text = text)
        self.optionName = optionName
        self.variable = StringVar()
        self.variable.set(optionGet(optionName, default, "str"))
        for count, option in enumerate(options):
            exec("self.{}RB = ttk.Radiobutton(self, text = '{}', variable = self.variable, \
                 value = '{}')".format(option.replace(" ", "_"), option, option))
            exec("self.{}RB.grid(row = count, column = 0, padx = 2, pady = 2, sticky = W)".format(
                 option.replace(" ", "_")))

    def get(self):
        "called when options are saved by root (i.e. Option Toplevel)"
        return "'" + self.variable.get() + "'"


class ChooseDirectoryFrame(ttk.Labelframe):
    "represents frame for selection of directory"
    def __init__(self, root, text, optionName, default):
        super().__init__(root, text = text)
        
        self.root = root
        self.currentDir = optionGet(optionName, default, "str")

        self.directory = StringVar()
        self.directory.set(self.currentDir)

        self.button = ttk.Button(self, text = "Choose", command = self.chooseFun)
        self.button.grid(column = 1, row = 0, padx = 3, pady = 1)

        self.entry = ttk.Entry(self, textvariable = self.directory, width = 70)
        self.entry.grid(column = 0, row = 0, padx = 3, pady = 1, sticky = (E, W))

        self.columnconfigure(0, weight = 1)

    def chooseFun(self):
        "opens dialog for directory selection"
        newDirectory = askdirectory(parent = self.root, initialdir = self.currentDir,
                                 title = "Choose a directory")
        if newDirectory:
            self.directory.set(newDirectory)

    def get(self):
        "returns chosen directory"
        return self.directory.get()
        
        

class OptionsCM(Toplevel):
    "options window reachable from menu"
    def __init__(self, root):
        super().__init__(root)
        self.title("Options")
        self.grab_set()
        self.focus_set()
        self.resizable(FALSE, FALSE)
        placeWindow(self, 824, 844)
        self["padx"] = 10
        self["pady"] = 10
        
        self.parametersF = ParameterFrame(self, "Default parameters")

        # default filetype of processor output
        self.fileTypeVar = StringVar()
        self.fileTypeVar.set(optionGet("DefProcessOutputFileType", ".txt", "str"))

        self.fileTypeFrame = ttk.Labelframe(self, text = "Default output filetype")

        self.txtRadioBut = ttk.Radiobutton(self.fileTypeFrame, text = ".txt",
                                           variable = self.fileTypeVar, value = ".txt")
        self.csvRadioBut = ttk.Radiobutton(self.fileTypeFrame, text = ".csv",
                                           variable = self.fileTypeVar, value = ".csv")
        
        self.txtRadioBut.grid(row = 1, column = 0, padx = 2, pady = 2, sticky = W)
        self.csvRadioBut.grid(row = 0, column = 0, padx = 2, pady = 2, sticky = W)

        # output separator
        self.separatorVar = StringVar()
        self.separatorVar.set(optionGet("ResultSeparator", ",", "str"))

        self.separatorFrame = ttk.Labelframe(self, text = "Result separator")

        self.commaRadioBut = ttk.Radiobutton(self.separatorFrame, text = "Comma",
                                             variable = self.separatorVar, value = ",")
        self.semicolonRadioBut = ttk.Radiobutton(self.separatorFrame, text = "Semicolon",
                                                 variable = self.separatorVar, value = ";")        
        self.tabRadioBut = ttk.Radiobutton(self.separatorFrame, text = "Tab",
                                           variable = self.separatorVar, value = "\t")
        
        self.commaRadioBut.grid(row = 0, padx = 2, pady = 2, sticky = W)
        self.semicolonRadioBut.grid(row = 1, padx = 2, pady = 2, sticky = W)
        self.tabRadioBut.grid(row = 2, padx = 2, pady = 2, sticky = W)

        # save filename as full path
        self.saveFilenameAs = RadioFrame(self, text = "Save (show) filename as:",
                                         optionName = "SaveFullPath", default = "Basename",
                                         options = ["Basename", "Full path", "Unique path"])

        # selection of directories
        self.directoriesFrame = ttk.Frame(self)
        self.directoriesFrame.columnconfigure(0, weight = 1)
        self.directoryOptions = [
            ("Default directory for file selection", "FileDirectory", os.getcwd()),
            ("Default directory for results", "ResultDirectory", os.getcwd()),
            ("Directory for saving of processing logs", "LogDirectory",
             os.path.join(os.getcwd(), "Stuff", "Logs")),
            ("Directory for images", "ImageDirectory", os.getcwd()),
            ("Directory for saving of selected files", "SelectedFilesDirectory",
             os.path.join(os.getcwd(), "Stuff", "Selected files"))]
        for count, option in enumerate(self.directoryOptions):
            exec("""self.{1} = ChooseDirectoryFrame(self.directoriesFrame, '{0}', '{1}', \
                 r'{2}')""".format(*option))
            exec("self.{}.grid(row = {}, column = 0, pady = 2, padx = 2, sticky = (E, W))".format(
                option[1], count))

        # default time
        self.timeLabFrame = ttk.Labelframe(self, text = "Default time")
        self.timeFrame = TimeFrame(self.timeLabFrame)
        self.timeFrame.grid(row = 0, column = 0)

        # processor options
        self.processorOptions = OptionFrame(self, text = "Default process options")

        # checking messages
        self.messageCheckingFrame = ttk.Labelframe(self, text = "Messages and new versions")
        self.messageCheckingVar = BooleanVar()
        self.messageCheckingVar.set(optionGet("CheckMessages", True, "bool"))
        self.messageCheckingChB = ttk.Checkbutton(self.messageCheckingFrame,
                                                  variable = self.messageCheckingVar,
                                                  onvalue = True, offvalue = False,
                                                  text = "Check messages and new versions")
        self.messageCheckingChB.grid(column = 0, row = 0)
        
        # buttons
        self.buttonFrame = ttk.Frame(self)
        self.buttonFrame.columnconfigure(1, weight = 1)

        self.saveBut = ttk.Button(self.buttonFrame, text = "Save", command = self.saveFun)
        self.okBut = ttk.Button(self.buttonFrame, text = "Ok", command = self.okFun)
        self.cancelBut = ttk.Button(self.buttonFrame, text = "Cancel", command = self.cancelFun)

        self.saveBut.grid(column = 0, row = 0, padx = 3, pady = 2, sticky = (W))
        self.okBut.grid(column = 1, row = 0, padx = 3, pady = 2)
        self.cancelBut.grid(column = 2, row = 0, padx = 3, pady = 2, sticky = (E))

        # grid of self contents        
        self.parametersF.grid(row = 0, column = 0, columnspan = 4, sticky = (N, W), padx = 4,
                              pady = 2)
        self.fileTypeFrame.grid(row = 2, column = 0, columnspan = 2, padx = 3, pady = 4,
                                sticky = (W, N, E, S))
        self.buttonFrame.grid(row = 8, column = 0, columnspan = 4, padx = 3, pady = 4,\
                              sticky = (E, W, N, S))
        self.separatorFrame.grid(row = 3, column = 0, columnspan = 2, padx = 3, pady = 4,
                                 sticky = (W, N, E))
        self.saveFilenameAs.grid(row = 2, column = 2, padx = 3, pady = 4, sticky = (N, W, E))
        self.directoriesFrame.grid(row = 5, column = 0, columnspan = 5, padx = 3, pady = 8,
                                   sticky = (N, W, E))
        self.timeLabFrame.grid(row = 2, column = 3, padx = 3, pady = 4, sticky = (N, W))
        self.processorOptions.grid(row = 3, column = 2, pady = 4, padx = 4, sticky = (N, W),
                                   columnspan = 2, rowspan = 2)
        self.messageCheckingFrame.grid(row = 4, column = 0, columnspan = 2, sticky = (N, W),
                                       pady = 3, padx = 3)
                                   
        
    def saveFun(self):
        "saves all options"
        for parameter in Parameters().parameters:
            optionWrite(parameter[4], bool(eval(("self.parametersF." +\
                                                 parameter[0].replace(" ", "") + "Var.get()"
                                                 ))))
        optionWrite("DefProcessOutputFileType", "'" + self.fileTypeVar.get() + "'")
        optionWrite("SaveFullPath", self.saveFilenameAs.get())
        optionWrite("ResultSeparator", "'" + self.separatorVar.get() + "'")
        optionWrite("DefStartTime", self.timeFrame.startTimeVar.get())
        optionWrite("DefStopTime", self.timeFrame.timeVar.get())
        optionWrite("ProcessWhat", "'" + self.processorOptions.processWhat.get() + "'")
        optionWrite("RemoveReflectionsWhere",
                    "'" + self.processorOptions.removeReflectionsWhere.get() + "'")
        optionWrite("DefSaveTags", self.processorOptions.saveTags.get())
        optionWrite("DefClearFilesAfterProcessing",
                    self.processorOptions.clearFilesAfterProcessing.get())
        optionWrite("CheckMessages", bool(self.messageCheckingVar.get()))
        for option in self.directoryOptions:
            directory = eval("self.{}.get()".format(option[1])).rstrip("\/")
            if os.path.exists(directory):
                optionWrite(option[1], "r'" + directory  + "'")
            else:
                messagebox.showinfo(message = "Directory " + directory + " does not exist.",
                                    icon = "error", parent = self, title = "Error",
                                    detail = "Choose an existing directory.")
                return False
        return True
                

    def okFun(self):
        "saves options and exits"
        if self.saveFun():
            self.destroy()


    def cancelFun(self):
        "destroys the window"
        self.destroy()     


        
class AdvancedOptions(Toplevel):
    "advanced options window reachable from menu"
    def __init__(self, root):
        super().__init__(root)
        self.title("Parameter settings")
        self.grab_set()
        self.focus_set()
        self.resizable(FALSE, FALSE)   
        placeWindow(self, 389, 682)
        self["padx"] = 10
        self["pady"] = 10
         

        self.saveBut = ttk.Button(self, text = "Save", command = self.saveFun)
        self.okBut = ttk.Button(self, text = "Ok", command = self.okFun)
        self.cancelBut = ttk.Button(self, text = "Cancel", command = self.cancelFun)

        self.saveBut.grid(column = 0, row = 3, padx = 3, pady = 2)
        self.okBut.grid(column = 1, row = 3, padx = 3, pady = 2)
        self.cancelBut.grid(column = 2, row = 3, padx = 3, pady = 2)

        
        # parameter settings
        self.parSettingsFrame = ttk.Frame(self)
        self.parSettingsFrame.grid(row = 1, column = 0, columnspan = 3, padx = 3, pady = 4,
                                   sticky = (N, W))
        self.parSettingsFrame.columnconfigure(1, weight = 1)
        
        self.RlabelWidth = 8
        self.EntryWidth = 10
        

        # thigmotaxis - mozno nahradit pomoci ParameterOptionFrame !
        self.thigmotaxisFrame = ttk.Labelframe(self.parSettingsFrame, text = "Thigmotaxis")
        self.thigmotaxisFrame.grid(column = 0, row = 2, columnspan = 3, pady = 3, padx = 3,
                                   sticky = (W, E))
        self.thigmotaxisFrame.columnconfigure(0, weight = 1)
                             
        self.thigmotaxisVar = StringVar()
        self.thigmotaxisVar.set(optionGet("ThigmotaxisPercentSize", 20, ["int", "float"]))

        self.thigmotaxisEntry = ttk.Entry(self.thigmotaxisFrame,
                                          textvariable = self.thigmotaxisVar,
                                          width = self.EntryWidth, justify = "right")
        self.thigmotaxisEntry.grid(column = 1, row = 1, padx = 1, pady = 2)
        self.thigmotaxisLab = ttk.Label(self.thigmotaxisFrame, text = "Annulus width:")
        self.thigmotaxisLab.grid(column = 0, row = 1, padx = 1, pady = 2, sticky = E)
        self.percentLab = ttk.Label(self.thigmotaxisFrame, text = "%", width = self.RlabelWidth)
        self.percentLab.grid(column = 2, row = 1, padx = 1, pady = 2, sticky = W)


        # setting of Time in chosen sector parameter
        self.TimeInChosenFrame = ttk.Labelframe(self.parSettingsFrame,
                                                text = "Time in chosen sector")
        self.TimeInChosenFrame.grid(column = 0, row = 0, columnspan = 3, pady = 3, padx = 3)
                               
        self.TimeInChosenWidthVar = StringVar()
        self.TimeInChosenWidthVar.set(optionGet('WidthParTimeInChosen', 'default',
                                                ['int', 'float']))
        self.TimeInChosenWidthEntry = ttk.Entry(self.TimeInChosenFrame, textvariable =
                                                self.TimeInChosenWidthVar, width = self.EntryWidth,
                                                justify = "right")
        self.TimeInChosenWidthEntry.grid(column = 1, row = 1, padx = 2, pady = 2)

        self.TimeInChosenWidthLab = ttk.Label(self.TimeInChosenFrame, text =
                                              "Width of sector ('default' if same as target):")
        self.TimeInChosenWidthLab.grid(column = 0, row = 1, pady = 2, sticky = (E))
        self.DegreesLab = ttk.Label(self.TimeInChosenFrame, text = "°", width = self.RlabelWidth)
        self.DegreesLab.grid(column = 2, row = 1, pady = 2)

        self.TimeInChosenAngleVar = StringVar()
        self.TimeInChosenAngleVar.set(optionGet('AngleParTimeInChosen', 0, ['int', 'float']))
        self.TimeInChosenAngleEntry = ttk.Entry(self.TimeInChosenFrame, textvariable =
                                                self.TimeInChosenAngleVar, width = self.EntryWidth,
                                                justify = "right")
        self.TimeInChosenAngleEntry.grid(column = 1, row = 0, padx = 2, pady = 2)

        self.TimeInChosenAngleLab = ttk.Label(self.TimeInChosenFrame,
                                              text = "Center of sector relative to the target:")
        self.TimeInChosenAngleLab.grid(column = 0, row = 0, pady = 2, sticky = (E))
        self.DegreesLab2 = ttk.Label(self.TimeInChosenFrame, text = "°", width = self.RlabelWidth)
        self.DegreesLab2.grid(column = 2, row = 0, pady = 2)

        
        # setting of Time in sectors parameter
        self.TimeInSectorsFrame = ttk.Labelframe(self.parSettingsFrame,
                                                text = "Time in sectors")
        self.TimeInSectorsFrame.grid(column = 0, row = 1, columnspan = 3, pady = 3, padx = 3)
                               
        self.TimeInSectorsWidthVar = StringVar()
        self.TimeInSectorsWidthVar.set(optionGet('WidthParTimeInSectors', 'default',
                                                ['int', 'float']))
        self.TimeInSectorsWidthEntry = ttk.Entry(self.TimeInSectorsFrame, textvariable =
                                                 self.TimeInSectorsWidthVar, width =
                                                 self.EntryWidth, justify = "right")
        self.TimeInSectorsWidthEntry.grid(column = 1, row = 1, padx = 2, pady = 2)

        self.TimeInSectorsWidthLab = ttk.Label(self.TimeInSectorsFrame, text =
                                              "Width of sector ('default' if same as target):")
        self.TimeInSectorsWidthLab.grid(column = 0, row = 1, pady = 2, sticky = (E))
        self.DegreesLab3 = ttk.Label(self.TimeInSectorsFrame, text = "°", width = self.RlabelWidth)
        self.DegreesLab3.grid(column = 2, row = 1, pady = 2)


        # setting of Total distance parameter
        self.totalDistance = ParameterOptionFrame(self.parSettingsFrame, "Total distance",
                                                  (("Sampling after every:", (
                                                      'StrideParTotalDistance', 25, 'int'),
                                                    "rows"),
                                                   ("Minimal distance counted:", (
                                                       'MinDiffParTotalDistance', 0,
                                                       ['int', 'float']), "pixels")))
        self.totalDistance.grid(column = 0, row = 3, columnspan = 3, pady = 3, padx = 3,
                                sticky = (W, E))

        # setting of Maximum time of immobility parameter
        self.maximumTimeImmobility = ParameterOptionFrame(self.parSettingsFrame,
                                                          "Maximum time of immobility",
                                                          (("Minimum speed counted:", (
                                                              'MinSpeedMaxTimeImmobility', 10,
                                                              ['int', 'float']), "cm/s"),
                                                           ("Computed from every:",
                                                            ('SkipMaxTimeImmobility', 12, ['int']),
                                                            "rows"),
                                                           ("Averaged across:",
                                                            ('SmoothMaxTimeImmobility', 2,
                                                             ['int']), "intervals")))
        self.maximumTimeImmobility.grid(column = 0, row = 4, columnspan = 3, pady = 3, padx = 3,
                                        sticky = (W, E))

        # setting of Periodicity parameter
        self.periodicity = ParameterOptionFrame(self.parSettingsFrame, "Periodicity",
                                                (("Minimum speed counted:", ('MinSpeedPeriodicity',
                                                                           10, ['int', 'float']),
                                                 "cm/s"),
                                                ("Computed from every:", ('SkipPeriodicity', 12,
                                                                          ['int']), "rows"),
                                                ("Averaged across:", ('SmoothPeriodicity', 2,
                                                                      ['int']), "intervals"),
                                                ("Minimum time of interval:",
                                                 ('MinTimePeriodicity', 9, ['int', 'float',
                                                                            'list']), "seconds")))                                                                     
        self.periodicity.grid(column = 0, row = 5, columnspan = 3, pady = 3, padx = 3,
                              sticky = (W, E))                                                       

        # setting of Proportion of time moving parameter
        self.percentMobility = ParameterOptionFrame(self.parSettingsFrame,
                                                    "Proportion of time moving",
                                                    (("Minimum speed counted:",
                                                      ('MinSpeedPercentMobility', 5, ['int',
                                                                                      'float']),
                                                      "cm/s"),
                                                     ("Computed from every:",
                                                      ('SkipPercentMobility', 12, 'int'), "rows"),
                                                     ("Averaged across:",
                                                      ('SmoothPercentMobility', 2, 'int'),
                                                      "intervals")))
        self.percentMobility.grid(column = 0, row = 6, columnspan = 3, pady = 3, padx = 3,
                                  sticky = (W, E))

        # setting of Proportion of time moving parameter
        self.speedAfterShock = ParameterOptionFrame(self.parSettingsFrame,
                                                    "Median speed after shock",
                                                    [("Computed from every:",
                                                     ('SkipSpeedAfterShock', 25, 'int'), "rows")])
        self.speedAfterShock.grid(column = 0, row = 7, columnspan = 3, pady = 3, padx = 3,
                                  sticky = (W, E))
                                                    

    def saveFun(self):
        optionWrite('WidthParTimeInChosen', self.TimeInChosenWidthVar.get())
        optionWrite('AngleParTimeInChosen', self.TimeInChosenAngleVar.get())
        optionWrite('ThigmotaxisPercentSize', self.thigmotaxisVar.get())
        optionWrite('WidthParTimeInSectors', self.TimeInSectorsWidthVar.get())
        self.totalDistance.save()
        self.maximumTimeImmobility.save()
        self.periodicity.save()
        self.percentMobility.save()
        self.speedAfterShock.save()
        

    def okFun(self):
        self.saveFun()
        self.destroy()


    def cancelFun(self):
        self.destroy()




class ParameterOptionFrame(ttk.Labelframe):
    """
    frame with options for one parameter
        options = ((text, option, sign), (...)), where option = (option name, default, types)
    """
    def __init__(self, root, name, options, entryWidth = 10, rightLabWidth = 8):
        super().__init__(root, text = name)
        self.options = options
        
        for row, option in enumerate(options):
            exec("self.{}Var = StringVar()".format(option[1][0]))
            exec("self.{}Var.set({})".format(option[1][0], optionGet(*option[1])))
            exec("self.{}Lab = ttk.Label(self, text = '{}')".format(option[1][0],
                                                                              option[0]))
            exec("self.{}Lab.grid(column = 0, row = {}, pady = 2, sticky = E)".format(option[1][0],
                                                                                      row))
            exec("""self.{}Entry = ttk.Entry(self, textvariable = self.{}Var, width = {}, justify =
                    'right')""".format(option[1][0], option[1][0], entryWidth))
            exec("self.{}Entry.grid(column = 1, row = {}, padx = 2, pady = 2)".format(option[1][0],
                                                                                      row))
            exec("self.{}Sign = ttk.Label(self, text = '{}', width = {})".format(
                option[1][0], option[2], rightLabWidth))
            exec("self.{}Sign.grid(column = 2, row = {}, pady = 2, sticky = W)".format(
                option[1][0], row))

        self.columnconfigure(0, weight = 1)


    def save(self):
        for option in self.options:
            optionWrite(option[1][0], eval("self.{}Var.get()".format(option[1][0])))

        
