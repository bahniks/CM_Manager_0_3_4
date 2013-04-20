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
from tkinter import ttk, messagebox
import webbrowser
import os.path
import os

from options import OptionsCM, AdvancedOptions
from helpCMM import HelpCM
from tools import saveFileStorage, loadFileStorage
from window import placeWindow
import version



class MenuCM(Menu):
    "menu of main window"
    def __init__(self, root):
        super().__init__(root)
        self.root = root

        self.menu_file = Menu(self)
        self.menu_options = Menu(self)
        self.menu_tools = Menu(self)
        self.menu_help = Menu(self)
        
        menuWidth = 8
        self.add_cascade(menu = self.menu_file, label = "{:^{}}".format("File", menuWidth))
        self.add_cascade(menu = self.menu_options, label = "{:^{}}".format("Options", menuWidth))
        self.add_cascade(menu = self.menu_tools, label = "{:^{}}".format("Tools", menuWidth))
        self.add_cascade(menu = self.menu_help, label = "{:^{}}".format("Help", menuWidth))

        self.menu_file.add_command(label = "Exit", command = self.exitCM)
        self.menu_options.add_command(label = "Options", command = self.options)
        self.menu_options.add_command(label = "Parameter settings", command = self.advOptions)
        self.menu_tools.add_command(label = "Save selected files", command = self.saveLoadedFiles)
        self.menu_tools.add_command(label = "Load selected files", command = self.loadSavedFiles)
        self.menu_help.add_command(label = "Help", command = self.helpCM)
        self.menu_help.add_command(label = "About", command = self.about)

    def exitCM(self):
        self.root.destroy()

    def options(self):
        OptionsCM(self.root)

    def advOptions(self):
        AdvancedOptions(self.root)

    def saveLoadedFiles(self):
        saveFileStorage(self.root)
        
    def loadSavedFiles(self):
        loadFileStorage(self.root)

    def helpCM(self):
        try:
            HelpCM(self.root)
        except Exception as e:
            messagebox.showinfo(message = e, title = "Error", icon = "error")
            
    def about(self):
        AboutCM(self.root)

        

class AboutCM(Toplevel):
    "about window reachable from menu"
    def __init__(self, root):
        super().__init__(root)
        self["padx"] = 4
        self["pady"] = 4

        self.version = ".".join(version.version())        
        self.title("About")
        self.resizable(FALSE, FALSE)
        placeWindow(self, 488, 303)
        
        line12 = "Carousel Maze Manager\nVersion " + self.version + "\n" + version.date() + "\n\n"
        line5 = "Copyright "+ version.copyleft() + " Štěpán Bahník\nbahniks@seznam.cz\n\n"
        line6 = "This program comes with ABSOLUTELY NO WARRANTY.\n"
        line8 = "This is free software, and you are welcome to redistribute\n"
        line9 = "it under certain conditions; click "
        line10 = "here"
        line11 = " for details.\n\n"
        
        self.aboutText = Text(self, height = 15, width = 58, relief = "flat",
                              background = self.cget("background"))
        self.aboutText.grid(column = 0, row = 0, padx = 6, pady = 6)

        text = line12 + line5 + line6 + line8 + line9
        
        self.aboutText.insert("end", text)
        self.aboutText.insert("end", line10, "link")
        self.aboutText.insert("end", line11)

        self.aboutText.tag_configure("link", foreground = "blue")
        self.aboutText.tag_bind("link", "<1>", lambda e: self.link(e))
        self.aboutText.tag_bind("link", "<Enter>", lambda e: self._enter(e))
        self.aboutText.tag_bind("link", "<Leave>", lambda e: self._leave(e))

        filepath = os.path.join(os.getcwd(), "Stuff", "Modules", "GNUlogo.gif")
        self.logo = PhotoImage(file = filepath)
        self.aboutText.insert("end", " "*21)
        self.aboutText.image_create("end", image = self.logo)
        
        self.aboutExit = ttk.Button(self, text = "Close", command = self.aboutExit)
        self.aboutExit.grid(column = 0, row = 1, pady = 7)

    def aboutExit(self):
        self.destroy()

    def _enter(self, event):
        "changes cursor when entering link"
        self.aboutText.config(cursor = "hand2")

    def _leave(self, event):
        "changes cursor when leaving link"
        self.aboutText.config(cursor = "")
        
    def link(self, event):
        "opens browser with linked page"
        link = "http://www.gnu.org/licenses/gpl-3.0.html"
        try:
            webbrowser.open(link)
        except Exception:
            self.bell()




def main():
    testGUI = Tk()
    testGUI["menu"] = MenuCM(testGUI)
    testGUI.mainloop()


if __name__ == "__main__": main()
