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
import webbrowser
import os

from options import optionWrite
from window import placeWindow


class DialogBox(Toplevel):
    def __init__(self, root, title, message, dontShowOption = "", optionValue = None, html = True):
        super().__init__(root)
        
        self.root = root
        self.title(title)
        self.grab_set()
        self.focus_set()
        self.lift(root)
        placeWindow(self, 300, 150)
        self.resizable(False, False)
        self.minsize(300, 150)
        self.dontshow = dontShowOption
        self.optionValue = optionValue
        
        # message
        if html:
            message = message.replace("<br>", "\n")
        try:
            width, height = message.split("\n")[0].split("x")
            width = int(width.strip())
            height = int(height.strip())
        except Exception:
            width, height = 60, 10
        else:
            message = "\n".join(message.split("\n")[1:])
        self.text = Text(self, width = width, height = height, wrap = "word")
        self.text.grid(column = 0, row = 0, pady = 2, sticky = (N, S, E, W))
        for count, part in enumerate(message.split("\\n")):
            if count != 0:
                self.text.insert("end", "\n")
            self.text.insert("end", part)
        links = [word for word in message.split() if "www." in word]
        idx = "1.0"
        for link in links:
            idx = self.text.search(link, idx, "end")
            lastidx = "{}+{}c".format(idx, len(link))
            self.text.tag_add("link", idx, lastidx)
            idx = lastidx
        self.text.tag_configure("link", foreground = "blue")
        self.text.tag_bind("link", "<1>", lambda e: self.link(e))
        self.text.tag_bind("link", "<Enter>", lambda e: self._enter(e))
        self.text.tag_bind("link", "<Leave>", lambda e: self._leave(e))
        self.text["state"] = "disabled"
        

        # dont show again checkbutton
        if self.dontshow:
            self.dontShowVar = BooleanVar()
            self.dontShowVar.set(False)
            self.dontShowCheck = ttk.Checkbutton(self, text = "Don't show me this message again.",
                                                 variable = self.dontShowVar)
            self.dontShowCheck.grid(column = 0, row = 1, pady = 6, sticky = W, padx = 4)

        # cancel button
        self.okBut = ttk.Button(self, text = "Ok", command = self.okFun)
        self.okBut.grid(column = 0, row = 2, pady = 2)

        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight = 1)


    def _enter(self, event):
        "changes cursor when entering link"
        self.text.config(cursor = "hand2")

    def _leave(self, event):
        "changes cursor when leaving link"
        self.text.config(cursor = "")
        
    def link(self, event):
        "opens browser with linked page"
        link = self.text.get(self.text.tag_prevrange("link", "current")[0],
                             self.text.tag_prevrange("link", "current")[1])
        try:
            webbrowser.open(link)
        except Exception:
            self.bell()
                           

    def okFun(self):
        "destroys window and saves option dont show again option if selected"
        self.destroy()
        if self.dontshow and self.dontShowVar.get():
            optionWrite(self.dontshow, self.optionValue)
  
     
