#Renkforce Downloader

overview

this software (RFDownLoader) has  been created to download data from renkforce GPS loggers, specifically the GT-730 series simple loggers.

while this loggers come software to process them (canway1.1  from canmore electronics)  the BMAA competition group required a software app to download this loggers quickly and process the data into IGC format files named in away that existing competition software can process them without any manual post processing.

the software has been created to be very lightweight and follow the look and feel of the existing software (FRDL) currently used to download the down deprecated AMOD loggers.

documentation

there  is a video showing operation of v2.1 of the app   https://youtu.be/fbyE8wkoz-s 

platforms

the software is python,  specifically py3.8, it current will run native on linux or windows having been tested on windows11 and linux Mint 22.1. 

pre-req Py imports outside the standard pack

PIL,pyserial,matplotlib.binascii,tkinter

Binary

currently there is a windows10/11 binary file provided, that allows operation without a python environment. other platforms will be added.

flat files

championships.csv - required to define a list of competitions or events.  this is used to seperate data into output directories

pilots.csv - required to create the list of pilots and their comp numbers. this is required to follow the existing naming standard for files

tasks.csv -  simple list of task number, used to populate the drop down for the task. this again is required to follow the existing naming standard.
