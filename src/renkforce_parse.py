#!/usr/bin/env python3
# -*- coding: utf8 -*-
##################################################################################
# this routine takes the downloaded binary file and converts the position data
# into igc format B records
# updated 17 mar 25 to fix pad to 5chrs for lon minutes

##################################################################################

def bin2igc_converter(rawfil,stagingfile,extend):
    #  rawfil is bin,  stagingfile is bigIGCfile,  extend is Y/N for extra info (GSP) 
    #import binascii
    from skytraq.venus6 import Venus6
    from datetime import timedelta, datetime
    #import sys
    rowcounter = 0
    outfil = open(stagingfile, "w")
    print (extend)

    with open(rawfil, 'rb') as raw:
        data = raw.read()
        entries = Venus6.decodeLog(data)
        #print (entries)
        for (date, lat, lon, alt, speed) in entries:
             #print (date, lat, lon, alt, speed)
             lat_igc, lon_igc = decimal_to_igc(lat, lon)
             dt = str(date)  # as this is still in datetime.datetime format
             time = dt[11:19].replace(":","")
             date = dt[0:10]
             altitude = "A00000" + str(int(round(alt))).zfill(5)
             extension = "0001" + str(speed).zfill(3)   # add FXA and GSP to B records
             #print (date,time,lat_igc, lon_igc,altitude,extension)
             if extend == True:
                 Brecord = date + ",B"  + time + lat_igc + lon_igc + altitude + extension + "\n"
             else:
                 Brecord = date + ",B"  + time + lat_igc + lon_igc + altitude + "\n" 
             rowcounter = rowcounter + 1
             outfil.write(Brecord)
             print (Brecord)
    outfil.close()
    return dt,rowcounter 

######routine to turn dec coords to igc B format
def decimal_to_igc(lat_decimal, lon_decimal):
    # Convert latitude
    lat_deg = int(abs(lat_decimal))
    lat_min = (abs(lat_decimal) - lat_deg) * 60
    lat_min_str = f"{lat_min:06.3f}".replace(".", "")
    lat_direction = 'N' if lat_decimal >= 0 else 'S'
    
    # Convert longitude
    lon_deg = int(abs(lon_decimal))
    lon_min = (abs(lon_decimal) - lon_deg) * 60
    lon_min_str = f"{lon_min:06.3f}".replace(".", "")  # updated to 6.3f
    lon_direction = 'E' if lon_decimal >= 0 else 'W'
    
    # Format latitude and longitude in IGC format
    lat_igc = f"{lat_deg:02d}{lat_min_str}{lat_direction}"
    lon_igc = f"{lon_deg:03d}{lon_min_str}{lon_direction}"

    return lat_igc, lon_igc








