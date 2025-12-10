#!/usr/bin/env python3
##########################################
#
# this script is called from the rfloader, it created a plot window showing where the saved track went etc
#
# Force matplotlib to use an TK backend, as there are compat issues on macOS
import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import math
import sys

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the Haversine distance between two points on Earth (in decimal degrees).
    
    Returns:
      The distance in miles.
    """
    R = 3958.8  # Radius of the Earth in miles
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def parse_igc(filename):
    """
    Reads an IGC file and extracts:
      - latitudes and longitudes from B records,
      - header information (HSPLTPILOT and HSCIDCOMPETITIONID) for the plot title,
      - and the flight start time from the first B record.
    
    B record format (fixed-width):
      Character 1: 'B'
      Characters 2-7: Time in HHMMSS format.
      Characters 8-14: Latitude in DDMMmmm format.
      Character 15: Latitude hemisphere ('N' or 'S').
      Characters 16-24: Longitude in DDDMMmmm format.
      Character 25: Longitude hemisphere ('E' or 'W').
    
    Returns:
      latitudes: List of decimal degree latitudes.
      longitudes: List of decimal degree longitudes.
      title_str: Combined header string.
      formatted_time: Flight start time formatted as HH:MM:SS.
    """
    latitudes = []
    longitudes = []
    pilot = None
    comp_id = None
    start_time = None

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Extract header records for the plot title.
            if line.startswith("HSPLTPILOT"):
                if ":" in line:
                    pilot = line.split(":", 1)[1].strip()
                else:
                    pilot = line[len("HSPLTPILOT"):].strip()
            elif line.startswith("HSCIDCOMPETITIONID"):
                if ":" in line:
                    comp_id = line.split(":", 1)[1].strip()
                else:
                    comp_id = line[len("HSCIDCOMPETITIONID"):].strip()
            # Process B records.
            elif line.startswith('B') and len(line) >= 25:
                time_str = line[1:7]  # HHMMSS
                if start_time is None:
                    start_time = time_str  # Record first B record time.
                try:
                    # Process latitude (DDMMmmm and hemisphere).
                    lat_str = line[7:14]
                    lat_hem = line[14]
                    degrees_lat = int(lat_str[0:2])
                    minutes_lat = float(lat_str[2:]) / 1000.0
                    lat = degrees_lat + (minutes_lat / 60.0)
                    if lat_hem == 'S':
                        lat = -lat

                    # Process longitude (DDDMMmmm and hemisphere).
                    lon_str = line[15:23]
                    lon_hem = line[23]
                    degrees_lon = int(lon_str[0:3])
                    minutes_lon = float(lon_str[3:]) / 1000.0
                    lon = degrees_lon + (minutes_lon / 60.0)
                    if lon_hem == 'W':
                        lon = -lon

                    latitudes.append(lat)
                    longitudes.append(lon)
                except Exception as e:
                    print("Error parsing line:", line, "Error:", e)

    # Create the title string using header records.
    title_str = ""
    if pilot:
        title_str += pilot
    if comp_id:
        if title_str:
            title_str += " " + comp_id
        else:
            title_str = comp_id
    if not title_str:
        title_str = "Gliding Flight Path"

    formatted_time = ""
    if start_time and len(start_time) == 6:
        formatted_time = f"{start_time[0:2]}:{start_time[2:4]}:{start_time[4:6]}"

    return latitudes, longitudes, title_str, formatted_time

def set_window_position_top_right():
    """
    Sets the matplotlib plot window to a fixed size of 750x600 pixels and positions it
    to the top right-hand side of the screen.
    """
    try:
        # Set fixed dimensions for the plot window.
        fixed_width_px = 750
        fixed_height_px = 600

        # Use Tkinter to get screen dimensions.
        import tkinter as tk
        tk_root = tk.Tk()
        tk_root.withdraw()  # Hide the main window.
        screen_width = tk_root.winfo_screenwidth()
        tk_root.destroy()

        # Compute x position for top right (x offset = screen width - fixed width; y = 0 for top).
        x = screen_width - fixed_width_px
        y = 0

        # Apply geometry to the plot window.
        manager = plt.get_current_fig_manager()
        if hasattr(manager.window, 'wm_geometry'):
            # Format: "widthxheight+x+y"
            geometry_str = f"{fixed_width_px}x{fixed_height_px}+{x}+{y}"
            manager.window.wm_geometry(geometry_str)
            manager.window.wm_title("RFdownloader - plotter")
        elif hasattr(manager.window, 'resize'):
            # For Qt backends.
            manager.window.resize(fixed_width_px, fixed_height_px)
        elif hasattr(manager.window, 'move'):
            # For other backends.
            manager.window.move(x, y)
        else:
            print("No method available to set window geometry on this backend.")
    except Exception as e:
        print("Error setting window position:", e)


def main(filename):
    """
    Main function to parse the IGC file, compute total distance using the Haversine formula,
    and plot the flight track. A red dot marks the first point, and a legend displays the
    start time along with the total distance (in miles). The window is then repositioned
    to the top right-hand side of the screen.
    """
    latitudes, longitudes, title, start_time = parse_igc(filename)
    if not latitudes or not longitudes:
        print("No valid B records found in the file!")
        return

    # Calculate total track distance.
    total_distance = 0.0
    for i in range(1, len(latitudes)):
        total_distance += haversine_distance(latitudes[i-1], longitudes[i-1], latitudes[i], longitudes[i])

    plt.figure(figsize=(10, 6))
    # Plot the flight path.
    plt.plot(longitudes, latitudes, marker='o', markersize=2, linestyle='-', color='blue', label='Flight Track')
    # Mark the first point with a red dot.
    plt.plot(longitudes[0], latitudes[0], marker='o', markersize=6, color='red',
             label=f'Start: {start_time} | Distance: {total_distance:.1f} miles')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title(title)
    plt.grid(True)
    plt.legend(loc='best')

    # Reposition the window to the top right-hand side of the screen.
    set_window_position_top_right()

    plt.show()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 plot_igc.py <igc_file>")
        sys.exit(1)
    main(sys.argv[1])

