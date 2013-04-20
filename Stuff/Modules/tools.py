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

from tkinter.filedialog import askopenfilename, asksaveasfilename
from optionget import optionGet
import pickle
import os
import os.path


def saveFileStorage(root):
    "saves picled fileStorage"
    initialdir = optionGet("SelectedFilesDirectory", os.path.join(os.getcwd(), "Stuff",
                                                                  "Selected files"), "str")
    file = asksaveasfilename(filetypes = [("Filestorage", "*.files")], initialdir = initialdir)
    if file:
        if os.path.splitext(file)[1] != ".files":
            file = file + ".files"
        with open(file, mode = "wb") as infile:
            pickle.dump(root.selectFunction.fileStorage, infile)


def loadFileStorage(root):
    "loads pickled fileStorage"
    initialdir = optionGet("SelectedFilesDirectory", os.path.join(os.getcwd(), "Stuff",
                                                                  "Selected files"), "str")
    file = askopenfilename(filetypes = [("Filestorage", "*.files")], initialdir = initialdir)
    if file:
        with open(file, mode = "rb") as infile:
            root.selectFunction.fileStorage.__dict__ = pickle.load(infile).__dict__
        root.checkProcessing(None)
