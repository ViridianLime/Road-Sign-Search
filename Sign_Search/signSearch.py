#==================================================================================================
# Project: Road Sign Search
# File: SignSearch.py
# Author: Stephen Deline
# Description: The main processing class of the Road Sign Search program 
# This module takes in a provided input filename and output filename and outputs an
# image with all road signs of a given colour highlighted in green
#==================================================================================================

import sys
import os
from time import time

import numpy as np
import cv2

#=============================================================================
#Constant Global Values
#=============================================================================
cBlack = (0,0,0)
cGreen = (55,255,0)
highlightWidth = 2
blurFilterSize = 7
edgeThresh1 = 50
edgeThresh2 = 150

#=============================================================================
# Class: LocateSign
#=============================================================================
class LocateSign:

    #==========================================================================
    # Class Attributes
    #==========================================================================

    #Define range of red color in HSV 
    #(Red requires 2 ranges because it wraps around the 
    # end of the HSV colour space)
    lowRed1 = np.array([160,15,15])
    upRed1 = np.array([179,255,255])
    lowRed2 = np.array([0,15,15])
    upRed2 = np.array([10,255,255])

    #Define range of yellow color in HSV
    lowYellow = np.array([20,128,128])
    upYellow = np.array([40,255,255])

    #Define range of orange color in HSV
    lowOrange = np.array([5,100,100])
    upOrange = np.array([35,255,255])

    distTolerence = 0.04
    objSizeFloor = 0.005

    #Bool to determine if intermediary result images should be printed
    showIntRes = False

    #==========================================================================
    # Function: processImage
    #==========================================================================
    @classmethod
    def processImage(cls,inputFile,outputFile,thresholdCol):
        #Read in image and make a copy
        img, imgSize = LocateSign.readImage(inputFile)
        originalImg = img.copy()

        startTime = time()

        #Threshold the colour in the image based on the thresholdCol parameter
        img = LocateSign.threshCol(img, thresholdCol)
        #Homogenize the shapes in the image
        img = LocateSign.fillObjects(img, outputFile)

        #Remove small or non-sign shaped objects from the image
        img = LocateSign.removeSmallObjects(img, imgSize)
        img = LocateSign.removeIrregularObjects(img)

        #Overlay the locations of the sign-like objects onto the original image
        img, finalImage = LocateSign.highlightObjects(img, originalImg, outputFile)

        endTime = time()

        #Write out the new image and return the statistics
        cv2.imwrite(outputFile, finalImage)
        stats = "Time to complete: {0:.3f}s".format(endTime - startTime)

        return stats

    #==========================================================================
    # Function: readImage
    #==========================================================================
    @classmethod
    def readImage(cls,inputFile):
        #Read in and store the image using provided filename
        img = cv2.imread(inputFile)

        #Find the demensions and calculate the image size in pixels
        height, width, channels = img.shape
        imgSize = height*width

        return img, imgSize

    #==========================================================================
    # Function: threshCol
    #==========================================================================
    @classmethod
    def threshCol(cls,img,thresholdCol):
        #Threshold the colour in the image based on the thresholdCol parameter
        if thresholdCol == "Yellow":
            img = LocateSign.threshNormal(img,cls.lowYellow,cls.upYellow)
        elif thresholdCol == "Orange":
            img = LocateSign.threshNormal(img,cls.lowOrange,cls.upOrange)
        elif thresholdCol == "Red":
            img = LocateSign.threshRed(img,cls.lowRed1,cls.upRed1, cls.lowRed2,cls.upRed2)
        else:
            print("ERROR- No threshold colour selected or colour is invalid")
            exit()

        return img

    #==========================================================================
    # Function: threshNormal
    #==========================================================================
    @classmethod
    def threshNormal(cls,img,lowColour,upColour):
        # Convert BGR to HSV
        hsv = cv2.cvtColor(img , cv2.COLOR_BGR2HSV)
        # Threshold the HSV image to get only selected colors
        mask = cv2.inRange(hsv, lowColour, upColour)

        # Bitwise-AND mask and original image
        resFin = cv2.bitwise_and(img ,img , mask= mask)

        #Apply a median blur filter and convert to gray colourspace 
        resFin = cv2.medianBlur(resFin, blurFilterSize)
        resFin = cv2.cvtColor(resFin , cv2.COLOR_BGR2GRAY)

        return resFin

    #==========================================================================
    # Function: threshRed
    #==========================================================================
    @classmethod
    def threshRed(cls,img,lowColour1,upColour1,lowColour2,upColour2):
        # Convert BGR to HSV
        hsv = cv2.cvtColor(img , cv2.COLOR_BGR2HSV)
        # Threshold the HSV image to get only selected colors
        mask1 = cv2.inRange(hsv, lowColour1, upColour1)
        mask2 = cv2.inRange(hsv, lowColour2, upColour2)

        # Bitwise-AND masks and original image
        res1 = cv2.bitwise_and(img ,img, mask= mask1)
        res2 = cv2.bitwise_and(img ,img, mask= mask2)
        resFin = cv2.add(res1,res2)

        #Apply a median blur filter and convert to gray colourspace 
        resFin = cv2.medianBlur(resFin, blurFilterSize)
        resFin = cv2.cvtColor(resFin , cv2.COLOR_BGR2GRAY)

        return resFin

    #==========================================================================
    # Function: fillInObjects
    #==========================================================================
    @classmethod
    def fillObjects(cls,img,outputName):  
        #Detect all contours in the image
        edges = cv2.Canny(img, edgeThresh1, edgeThresh2, 3)
        contours,_ = cv2.findContours(edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        #Fill in image objects based on contours detected
        for cont in contours:
            cv2.drawContours(img, [cont], 0, 255, -1)

        #Threshold the greyscale image to binary(black and white)
        _,bwImage = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY)

        #Print out filled image if showIntRes is true
        if LocateSign.showIntRes == True:
            cv2.imwrite(outputName+"_fill.png", bwImage)

        return bwImage

    #==========================================================================
    # Function: removeSmallObjects
    #==========================================================================
    @classmethod
    def removeSmallObjects(cls,img,imgSize):
        contImg = img.copy()
        contours,_ = cv2.findContours(contImg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        #For each contour calculate its area
        for cont in contours:
            area = cv2.contourArea(cont)
            #If its area is less than a certain percentage of the total image area,fill it in 
            if area < (imgSize * cls.objSizeFloor):
                cv2.drawContours(img, [cont], 0, cBlack, -1)
        
        return img

    #==========================================================================
    # Function: removeIrregularObjects
    #==========================================================================
    @classmethod
    def removeIrregularObjects(cls,img):
        contImg = img.copy()
        contours,_ = cv2.findContours(contImg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        #For each shape, calculate the ratio (perimiter^2/area) and use to determine shape
        for cont in contours:
            area = cv2.contourArea(cont)
            perimeter = cv2.arcLength(cont,True)
            peri2Area = (perimeter**2) / area

            #Categorize the shape of each object based on it`s peri2Area value
            if peri2Area >= 9 and peri2Area <= 11.75:
                print ("%f - Octagon " %(peri2Area))
            elif peri2Area > 11.75 and peri2Area <= 14:
                print( "%f - Circle " %(peri2Area))
            elif peri2Area > 14 and peri2Area <= 15.77:
                print("%f - Pentagon " %(peri2Area))
            elif peri2Area > 15.77 and peri2Area <= 19.14:
                print( "%f - Rectangle " %(peri2Area))
            elif peri2Area > 19.14 and peri2Area <= 23:
                print("%f - Triangle " %(peri2Area))
            #Remove objects that are not sign-shaped by filling them with black
            else:
                print("%f - Not Sign" %peri2Area)
                cv2.drawContours(img, [cont], 0, cBlack, -1)
        return img

    #==========================================================================
    # Function: highlightObjects
    #==========================================================================
    @classmethod
    def highlightObjects(cls,img,originalImg,outputName):
        #Draw remaining objects outlines onto original image
        edges = cv2.Canny(img, edgeThresh1, edgeThresh2, 3)

        #Print out filled image if showIntRes is true
        if LocateSign.showIntRes == True:
            cv2.imwrite(outputName+"_fill---.png", edges)

        contours,_ = cv2.findContours(edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        for cont in contours:
            #Calcuate a simpler perimiter line for each contour and draw it
            maxDis = cls.distTolerence * cv2.arcLength(cont, True) 
            simplePerim = cv2.approxPolyDP(cont, maxDis, True)
            cv2.drawContours(originalImg, [simplePerim], 0, cGreen, highlightWidth)

        return img, originalImg
