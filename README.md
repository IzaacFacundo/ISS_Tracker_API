# ISS Tracker

The primary objective of this project was to take the position and velocity data provided on the ISS website and
return various forms of it to the user via a Flask application. A Flask application is a web server with which a
REST API can be set up with multiple routes. With a Flask server running, users can query for whatever data you set
up to be accessed via the API. In this folder you will find two files: iss\_tracker.py & Dockerfile. When
iss\_tracker.py is run, this code creates an API that can be accessed to return various information about the state
of the ISS. This data comes from and can be accessed at this website in either .txt or .xml format:
    https://spotthestation.nasa.gov/trajectory_idata.cfm .
Aside from providing the data, this website describes the data in more detail.

In addition to providing the python script, there is also a Dockerfile provided for this package. This containerizes
the code for use on other machines through managing the dependencies.

## ISS Data

The data that can be gathered from this REST API is mostly position and velocity data of the ISS at a given epoch.
An epoch is a point in time and is represented by a string in the form '\<YEAR\>-\<DAYOFYEAR\>T\<TIME\>Z'. At a given epoch,
the ISS data records a state vector with the three components of the position and velocity in the J2000 frame. The
units for these components are km and km/s respectively.

## iss\_tracker.py

This python script runs the API that the user can pull from. It has the following routes:  

'/' - returns the entire data set for the ISS tracker in .xml form. It returns it to the user as a dictionary.

'/epochs' - returns a list of strings that contains all of the epochs (times) contained in the data.

'/epochs/\<epoch>' - returns the state vector of the ISS at the given epoch.

'/epochs/\<epoch\>/speed' - returns the absolute speed of the ISS in km/s at the given epoch.

'/help' - returns a message detailing all routes available to the user.

'/delete-data' - deletes the ISS data that was pulled from the .xml file on the ISS website

'/post-data' - posts the ISS data back to the server for use in other methods after it's been deleted

'/comment' - returns the comment block from the ISS .xml data

'/header' - returns the header object from the ISS .xml data

'/metadata' - returns the metadata object from the ISS .xml data

'/epochs/\<epoch\>/location' - returns the geopositional location data for a given epoch

'/now' - returns the geopositional location data for the epoch closest to the current time

## How to run the code

To run the code, navigate to the directory that contains both the Dockerfile and the python script iss\_tracker.py.
From there, you will want to either pull the Docker image from Docker Hub or build a new Docker image using the
Dockerfile included. In any case, creating this docker image will ensure you have the correct dependencies to
run the code. Docker must be installed to pull the image or create the container.

### Build Docker image locally

To build the docker image locally, you must run the following command from within the directory that the python
script and Dockerfile reside:
```
    docker build -t izaacfacundo/iss_tracker:2.0 .
```

### Pull Docker image from Docker Hub

Here is the command to pull this container from Docker Hub:
```
    docker pull izaacfacundo/iss_tracker:2.0
```

### Run code with pulled or locally built docker image

To run the Flask web server you must run the following command:
```
    docker run -t --rm -p 5000:5000 izaacfacundo/iss_tracker:2.0
```
This launches the REST API server that you can then call with the command 'curl'.

### Launch container locally using docker-compose

To create the container locally and automatically run the server, you must run the following command from within  
the directory that the python script, Dockerfile, and docker-compose.yml file reside:
```
    docker-compose up
```
This launches the REST API server that you can then call with the command 'curl'.


### Example Queries

Once the Flask web server is running, you can use any of the routes above to access, delete, or restore the ISS
data. Here is an example command:
```
    curl 'localhost:5000/epochs?limit=5&offset=20'
```
This should produce this output:
```
{
  "epochs": [
    "2023-058T13:20:00.000Z",
    "2023-058T13:24:00.000Z",
    "2023-058T13:28:00.000Z",
    "2023-058T13:32:00.000Z",
    "2023-058T13:36:00.000Z"
  ]
}
```

Here is another example query:
```
    curl -X DELETE localhost:5000/delete-data
```
This should produce this message:
```
    Successfully deleted all ISS Data
```
And all routes other than '/post-data' should produce an error message.


Finally, here is what I believe to be the most impressive query to run:
```
    curl localhost:5000/now
```
This should produce this output:
```
{
  "closest_epoch": "2023-066T04:31:30.000Z",
  "geo": {
    "ISO3166-2-lvl4": "US-NC",
    "country": "United States",
    "country_code": "us",
    "county": "Onslow County",
    "state": "North Carolina"
  },
  "location": {
    "altitude": {
      "units": "km",
      "value": 416.2411014770796
    },
    "latitiude": 34.73405901165495,
    "longitude": -78.85015633069156
  },
  "seconds_from_now": -88.0,
  "speed": {
    "units": "km/s",
    "value": "7.668252667574941"
  }
}
