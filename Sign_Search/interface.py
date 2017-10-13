#==================================================================================================
# Project: Road Sign Search
# File: Interface.py
# Author: Stephen Deline
# Description: The graphical display component of the Road Sign Search program
#==================================================================================================

from Tkinter import *
import tkMessageBox
import Tkinter
import Tkconstants
import tkFileDialog

from signSearch import LocateSign

#=============================================================================
# Class: SelectDialog
#=============================================================================
class SelectDialog:

    #=============================================================================
    # Function: SelectDialog Construtor
    #=============================================================================
    def __init__(self):
        #Define Window properties and add all elements
        self.defineBaseProperties()
        self.createLayout()
        self.createInputSelect()
        self.createOutputSelect() 
        self.createColourSelect()
        self.createProcessButton()
        
        #Start interface event loop
        self.root.mainloop()

    #=============================================================================
    # Function: defineBaseProperties
    #=============================================================================    
    def defineBaseProperties(self):
        self.inputFileName = ""
        self.outputFileName = ""
        self.threshCol = "red"

        self.root = Tk()
        self.root.title("Road Sign Program")
        self.root.geometry('650x400')

    #=============================================================================
    # Function: createLayout
    #=============================================================================
    def createLayout(self):
        #Center Frame
        self.centerFrame = Frame(self.root)
        self.centerFrame.grid(row=0, column=0)

        #Right Frame
        self.rightFrame = Frame(self.root)
        self.rightFrame.grid(row=0, column=1)

    #=============================================================================
    # Function: createInputSelect
    #=============================================================================
    def createInputSelect(self):
        #Label for Input File
        self.selectInputLabel = Label(self.centerFrame,
        text="Select Input Filename")
        self.selectInputLabel.grid(row=0, column=0)
        #Button for Input File
        self.selectInputButton = Button(self.centerFrame,text="...",fg="black",command=self.chooseFile)
        self.selectInputButton.grid(row=0,column=1)
        #Blank Space
        self.space1Label = Label(self.centerFrame,text="")
        self.space1Label.grid(row=1, column=0)

    #=============================================================================
    # Function: createOutputSelect
    #=============================================================================
    def createOutputSelect(self):
        #Label for Output File
        self.selectOutputLabel = Label(self.centerFrame,
        text="Select Output Filename")
        self.selectOutputLabel.grid(row=2, column=0)
        #Button for Output File
        self.selectOutputButton = Button(self.centerFrame,text="...",fg="black", command=self.chooseOutput, state=DISABLED)
        self.selectOutputButton.grid(row=2,column=1)
        #Blank Space
        self.space2Label = Label(self.centerFrame,text="")
        self.space2Label.grid(row=3, column=0)

    #=============================================================================
    # Function: createColourSelect
    #=============================================================================
    def createColourSelect(self):
        #Colour List Label
        self.selectColourLabel = Label( self.rightFrame,
        text = "Select a colour to search for:")
        self.selectColourLabel.grid(row=0, column=0)
        
        #Colour List
        self.colourList = Listbox(self.rightFrame, height=3)
        self.colourList.grid(row=1, column=0)
        self.colourList.insert(1, "Red")
        self.colourList.insert(2, "Yellow")
        self.colourList.insert(3, "Orange")

    #=============================================================================
    # Function: createProcessButton
    #=============================================================================
    def createProcessButton(self):
        #Button for processing the image
        self.processButton = Button(self.rightFrame,
            text="Process Image",fg="black", 
            command=self.processImage, state=DISABLED)
        self.processButton.grid(row=2, column=0)

    #=============================================================================
    # Function: chooseFile
    #=============================================================================        
    def chooseFile(self):
        self.inputFileName = tkFileDialog.askopenfilename(
            filetypes=[("JPG Files","*.jpg")])

        #Update Input file label and activate output select button
        if self.inputFileName != "":
            self.selectInputLabel.config(text=self.inputFileName)
            self.selectOutputButton.config(state=NORMAL)

    #=============================================================================
    # Function: chooseOutput
    #=============================================================================
    def chooseOutput(self): 
        #Cut off the name of the file from the filepath
        nameList =  self.inputFileName.split("/")
        fileName = nameList[len(nameList)-1]
        print (fileName)

        #Replace file extension for output file
        self.outputFileName = fileName.split('.')[0]
        self.outputFileName += "_out.png"

        #Retrive output filepath
        self.outputFileName = tkFileDialog.asksaveasfilename(
            filetypes=[("PNG Files","*.png")], initialfile=self.outputFileName,
            confirmoverwrite=True)

        #Update Output file label and activate process image button
        if self.outputFileName != "":
            self.selectOutputLabel.config(text=self.outputFileName)
            self.colourList.selection_set( first = 0 )
            self.processButton.config(state=NORMAL)

    #=============================================================================
    # Function: processImage
    #=============================================================================
    def processImage(self):
        #Retrive the threshold colour from the list selection
        pos = self.colourList.curselection()[0]
        self.threshCol = self.colourList.get(pos)

        if self.inputFileName == "":
            print("ERROR:No input file selected") 
        if self.outputFileName == "":
            print("ERROR:No output file selected") 
        if self.threshCol == "":
            print("ERROR:No threshold colour selected")
        if (self.inputFileName == "" 
        or self.outputFileName == ""
        or self.threshCol == ""):
            exit()

        print(self.inputFileName)
        print(self.outputFileName)     
        stats = LocateSign.processImage(self.inputFileName,self.outputFileName, self.threshCol)
        print(stats)
        tkMessageBox.showinfo("Complete", stats)

        #Reset inputs, labels and buttons
        self.outputFileName = ""
        self.inputFileName = ""
        self.threshCol = ""
        self.selectOutputLabel.config(text="Select Output Filename")
        self.selectInputLabel.config(text="Select Input Filename")
        self.selectOutputButton.config(state=DISABLED)
        self.processButton.config(state=DISABLED)