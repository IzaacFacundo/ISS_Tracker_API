#!/usr/bin/env python

import math
import xmltodict
import requests
from flask import Flask
from flask import request
from geopy.geocoders import Nominatim
import time

app = Flask(__name__)

r = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
all_data = xmltodict.parse(r.content)
state_vector_data = all_data['ndm']['oem']['body']['segment']['data']['stateVector']
MEAN_EARTH_RADIUS = 6371 # in km

def convert_j2k_to_geoposition(state_vector_dict:dict):
    '''
    This function takes state position in the J2000 frame and turns it into latitude, longitude, 
    and altitude.

    Args:
        state_vector_dict (dict) : a dictionary containing the state vector (position and velocity components) in units km and km/s in the J2000 frame
    Returns:
        geodata (dict) : a dictionary containing the latitude, longitude, and altitude of the spacecraft
    '''
    try:
        x = state_vector_dict['X']
        y = state_vector_dict['Y']
        z = state_vector_dict['Z']
        epoch = state_vector_dict['EPOCH']
    except:
        return("Invalid Epoch")


    hrs = int(epoch[9:11])
    mins = int(epoch[12:14])

    lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))                
    lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 24
    alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS
    altitude = {"value" : alt, "units": "km"}
    geodata = {"latitude" : lat, "longitude" : lon, "altitude" : altitude} 

    return(geodata)

@app.route('/',methods=['GET'])
def get_all_data() -> dict:
    '''
    This function returns to the user a dictionary of the entire .xml file given by the ISS website.

    Args: NONE
    Returns:
        all_data (dict) : .xml from ISS website in dictionary form
    '''
    if not all_data:
        return "Error: ISS Data has been deleted. Use route '/post-data' to restore data.\n"

    return all_data

@app.route('/epochs',methods=['GET'])
def get_list_of_epochs() -> dict:
    '''
    This function returns a list of all epochs (times) that are contained within the ISS tracker .xml file

    Args: NONE
    Returns:
        json_list_of_epochs (dict) : list of strings containing each epoch
    '''
    if not all_data:
        return "Error: ISS Data has been deleted. Use route '/post-data' to restore data.\n"
    
    limit = request.args.get('limit',len(state_vector_data))
    try:
        limit = int(request.args.get('limit',len(state_vector_data)))
    except ValueError:
        return("Invalid limit parameter; limit must be an integer.\n", 400)
    if limit < 0:
        return("Error: limit must be a positive integer.\n")
    # If limit is higher than the number of epochs, we will just give all epochs without error message

    try:
        offset = int(request.args.get('offset',0))
    except ValueError:
        return("Invalid offset parameter; offset must be an integer.\n", 400)    
    if offset < 0:
        return("Error: offset must be a positive integer.\n")
    if offset >= len(state_vector_data):
        return("Error: offset is equal to or greater than number of epochs (" + str(len(state_vector_data)) + ").\n") 

    list_of_epochs = []
    offset_count = 0
    epoch_count = 0
    for item in state_vector_data:
        if offset_count < offset:
            offset_count += 1
            continue
        if epoch_count == limit:
            break
        list_of_epochs.append(item['EPOCH'])
        epoch_count += 1
    json_list_of_epochs = {'epochs':list_of_epochs}

    return json_list_of_epochs

@app.route('/epochs/<string:epoch>',methods=['GET'])
def get_state_vector(epoch:str) -> dict:
    '''
    This function returns the state vector of the ISS at an inputted epoch. Units are km and km/s

    Args:
        epoch (str) : The epoch at which the user wants the state vector of the ISS

    Returns:
        state_vector (dict) : The state vector of the ISS given as a list of floats [X, Y, Z, X_DOT, Y_DOT, Z_DOT]
    '''
    if not all_data:
        return "Error: ISS Data has been deleted. Use route '/post-data' to restore data.\n"
    
    for i in state_vector_data:
        if i['EPOCH'] == epoch:
            X = float(i['X']['#text'])
            Y = float(i['Y']['#text'])
            Z = float(i['Z']['#text'])
            X_DOT = float(i['X_DOT']['#text'])
            Y_DOT = float(i['Y_DOT']['#text'])
            Z_DOT = float(i['Z_DOT']['#text'])
            state_vector = {"EPOCH" : epoch, "X": X, "Y" : Y, "Z" : Z, "X_DOT" : X_DOT, "Y_DOT" : Y_DOT, "Z_DOT" : Z_DOT}
            return(state_vector)
    return 'Epoch not found.\n'

@app.route('/epochs/<string:epoch>/speed',methods=['GET'])
def get_speed(epoch:str) -> dict:
    '''
        This function returns the absolute speed of the ISS in km/s at an inputted epoch.

        Args:
            epoch (str) : The epoch a twhich the user wants the absolute speed of the ISS

        Returns:
            speed (str) : The absolute speed of the ISS in km/s
    '''
    if not all_data:
        return "Error: ISS Data has been deleted. Use route '/post-data' to restore data.\n"
    
    for i in state_vector_data:
        if i['EPOCH'] == epoch:
            X_DOT = float(i['X_DOT']['#text'])
            Y_DOT = float(i['Y_DOT']['#text'])
            Z_DOT = float(i['Z_DOT']['#text'])
            speed = str(math.sqrt(X_DOT**2 + Y_DOT**2 + Z_DOT**2))
            return({"speed":{"units":"km/s", "value":speed}})
    return 'Epoch not found. Speed cannot be calculated.\n'

@app.route('/help',methods=['GET'])
def help_menu() -> str:
    '''
        This function takes no arguments and returns a block of text detailing all of the routes  
        a user can call in this flask app.

        Args: NONE

        Returns:
            message (str) : A large, detailed string that details all user commands to this app
    '''
    intro = "Usage (terminal): curl 'localhost:5000[route]' \n\n"
    routes = "Routes: \n"
    slash = "    '/'                        Returns entire ISS dataset in json dictionary form\n"
    epochs = "    '/epochs'                  Returns a list of all epochs of recorded ISS data\n"
    query = "                                   Query Parameters: \n"
    queryl = "                                       limit   Positive integer of how many epochs to display\n"
    queryo = "                                       offset  Positive integer of which epoch will start the list\n"
    state = "    '/epochs/<epoch>'          Returns the state vector (position in km and velocity in km/s) of the \n                               ISS at a specified epoch\n"
    speed = "    '/epochs/<epoch>/speed'    Returns the absolute speed of specific epoch in km/s\n"
    help_route = "    '/help'                    Returns this help menu\n"
    delete_data = "    '/delete-data'             Deletes all ISS Data stored in app. Must be run with '-X DELETE' \n                               following the curl command and preceding the address and route.\n"
    post_data = "    '/post-data'               Retrieves ISS data from the ISS website restoring it after use of \n                               '/delete-data'. Must be run with '-X POST' following the curl \n                               command and preceding the address and route.\n"
    message = "\n" + intro + routes + slash + epochs + query + queryl + queryo + state + speed + help_route + delete_data + post_data
    return message

@app.route('/delete-data',methods=['DELETE'])
def delete_all_data() -> str:
    '''
        This function deletes the ISS Data loaded in upon the startup of this flask app. All data
        dictionaries are emptied when this function runs.

        Args: NONE

        Returns: Returns a string saying the ISS Data has been deleted
    '''
    global r, all_data, state_vector_data
    r = {}
    all_data = {}
    state_vector_data = {}
    return "Successfully deleted all ISS Data\n"

@app.route('/post-data',methods=['POST'])
def retrieve_data_again() -> str:
    '''
        This function gets the ISS data back from the ISS website. It gets it using the requests.get
        method. The function fills the dictionaries emptied by the '/delete-data' route.

        Args: NONE

        Returns: Returns a string saying the ISS Data has been deleted
    '''
    global r, all_data, state_vector_data
    r = requests.get(url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    all_data = xmltodict.parse(r.content)
    state_vector_data = all_data['ndm']['oem']['body']['segment']['data']['stateVector']
    return "Restored ISS Data\n"

@app.route('/comment',methods=['GET'])
def get_comment_list() -> dict:
    '''
    This function returns the comments from the ISS data used in this app.

    Args: NONE
    Returns:
        comment_list (dict) : dict of comment list object from ISS data
    '''
    comment_list = all_data['ndm']['oem']['body']['segment']['data']['COMMENT']
    comment_list = {"COMMENT" : comment_list}

    return comment_list

@app.route('/header',methods=['GET'])
def get_header() -> dict:
    '''
    This function returns the header from the ISS data used in this app.
    
    Args: NONE
    Returns: 
        header_list (dict) : returns header dict object from ISS data
    '''
    header_list = all_data['ndm']['oem']['header']
    header_list = {"HEADER" : header_list}

    return header_list

@app.route('/metadata',methods=['GET'])
def get_metadata() -> dict:
    '''
    This function returns the metadata dict object from the ISS data used in this app.

    Args: NONE
    Returns:
        metadata (dict) : metadata dict object from ISS data
    '''
    metadata = all_data['ndm']['oem']['body']['segment']['metadata']
    metadata = {"METADATA" : metadata}

    return metadata

@app.route('/epochs/<string:epoch>/location',methods=['GET'])
def get_location(epoch:str) -> dict:
    '''
    This function returns the latitude, longitude, altitude, and geoposition for a given Epoch

    Args:
        epoch (str) : The epoch at which the user wants the state vector of the ISS
    Returns: 
        location_data (dict) : A dictionary containing location, geoposition, and speed data
    '''

    if not all_data:
        return "Error: ISS Data has been deleted. Use route '/post-data' to restore data.\n"

    state_vector = get_state_vector(epoch)    
    geodata = convert_j2k_to_geoposition(state_vector)
    try: 
        location = {"latitiude":geodata['latitude'],
                    "longitude":geodata['longitude'],
                    "altitude":geodata['altitude']
                    }    

    except:
        return("Invalid Epoch.\nFor a list of valid epochs, please access '/epochs'.\n")

    geocoder = Nominatim(user_agent='iss_tracker')
    geoloc = geocoder.reverse((geodata['latitude'],geodata['longitude']), zoom=15, language='en')
    
    speed = get_speed(epoch)
    try:
        geoinfo_dict = geoloc.raw
        geo = geoinfo_dict['address']
    except AttributeError as e:
        geo = {"geo" : {"Error" : "ISS is over water, GeoPy cannot determine geopositional data"}}
        
    location_data = {"EPOCH":epoch,"location":location,"geo":geo, "speed":{"units":speed["speed"]["units"],"value":speed["speed"]["value"]}}
    
    return(location_data)


@app.route('/now',methods=['GET'])
def get_location_now() -> dict:
    '''
    This function returns the latitude, longitude, altitude, and geoposition for a given Epoch closest to the current time

    Args:
        epoch (str) : The epoch at which the user wants the state vector of the ISS
    Returns:
        location_data (dict) : A dictionary containing location, geoposition, and speed data
    '''

    if not all_data:
        return "Error: ISS Data has been deleted. Use route '/post-data' to restore data.\n"
    
    # Find Closest Epoch to Now
    time_now = time.mktime(time.gmtime())
    time_first_epoch = time.mktime(time.strptime(state_vector_data[0]['EPOCH'][:-5], '%Y-%jT%H:%M:%S'))
    prev_diff = math.fabs(time_now - time_first_epoch)
    closest_epoch = state_vector_data[0]['EPOCH']

    for i in state_vector_data:
        time_epoch = time.mktime(time.strptime(i['EPOCH'][:-5], '%Y-%jT%H:%M:%S'))
        difference = math.fabs(time_now - time_epoch)
        if difference < prev_diff:
            prev_diff = difference
            closest_epoch = i['EPOCH']
            seconds_from_now = time_epoch - time_now
    
    # Get location data from closest epoch
    state_vector = get_state_vector(closest_epoch)
    geodata = convert_j2k_to_geoposition(state_vector)

    try:
        location = {"latitiude":geodata['latitude'],
                    "longitude":geodata['longitude'],
                    "altitude":geodata['altitude']
                    }

    except:
        return("Invalid Epoch.\nFor a list of valid epochs, please access '/epochs'.\n")

    geocoder = Nominatim(user_agent='iss_tracker')
    geoloc = geocoder.reverse((geodata['latitude'],geodata['longitude']), zoom=15, language='en')

    speed = get_speed(closest_epoch)
    try:
        geoinfo_dict = geoloc.raw
        geo = geoinfo_dict['address']
    except AttributeError as e:
        geo = {"geo" : {"Error" : "ISS is over water, GeoPy cannot determine geopositional data"}}

    location_data = {"closest_epoch":closest_epoch,"seconds_from_now":seconds_from_now,"location":location,"geo":geo, "speed":{"units":speed["speed"]["units"],"value":speed["speed"]["value"]}}
    
    return(location_data)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
