# ISS Tracker

The primary objective of this project was to take the position and velocity data provided on the ISS website and
return various forms of it to the user via a Flask application. A Flask application is a web server with which a
REST API can be set up with multiple routes. With a Flask server running, users can query for whatever data you set
up to be accessed via the API. In this folder you will find two files: iss\_tracker.py & Dockerfile. When
iss\_tracker.py is run, this code creates an API that can be accessed to return various information about the state
of the ISS. This data comes from and can be accessed at this website in either .txt or .xml format:
    https://spotthestation.nasa.gov/trajectory\_idata.cfm .
Aside from providing the data, this website describes the data in more detail.

In addition to providing the python script, there is also a Dockerfile provided for this package. This containerizes
the code for use on other machines through managing the dependencies.

## ISS Data

The data that can be gathered from this REST API is mostly position and velocity data of the ISS at a given epoch.
An epoch is a point in time and is represented by a string in the form '<YEAR>-<DAYOFYEAR>T<TIME>Z'. At a given epoch,
the ISS data records a state vector with the three components of the position and velocity in the J2000 frame. The
units for these components are km and km/s respectively.

## iss\_tracker.py

This python script runs the API that the user can pull from. It has the following routes:
    '/'
    '/epochs' - contains query parameters 'limit' and 'offset
    '/epochs/\<epoch>'
    '/epochs/\<epoch>/speed'
    '/help'
    '/delete-data'
    '/post-data'

'/' returns the entire data set for the ISS tracker in .xml form. It returns it to the user as a dictionary.

'/epochs' returns a list of strings that contains all of the epochs (times) contained in the data.

'/epochs/\<epoch>' returns the state vector of the ISS at the given epoch.

'/epochs/\<epoch\>/speed' returns the absolute speed of the ISS in km/s at the given epoch.

## How to run the code

To run the code, navigate to the directory that contains both the Dockerfile and the python script iss\_tracker.py.
From there, you will want to either pull the Docker image from Docker Hub or build a new Docker image using the
Dockerfile included. In any case, creating this docker image will ensure you have the correct dependencies to
run the code.

### Pull Docker image from Docker Hub

Here is the command to pull this container from Docker Hub:
```
    docker pull izaacfacundo/iss_tracker:hw5
```
### Build Docker Image locally

To build the docker image locally, you must run the following command from within the directory that the python
script and Dockerfile reside:
```
    docker build -t izaacfacundo/iss_tracker:hw5
```

### Run code with built docker image

Finally, to run the Flask web server you must run the following command:
```
    docker run -t --rm -p 5000:5000 izaacfacundo/iss_tracker:hw5
```
This launches the REST API that you can then call with the command 'curl'.

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

Here is another example command:
```
    curl -X DELETE localhost:5000/delete-data
```
This should produce this message:
```
    Successfully deleted all ISS Data
```
And all routes other than '/post-data' should produce an error message.
