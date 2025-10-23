#!/usr/bin/env python3


#######################################################################################################
# this scripts runs a tk.gui to all the user to download renkforce loggers and create from it
# an igc file in the format created by frdl so it would work with pesto and the circler 
#
# updated to fix/include the padding for lon mins in the parser.
# v1.4  updated to use 2019 gps epoch to fix the missing leap seconds, and auto guess the com port (on windows)
#######################################################################################################

# Import the tk.module 
import tkinter as tk
from tkinter import ttk
import subprocess,os,sys
import renkforce_parse
from PIL import ImageTk, Image
from datetime import date
import datetime
from serial.tools.list_ports import comports
import csv
global Plot
Plot = False

sys.stdout = open('debug.log' ,'w')

############################################################
# get the comand line args

if len(sys.argv) > 1:
   param1 = sys.argv[1] 
   print (param1)
   if param1 == "P":
       Plot = True
       import plot_igc
       print (Plot)


print ("app startup :" , datetime.datetime.now())

# init some vars we might need 
global messageStr
messageStr = "" 
champ_list = []
task_list = []
pilot_list = []
time_list = ["07:00","07:30","08:00","08:30","09:00","09:30","10:00","10:30","11:00","11:30","12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","20:00","20:30","21:00","21:30","22:00","22:30","23:00"]

champFile = "championships.csv"
taskFile = "tasks.csv"
pilotFile = "pilots.csv"
portNo = "com8"
global pilotNamesDict
pilotNamesDict = {}
champNamesDict = {}
igcfiles = "igcfiles"  # where the files end up
linefeed = '\n'  #  \n for linux  \r\n for windows
global timeToStartShort
global menu1_selection_dir


#########################################################
# open and populate the championship list
#########################################s################

try:
    OpenChampfile = open(champFile, "r", encoding='ascii', errors='replace')
except FileNotFoundError:
    print (champFile, " needs to be in the same dir as the exe")
    quit()

for line2 in OpenChampfile.read().splitlines():
    ChampNameIn = line2.split(",")[0]
    champ_list.append(ChampNameIn)

#############################################################################
# function to allow the logo to be included in a onefile bin
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
###############################################################################
# Function to populate menu2 based on tasks.csv in the champ subdirectory
def update_menu2_tasks(event):
    global menu1_selection_dir
    menu1_selection_dir = value_champName.get().replace(" ","_").lower()
    try:
        # Construct the file path: subdirectory/menu1_selection_dir/tasks.csv
        file_path = os.path.join(menu1_selection_dir, "tasks.csv")

        # Read the contents of the CSV file (first column only)
        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            menu2_options = [row[0] for row in reader if row]  # Read first column

        # Update menu2 dropdown
        menu2_var.set("1")  # Reset menu2 value
        menu2_dropdown["values"] = menu2_options
    except FileNotFoundError:
        menu2_var.set("")
        menu2_dropdown["values"] = []  # Clear menu2 options
        print(f"File {file_path} not found.")

#######################################################################
# Function to populate menu3 based on pilots.csv in the subdirectory
def update_menu3_pilots(event):
    global pilotNamesDict  # Access the global dictionary
    global menu1_selection_dir
    menu1_selection_dir = value_champName.get().replace(" ","_").lower()
    pilotNamesDict = {}

    try:
        # Construct the file path: subdirectory/menu1_selection/pilots.csv
        file_path = os.path.join(menu1_selection_dir, "pilots.csv")

        # Read the contents of the CSV file and populate the dictionary
        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if len(row) >= 2:  # Ensure there are at least two columns
                    pilotNamesDict[row[0]] = row[1]  # Column 0 as key, Column 1 as value
        # Update menu3 dropdown with keys from the dictionary
        menu3_var.set("0")  # Reset menu3 value
        #menu3_dropdown["values"] = list(pilotNamesDict.keys())
        menu3_dropdown["values"] = [f"{key} - {value[0:15]}" for key, value in pilotNamesDict.items()]
    except FileNotFoundError:
        menu3_var.set("")
        menu3_dropdown["values"] = []  # Clear menu3 options
        messageToWrite =  f"File {file_path} not found."
        resultsM = event_write(messageToWrite) 
        print(f"File {file_path} not found.")

# Bind the event once to the combined function for menu updates
def update_menus(event):                                                                        
    update_menu2_tasks(event)                                                                         
    update_menu3_pilots(event)

#########################################################
### get com port
def get_ComPort():
    portNo = "xx"
    for port in comports():
        if "STM32" in str(port):  # test for linux com port
            portNo = str(port)[:12]
        if "STMicroelectronics" in str(port):   # test for windows com port
            portNo = str(port)[:5]
    if portNo == "xx":
        portNo = "No port"
        messageToWrite = "no port found" 
        resultsM = event_write(messageToWrite) 
    else:
        messageToWrite = portNo + " found" 
        resultsM = event_write(messageToWrite) 
    value_port.set(portNo)
    print (portNo + " found")

    return portNo

#########################################################
###  do all the actuall downlaod stuff


def renkforce_clear():
    from skytraq.venus6 import Venus6
    port = get_ComPort()
    #port = "com8"
    serial_speed = None # 9600

    #gps = Venus6('/dev/ttyACM0', serial_speed, debug=False)
    gps = Venus6(port, serial_speed, debug=False)

    if serial_speed == None:
      # try to guess serial speed
      serial_speed = gps.guessSerialSpeed()

    clear_status = gps.clearLogs()

    print (" logger cleared")
    messageToWrite = "GPS logs cleared "
    resultsM = event_write(messageToWrite)



######################################################################
# this routine downloads the binary stream, sector by sector and saves it
# into a bin file for later processing.  there are 510 possible sectors 
def renkforce_download(port,raw_fil):
    global pilotNo
    import binascii
    from skytraq.venus6 import Venus6

    serial_speed = None # 9600

    #gps = Venus6('/dev/ttyACM0', serial_speed, debug=False)
    gps = Venus6(port, serial_speed, debug=False)

    if serial_speed == None:
      # try to guess serial speed
      serial_speed = gps.guessSerialSpeed()


    messageToWrite = pilotNo + " GPS connected, download starting"
    resultsM = event_write(messageToWrite)

    #print("====    getting log status    =====")
    (log_wr_ptr, sector_left, total_sector,
          min_time, max_time,
          min_distance, max_distance,
          min_speed, max_speed,
          data_log_enable, log_fifo_mode) = gps.getLogStatus()
    #print("> log_wr_ptr: 0x%X" % log_wr_ptr)

    if serial_speed != 115200:
      gps.setSerialSpeed(115200)

    entries = []
    with open(raw_fil, 'wb') as raw:
      for s in range(total_sector - sector_left + 1):
        if str(s)[-1]  == "0" :
            print("reading sector %d" % s)
        data = gps.readLog(s, 1)
        raw.write(data)

    print("Saved data to " ,raw_fil)

    # restore serial speed
    if serial_speed != 115200:
      gps.setSerialSpeed(serial_speed)

    # gps.clearLogs()
    return (total_sector - sector_left) 


### log to the event window
def event_write(messageToAdd):
    global messageStr
    print (messageToAdd)
    length = len(messageStr)
    if length >= 620:
        messageStr = messageStr[100:]
    messageStr = messageStr + messageToAdd + "\n"
    fred.set(messageStr)
    root.update()
    return 

### this runs as soon as we hit the download button
def start_download(): 
    global messageStr
    global timeToStart
    global timeToEnd
    global DateToStart
    global pilotNo
    global taskNo
    global port
    global menu1_selection_dir

    print ("downloading startup :" , datetime.datetime.now())

    try:
        menu1_selection_dir
    except NameError:    
         messageToWrite = "Comp not set"
         resultsM = event_write(messageToWrite)
         return None

    actualChampDir = menu1_selection_dir 
    sectors = 0
    DateToStart = format(value_taskDate.get())
    timeToStart = format(value_taskHH.get()).replace(":", "")
    timeToEnd = format(value_taskEE.get()).replace(":", "")
    taskNo = format(menu2_var.get()).zfill(2)
    pilotNo = format(menu3_var.get())[:3]  # clip the first 3 off the returned value
    print("taskNo/pilotNo: ",taskNo," ", pilotNo) 
    port = format(value_port.get())
    if pilotNo == '0':
         messageToWrite = "invalid pilotNo"
         resultsM = event_write(messageToWrite)
         return None
    print (DateToStart)

    if port == "No port":
         messageToWrite = "invalid port! , connect GPS and hit GET PORT"
         resultsM = event_write(messageToWrite)
         return None

    ######## call to get raw bin data from gps 
    sectors = renkforce_download(port,"renkforce_raw1.bin")

    if sectors == 0 :   #### log something
         messageToWrite = "FAILED to download " 
         resultsM = event_write(messageToWrite) 
    else:
        messageToWrite = pilotNo + " raw data downloaded " + str(sectors) + " sectors" 
        resultsM = event_write(messageToWrite) 
        ######## call to turn the raw binary data into igc data 
        returnCode = createBigIGC("renkforce_raw1.bin",taskNo,pilotNo,actualChampDir)
        
    return None


#### this routine takes the binary file from extract, and then turns it into a igc 
#    type file that can be chopped up for the correct time
def createBigIGC(raw_bin,taskNo,pilotNo,champDIR):
    print ("converting to big igc")
    #PilotDir = str(champDIR) + "\\" + str(pilotNo)
    PilotDir = str(champDIR) + os.sep + str(pilotNo)
    PilotName = pilotNamesDict.get(pilotNo) 
    if os.path.isdir(PilotDir) == False:
        os.mkdir(PilotDir)

    
    bigIGCfile = PilotDir + os.sep + pilotNo + "T" + taskNo + "big" + "_" + PilotName + ".igc"   
    lastDateStamp,counter = renkforce_parse.bin2igc_converter(raw_bin,bigIGCfile)

    if counter == 0 :   #### log something
         messageToWrite = "FAILED to convert " 
         resultsM = event_write(messageToWrite) 
    else:
        messageToWrite = pilotNo + " Big IGC created, last stamp:" + lastDateStamp + " " + str(counter) + " rows" 
        resultsM = event_write(messageToWrite) 

    igcfileDir = champDIR + os.sep + igcfiles
    if os.path.isdir(igcfileDir) == False:
        os.mkdir(igcfileDir)

    #######  lets turn the igc file into something we can score, this
    ###      this includes selected the date and time we need

    DateToStartShort = DateToStart[0:10]
    print ("looking for " , DateToStartShort , " ", timeToStart, " end ", timeToEnd)
    
    bigIGC = open(bigIGCfile, "r", encoding='ascii', errors='replace')
    igcFileName = igcfileDir + os.sep + pilotNo + "T" + taskNo + "V1R1" + "_" + PilotName + ".igc"
    pilotIGC = open(igcFileName, "w")
    counter = 0
    pilotIGC.write("AXXXXXXAM-renkforce GT370" + linefeed)
    YY = DateToStartShort[2:4]
    MM = DateToStartShort[5:7]
    DD = DateToStartShort[8:10]
    HSDate = DD + MM + YY
    pilotIGC.write("HSDTE" + HSDate + linefeed) #added to follow the format of FRDL files
    pilotIGC.write("HFDTE" + HSDate + linefeed) # and for the rest of the world
    pilotIGC.write("HFGPS:skytraq venus6" + linefeed)
    pilotIGC.write("HSPLTPILOT:" + PilotName + linefeed)
    pilotIGC.write("HSFTYFRTYPE:Renkforce,GT730" + linefeed)
    pilotIGC.write("HSCIDCOMPETITIONID:" + pilotNo + linefeed)
    pilotIGC.write("LCMASTSKTASKNUMBER:" + taskNo + linefeed)
    pilotIGC.write("LCMASTSNDATATRANSFERSOFTWARENAME:RFdownloader 2.1" + linefeed)
    timeLatch = 0
    for bigLine in bigIGC.read().splitlines():
        if bigLine[0:10] == DateToStartShort:
            if float(bigLine[12:16]) >= float(timeToStart) and timeLatch == 0:
                print ("first time stamp found " + bigLine[12:16])
                timeLatch = "1"
            if float(bigLine[12:16]) <= float(timeToEnd) and timeLatch == "1": 
                pilotIGC.write(bigLine[11:] + "\n")
                counter = counter + 1


    if counter == 0 :   #### log something
         messageToWrite = "FAILED to find date and time requested " 
         resultsM = event_write(messageToWrite) 
    else:
        messageToWrite = igcFileName + " IGC created "  + str(counter) + " rows" 
        resultsM = event_write(messageToWrite) 
    pilotIGC.close()
    ######################################################
    #plotter engine
    global Plot
    if Plot:
        print ("plot is-",Plot," creating plot")
        import plot_igc
        plot_igc.main(igcFileName)
    return 


def     Quit():
    root.quit()
###################################################
# set the plot button status, 
def     set_plot():
   global Plot
   if value_plotter.get() == 1:
       Plot = True
       print ("plot requested", Plot)
   if value_plotter.get() == 0:
       Plot = False
       print ("plot requested", Plot)

###################################################
# create the gui stuff
###################################################
    

# Create the default window  , root

root = tk.Tk() 
root.title("RenkForce GPS reader") 
root.geometry('750x600') 

root.columnconfigure((0,1,2,3), weight = 1)
root.rowconfigure((0,1,2), weight = 2, uniform="row")
root.rowconfigure((3,4,5,6,7), weight = 3, uniform="row")
root.rowconfigure((8), weight = 1, uniform="row")
  
value_plotter = tk.IntVar(root)
  
l0 = tk.Label(root,  text='Comp', width=15 )  
l0.grid(row=0,column=0,sticky="s")
l1 = tk.Label(root,  text='Task', width=15 )  
l1.grid(row=2,column=0,sticky="s")
l2 = tk.Label(root,  text='Pilot No', width=15 )  
l2.grid(row=3,column=0)
l2x = tk.Checkbutton(root,  text='create plot', variable = value_plotter, onvalue=1, offvalue=0, command=set_plot, width=15 )  
l2x.grid(row=4,column=3,sticky="s")
l3 = tk.Label(root,  text='Start Date', width=15 )  
l3.grid(row=2,column=2,sticky='se')
l4 = tk.Label(root,  text='      YYYY-MM-DD', width=15 )  
l4.grid(row=3,column=3,sticky='nw')
l5 = tk.Label(root,  text='Start Hour', width=15 )  
l5.grid(row=3,column=2,sticky="e")
l5x = tk.Label(root,  text='End Hour', width=15 )  
l5x.grid(row=3,column=2,sticky="se")
l6 = tk.Label(root,  text='Port', width=15 )  
l6.grid(row=4,column=0)

# Variable to keep track of the option 
# selected in OptionMenu 
value_pilotNo = tk.StringVar(root) 
value_champName = tk.StringVar(root) 
value_taskNo = tk.StringVar(root) 
value_taskDate = tk.StringVar(root) 
value_taskHH = tk.StringVar(root) 
value_taskEE = tk.StringVar(root)  # task end time
value_port = tk.StringVar(root) 
status_label = tk.StringVar(root) 
fred = tk.StringVar(root) 
menu2_var = tk.StringVar(root)                                                                  
menu3_var = tk.StringVar(root)
  
# Set the default value of the variable 
value_champName.set("Not set") 
value_pilotNo.set(000) 
menu3_var.set(000) 
menu2_var.set(1) 
value_taskNo.set(1) 
value_taskHH.set("09:00") 
value_taskEE.set("21:00") 
value_port.set("com0") 
value_port.set(get_ComPort()) 
value_taskDate.set(date.today()) 
  
# Create the optionmenu widget and passing  
# the options_list and value_inside to it. 

#question_menu3 = tk.OptionMenu(root, value_champName, *champ_list) 
menu1_dropdown = ttk.Combobox(root, textvariable=value_champName, values=champ_list)
menu1_dropdown.grid(row=0,column=1,sticky="s")

menu1_dropdown.bind("<<ComboboxSelected>>", update_menus)

#question_menu1 = tk.OptionMenu(root, value_taskNo, *task_list) 
menu2_dropdown = ttk.Combobox(root, textvariable=menu2_var)
menu2_dropdown.grid(row=2,column=1,sticky="s")

enterDateOpt = tk.Entry(root, textvariable = value_taskDate) 
enterDateOpt.grid(row=2,column=3,sticky="s")

enterTimeHH = tk.OptionMenu(root, value_taskHH, *time_list) 
enterTimeHH.grid(row=3,column=3)

enterTimeEE = tk.OptionMenu(root, value_taskEE, *time_list) 
enterTimeEE.grid(row=3,column=3,sticky="s")

enterPort = tk.Entry(root, textvariable = value_port) 
enterPort.grid(row=4,column=1)

#question_menu = tk.OptionMenu(root, value_pilotNo, *pilot_list) 
menu3_dropdown = ttk.Combobox(root, textvariable=menu3_var)
menu3_dropdown.grid(row=3,column=1)

# port updater button 
submit_button = tk.Button(root, text='get Port', command=get_ComPort) 
submit_button.grid(row=4,column=3)

# Download button 
submit_button = tk.Button(root, text='Download', command=start_download) 
submit_button.grid(row=5,column=3)
#  earse
submit_button = tk.Button(root, text='Erase', command=renkforce_clear) 
submit_button.grid(row=6,column=3,sticky="s")
# End button 
end_button = tk.Button(root, text='EXIT', command=Quit) 
end_button.grid(row=7,column=3,sticky="s")
  
###
status_label = tk.Label(root, textvariable=fred,background='white', borderwidth=2, relief='solid',anchor="nw",width=25,height=16,justify="left")
status_label.grid(row=5,column=0,rowspan=3,columnspan=3,sticky='nsew')
####  logo
logo_image = ImageTk.PhotoImage(Image.open(resource_path("GPS-logo.png")).resize((100,55)))
#logo_image = ImageTk.PhotoImage(Image.open("GPS-logo.png").resize((100,55)))
image_label = tk.Label(root, image = logo_image)
image_label.grid(row=1,column=3,sticky="nw")

l6 = tk.Label(root,  text='RFdownloader v2.2')  
l6.grid(row=8,column=3,sticky="se")


root.mainloop() 

