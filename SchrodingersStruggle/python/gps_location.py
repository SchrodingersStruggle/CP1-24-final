"""
This module imports data from a csv file and plots gps location
onto x-y plane (x -> longitudinal, y -> latitudinal)
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#Earth radius in meters:
EARTH_R = 6371009


def gps_coordinates(csv_file):
    """
    Gathers longitude and latitude coordinates from CSV file.
    Raw data must have headers with 'Longitude (°)', and 'Latitude (°)'
    """
    if not isinstance(csv_file, str):
        raise TypeError("csv_file must be a string representing the file path.")
    try:
        open_file = pd.read_csv(csv_file)
        longitudes = open_file['Longitude (°)'].values
        latitudes = open_file['Latitude (°)'].values
    except FileNotFoundError:
        raise FileNotFoundError(f"File {csv_file} was not found.")
    except KeyError:
        raise KeyError("File must have columns with 'Longitude (°)', and 'Latitude (°)' headers.")
    return longitudes, latitudes

def convert_gps_spherical(longitudes, latitudes):
    """
    Transforms gps coordinates readings to represent the angles of a 
    standard spherical coordinate system in radians.
    """
    if not isinstance(longitudes, int, float, list):
        raise TypeError("Inputs should be in the form of int, float, or list.")
    longitudes_rad = np.deg2rad(longitudes)
    latitudes_rad = np.pi/2 - np.deg2rad(latitudes)
    return longitudes_rad, latitudes_rad

def spherical_to_cartesian(theta, phi, radius=1):
    """
    Converts a set of inputs in spherical coordinates (in radians) 
    to cartesian coordinates.
    Radius is assigned to 1 unless specified.
    """
    x = radius * np.cos(theta) * np.sin(phi)
    y = radius * np.sin(theta) * np.sin(phi)
    z = radius * np.cos(phi)
    return x, y, z

def total_distance(long_i, lat_i, long_f, lat_f):
    """
    Computes the smallest connecting arclength between two GPS positions on Earth.
    Takes into account spherical geometry of Earth.
    Equation derived by myself, with explaination in INSERT MARKDOWN FILE NAME HERE.
    """
    the_i , phi_i = convert_gps_spherical(long_i, lat_i)
    the_f , phi_f = convert_gps_spherical(long_f, lat_f)
    alpha = np.arccos(np.cos(the_i-the_f)*np.sin(phi_i)*np.sin(phi_f)+np.cos(phi_i)*np.cos(phi_f))
    dist = EARTH_R * alpha
    return dist

def remove_first_values(longitudes, latitudes, n=1):
    """
    Removes first n data points in lists of gps coordinates.
    Default n value is set to 1.
    If n is set to 0, will not remove any values.
    """
    if n != 0:
        lat_filt = []
        long_filt = []
        for i in range(n,len(longitudes)):
            long_filt.append(longitudes[i])
            lat_filt.append(latitudes[i])
    else:
        long_filt, lat_filt = longitudes, latitudes
    return long_filt, lat_filt

def adjacent_distances(data_csv, remove_first = 0, remove_outliers = False):
    """
    Computes the distances between successive measurments on a given dataset.
    -Calls upon other functions such that the only input necesary is a csv file.
    -Removes first number of values specified to what remove_first is set equal to.
        Set equal to 0 by default, to not remove any values.
    -Option to remove massive outliers which are 10X greater than the average value.
    """
    distances = []
    long_raw, lat_raw = gps_coordinates(data_csv)
    longitudes, latitudes = remove_first_values(long_raw, lat_raw, remove_first)
    for i in range(1,len(longitudes)): #Computes distances between neighboring points.
        dist = total_distance(longitudes[i-1],latitudes[i-1],longitudes[i],latitudes[i])
        distances.append(float(dist))
    avg_dist = 1/len(distances)*sum(distances) #Computes average distance between points.
    filtered_distances = [] #Empty set to put acceptable distances in
    if remove_outliers is True:
        for i in distances:  # Filters through and removes any severe outlier distances.
            if i <= 10 * avg_dist:
                filtered_distances.append(i)
            else:
                print(f"Removed {i}")
    else: filtered_distances=distances
    return filtered_distances

def convert_xy(longitudes, latitudes):
    """
    Takes input gps coordinates and converts them into a list of x-y values to plot.
    x cooresponds to East-West motion, with East being +x direction.
    y cooresponds to North-South motion, with North being +y direction.
    """
    x_values = [0]
    y_values = [0]
    theta, phi = convert_gps_spherical(longitudes, latitudes)
    for i in range(1,len(theta)):
        x_step = EARTH_R * np.sin(phi[i]) * (theta[i]-theta[i-1])
        x_values.append(x_step+x_values[i-1])
        y_step = EARTH_R * (phi[i-1]-phi[i])
        y_values.append(y_step+y_values[i-1])
    return x_values, y_values

#Example code for generating a plot:
LONGITUDE_RAW, LATITUDE_RAW = gps_coordinates('your_data_path_here.csv')
LONGITUDE, LATITUDE = remove_first_values(LONGITUDE_RAW, LATITUDE_RAW,2)
X_VALUES, Y_VALUES = convert_xy(LONGITUDE, LATITUDE)
plt.figure()
plt.plot(X_VALUES, Y_VALUES)
plt.xlabel('Longitudinal Displacement (m)')
plt.ylabel('Latitudinal Displacement (m)')
plt.xlim()
plt.ylim()
plt.title('Latitudinal vs. Longitudinal Displacement')
plt.show()
plt.savefig('save_file_path_here.png',dpi = 300)
plt.close()
