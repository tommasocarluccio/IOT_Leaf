# LEAF: IoT Monitoring Platform
![](http://www.politocomunica.polito.it/var/politocomunica/storage/images/media/images/marchio_logotipo_politecnico/1371-1-ita-IT/marchio_logotipo_politecnico_large.jpg) 

> **Master course in ICT FOR SMART SOCIETIES**

> **Programming for IoT applications (01QWRBH) 2020-2021**

Source code for the project ***Leaf***🌱, a low-cost IoT system developed for monitoring the indoor air quality and conditions. 
### Key Features
- Microservices-based architecture
- Hardware kit with sensor network
- Real-time monitoring, including warning, alerting and tips
- Telegram bot and Grafana dashboard for data visualization
- Thingspeak interface for storing data
- External weather conditions API integration
- Data analysis and statistics

## Authors
Andrea Avignone \
Tommaso Carluccio\
Vincenzo Madaghiele

## Architecture overview
The system has been programmed for managing different users and hardware platforms, providing all the necessary aspects:
- Catalogue
- Control strategies functionalities
- User interface
- Sensor network

Each service is supported by one or more configuration file (JSON file).\
Eventually, services communications are based on HTTP REST and MQTT protocols, ensuring a distributed system which load can be splitted among different nodes.

## Getting started
It is suggested to use a virtual **Python 3** environment, installing the necessary requirements:

``
pip3 install -r requirements.txt
``

Scripts have similar structure and they require to be individually launched, indicating the configuration file.
Configuration files can be accessed and edited under:
> /conf

Classes and scripts necessary for the service to properly work are stored in:

> /etc

Services can be run using the specific command or by launching the autorun bash script.
After setting the right permissions:

``
chmod +x /run.sh
``

Run the command:

``
./run.sh
``

## Main actors

Each software component is in charge of some specific functionalities only, following the micro-services approach.
#### Catalogue

The main components are:
- **Service Catalog**, for registering and retrieving services information
- **Clients Catalog**, storing information concerning the formally deployed platforms and registered users
- **Profiles Catalog**, where preferences set by the user referred to platforms are collected
- **Resources Catalog**, tracking all the present and available devices (i.e. sensors, LED, display) following a hierarchical structure according to platforms and rooms
- **Tips Catalog**, exposing useful tips for the final user

