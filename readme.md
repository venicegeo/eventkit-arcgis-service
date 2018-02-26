Eventkit-ArcGIS-Service
==============
Eventkit-ArcGIS-Service is a service that can be run on an ArcGIS Engine/Server host to handle requests from EventKit.

### Installation
Activate the arcgis python environment then install the dependencies with:
<pre> pip install -r requirements.txt</pre>

### Getting Started
Run the service:
<pre> python manage.py serve 127.0.0.1 8000 </pre>

Check the service by navigating in a browser http://127.0.0.1:8000/healthcheck.

_Note: To satisfy security requirements of django you may need to manually set a `HOSTNAME` in the environment if the location of the server doesn't match the hostname of the server._