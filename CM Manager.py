"""
Carousel Maze Manager - a program for analysis of data from behavioral neuroscience tasks
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
from urllib.request import urlopen
from time import localtime, strftime

import traceback
import os.path
import os
import sys
sys.path.append(os.path.join(os.getcwd(), "Stuff", "Modules"))


from controller import Controller
from explorer import Explorer
from processor import Processor
from menu import MenuCM
from filestorage import FileStorage
from optionget import optionGet
from options import optionWrite
from dialogbox import DialogBox
from version import version
from window import placeWindow


class GUI(Tk):
    "represents GUI"
    def __init__(self):
        super().__init__()
   
        self.title("CM Manager " + ".".join(version()))
        self.option_add("*tearOff", FALSE)
        self.resizable(FALSE, FALSE)
        
        '''
        used when size of the window is changed for placeWindow arguments     
        self.after(50, lambda: print(self.winfo_width()))
        self.after(50, lambda: print(self.winfo_height()))
        '''
        placeWindow(self, 1010, 786)

        # notebook
        self.selectFunction = ttk.Notebook(self)
        self.selectFunction.grid()

        # FileStorage is associated with the Notebook
        self.selectFunction.fileStorage = FileStorage()
        
        self.processor = Processor(self.selectFunction)
        self.explorer = Explorer(self.selectFunction)
        self.controller = Controller(self.selectFunction)

        notepageWidth = 20
        self.selectFunction.add(self.processor, text = "{:^{}}".format("Process", notepageWidth))
        self.selectFunction.add(self.explorer, text = "{:^{}}".format("Explore", notepageWidth))
        self.selectFunction.add(self.controller, text = "{:^{}}".format("Control", notepageWidth))

        self.selectFunction.bind("<<NotebookTabChanged>>", lambda e: self.checkProcessing(e))
            
        # menu
        self["menu"] = MenuCM(self)

        # checks for new messages and versions on the web
        if optionGet("CheckMessages", True, "bool"):
            self.onStart()

        self.mainloop()



    def onStart(self):
        "checks web for new version and post"
        try:
            self.checkNewVersion()
        except Exception:
            pass

        try:
            self.checkNewPost()
        except Exception:
            pass       


    def checkNewVersion(self):
        "checks whether there is a new version available"
        newVersion = self.returnSiteContent("http://www.cmmanagerweb.appspot.com/version").\
                     split(".")
        versionSeen = optionGet("DontShowVersion", version(), "list")
        for i in range(3):
            if int(newVersion[i]) > int(versionSeen[i]):
                DialogBox(self, title = "New version available", message =
                          self.returnSiteContent(
                                        "http://www.cmmanagerweb.appspot.com/version/message"),
                          dontShowOption = "DontShowVersion", optionValue = newVersion)
                break            


    def checkNewPost(self):
        "checks whether there is some post with new information on the web"
        currentPost = optionGet("WebPostNumber", 0, "int")
        webPostNumber = int(self.returnSiteContent("http://www.cmmanagerweb.appspot.com/post"))
        if  webPostNumber > currentPost:
            DialogBox(self, "New information", self.returnSiteContent(
                "http://www.cmmanagerweb.appspot.com/post/message"))
            optionWrite("WebPostNumber", webPostNumber)


    def returnSiteContent(self, link):
        "return text obtained from web site"
        site = urlopen(link)
        text = site.read()
        site.close()
        text = str(text)[2:-1]
        return text       


    def checkProcessing(self, event):
        """checks whether it is possible for processor and controller to process files and change
        states of buttons accordingly"""
        self.processor.checkProcessing()
        self.controller.checkProcessing()
        self.explorer.checkProcessing()

     
            

def main():
    if optionGet("Developer", False, 'bool'):
        GUI()
    else:
        try:
            filepath = os.path.join(os.getcwd(), "Stuff", "Bugs")
            writeTime = localtime()
            filename = os.path.join(filepath, strftime("%y_%m_%d_%H%M%S", writeTime) +
                                    "_bugs" + ".txt")
            with open(filename, mode = "w") as bugfile:
                sys.stderr = bugfile
                GUI()
        finally:
            bugfile.close()


   
if __name__ == "__main__": main()

