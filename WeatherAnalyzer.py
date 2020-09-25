"""
===================================================================================================

Station ID search: https://www.ncei.noaa.gov/access/search/data-search/global-summary-of-the-day
https://data.noaa.gov/onestop/
CSV data from https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/

New York:
https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/1986/74486094789.csv
https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/1987/74486094789.csv

Heathrow (3772099999)
https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/1986/3772099999.csv

===================================================================================================
"""


import os       # Required for easy Windows filepaths: https://stackoverflow.com/questions/2953834/windows-path-in-python
import pathlib
import platform
import sys

from multiprocessing import Process, Queue
from matplotlib import pyplot

CSV = r"JFK-1986.csv"

def ReadData():

    ##### Read in Data ##### 

    # Open file #

    # Get file path from user
    data_file = CSV

    print(data_file)

    # Give open command
    infile = open(data_file, 'r')

    # Read lines from file #
    idata_list = [] # List of lists 🤭

    headerCheckComplete = False

    # Loop over all lines
    for current_line in infile:

        # Get data from the string and convert to appropriate type
        # print(current_line)
        # STATION, DATE, LATITUDE, LONGITUDE, ELEVATION, NAME, TEMP, TEMP_ATTRIBUTES, DEWP, DEWP_ATTRIBUTES, SLP, SLP_ATTRIBUTES, STP, STP_ATTRIBUTES, VISIB, VISIB_ATTRIBUTES, WDSP, WDSP_ATTRIBUTES, MXSPD, GUST, MAX, MAX_ATTRIBUTES, MIN, MIN_ATTRIBUTES, PRCP, PRCP_ATTRIBUTES, SNDP, FRSHTT = current_line.split(',') # Tells Python to separate values by comma. Returns a tuple

        temp_list = [] 
        temp_list = current_line.split(',') # Tells Python to separate values by comma. Returns a tuple
        #Test: print(temp_list)


        if (headerCheckComplete == False) and (temp_list[0] == 'STATION'):
        
            # Check if the CSV format is what we expect
            #print(temp_list[20])
            #print(temp_list[22])
            #print(temp_list[24])
            print("CSV format check succeeded: continuing program")
            headerCheckComplete = True
            continue # Ends further processing of current line, thereby preventing CSV headers from being used

        #print(temp_list[21]) # MAX
        #print(temp_list[23]) # MIN
        #print(temp_list[25]) # PRECIP

        date = temp_list[1]
        high_t = float(temp_list[21])
        low_t = float(temp_list[23])

        #Convert to Celsius
        high_temp = (high_t - 32) / 1.8
        high_temp = round(high_temp, 1)

        low_temp = (low_t - 32) / 1.8
        low_temp = round(low_temp, 1)

        rainfall = float(temp_list[25])

        d, m, y = date.split('/')
        day = int(d)
        month = int(m)
        year = int(y)

        #print(day, month, year, high_temp, low_temp, rainfall) 

        # Store data in a larger list
        idata_list.append([day, month, year, high_temp, low_temp, rainfall]) # Note, we can order this however we want

    print("Data list:", idata_list)

    # Close file
    infile.close()

    # Return data_list variable
    #print(idata_list[0])
    #print(idata_list[-1])
    return idata_list


def AnalyzeData(idata_list):

    ##### Analyze Data ######

    # Get date #
    query_date = "05/05/1986" #input("Enter date to query (format: dd/mm/yyyy):")
    query_day, query_month, query_year = query_date.split('/')
    print("Query split:", query_day, query_month, query_year)

    # Loop through all historical data, checking if there are matches
    match_date = [] 
    for single_day in idata_list:
        if (query_day == single_day[0]) and (query_month == single_day[1]) and (query_year == single_day[2]):
            match_date.append(single_day[3], single_day[4], single_day[5])
    print("Match dates:", match_date)

    # Analyze historical data
    maxsofar = 0
    hottest_day = ''
    minsofar = 100
    coldest_day = ''
    sumofmax = 0
    sumofmin = 0
    rain_maxsofar = 0
    rain_sum = 0

    for single_day in idata_list:
        sumofmax += single_day[3]
        sumofmin += single_day[4]
        rain_sum += single_day[5]

        if (single_day[3] > maxsofar):
            maxsofar = single_day[3]
            hottest_day = str(single_day[0]) + "/" + str(single_day[1]) + "/" +  str(single_day[2])

        if (single_day[4] < minsofar):
            minsofar = single_day[4]
            coldest_day = str(single_day[0]) + "/" + str(single_day[1]) + "/" +  str(single_day[2])

        if (single_day[5] > rain_maxsofar):
            rain_maxsofar = single_day[5]

    # Compute averages
    count = len(idata_list)
    print("Count:", count)

    sumofmax /= count
    sumofmin /= count
    rain_sum /= count

    # Return outputs
    return maxsofar, hottest_day, minsofar, coldest_day, sumofmax, sumofmin, rain_maxsofar, rain_sum


def PresentResults(idata_list, imaxsofar, ihottest_day, iminsofar, icoldest_day, isumofmax, isumofmin, irain_maxsofar, irain_sum):

    ##### Present Results #####
    
    start_date = (str(idata_list[0][0]) + "/" + str(idata_list[0][1]) + "/" + str(idata_list[0][2]))
    end_date = (str(idata_list[-1][0]) + "/" + str(idata_list[-1][1]) + "/" + str(idata_list[-1][2]))
    print("Start date:", start_date)
    print("End date:", end_date) 

    # Maximum temperature in data range
    print("Highest temperature:", int(imaxsofar))

    # Maximum temperature date
    print(ihottest_day)

    # Minimum temperature in data range
    print("Lowest temperature:", int(iminsofar))

    # Minimum temperature date
    print(icoldest_day)

    # Average high
    print("Average daily high:", int(isumofmax))

    # Average low
    print("Average daily low:", int(isumofmin))

    # Maximum rain
    print("Highest daily rainfall:", irain_maxsofar)

    # Average rain
    print("Average daily rainfall:", round(irain_sum), 2)


def PresentGraph(idata_list):
    xlist = range(1, 366)

    ylist_high = []
    ylist_low = []

    for single_day in idata_list:
        ylist_high.append(single_day[3])
        ylist_low.append(single_day[4])
    

    pyplot.plot(xlist, ylist_high, label = "Daily High", color = "red")
    pyplot.plot(xlist, ylist_low, label = "Daily Low", color = "blue")
    pyplot.plot()
    pyplot.axis([0, 364, -15, 40])

    pyplot.legend()
    pyplot.show()

process_list = []
multi_q = Queue    # Perhaps not required, since the ReadData() order is irrelevant



"""
if __name__ == '__main__':
    p = Process(target=ReadData)
"""
    
    

data_list = ReadData()
maxsofar, hottest_day, minsofar, coldest_day, sumofmax, sumofmin, rain_maxsofar, rain_sum = AnalyzeData(data_list)
PresentResults(data_list, maxsofar, hottest_day, minsofar, coldest_day, sumofmax, sumofmin, rain_maxsofar, rain_sum)
PresentGraph(data_list)