# LEAF: IoT Monitoring Platform

<img src="http://www.politocomunica.polito.it/var/politocomunica/storage/images/media/images/marchio_logotipo_politecnico/1371-1-ita-IT/marchio_logotipo_politecnico_large.jpg" alt="poli_logo" width="200"/>

> **Master course in ICT FOR SMART SOCIETIES**

> **Programming for IoT applications (01QWRBH) 2020-2021**

<img src="https://github.com/tommasocarluccio/IOT_Leaf/blob/develop/documents/leaf_logo.png" alt="leaf_logo" width="150"/>

Source code for the project ***Leaf***🌱, a low-cost IoT system developed for monitoring the indoor air quality and conditions. 

Video promo: https://www.youtube.com/watch?v=uD7t_eonkQc

Video demo: https://www.youtube.com/watch?v=qpY-RZPQCd0

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

## Main actors

Each software component is in charge of some specific functionalities only, following the micro-services approach.

#### Catalog

The main components are:
- **Service Catalog**, for registering and retrieving services information
- **Clients Catalog**, storing information concerning the formally deployed platforms and registered users
- **Profiles Catalog**, where preferences set by the user referred to platforms are collected
- **Resources Catalog**, tracking all the present and available devices (i.e. sensors, LED, display) following a hierarchical structure according to platforms and rooms

#### Controls

Also controls strategies have been included in order to analyze collected data and inform the user about critical conditions.
In particular:
- **LED Controller**, sending real-time the actuation command to registered LEDs according to the associated parameter value and the corresponding thresolds retrieved by the Profiles Catalog.
- **Telegram Alerting**, crucial for the monitoring functionalities. It sends warning notifications concerning the environmental conditions of the last hour, including tips related to the specific situation.

#### Platform

This section is in charge of allowing the physical platform to communicate with the system:
- **Room**, for performing the association of the hardware kit with the virtual instance
- **Sensors**, for collecting environmental data
- **Display**, showing real-time overview
- **LED**, used for alerting

#### Database

- **Database Adaptor**, linking Thingspeak (for storing historical data) with the other system services.
- **Tips**, exposing useful tips for the final user.

#### User interface

The final user can interact with the system by exploting:
- **Telegram Bot**, to visualize all data and information, receiving notifications and setting preferences.
- **Grafana**, offering a fascinating dashboard for data visualization
- **Statics**, presenting interesting insights according to different time period


## Getting started

#### Configuration

It is suggested to use a virtual **Python 3** environment, installing the necessary requirements:

``
pip3 install -r requirements.txt
``

Then, it is important to set the IP address of crucial built-in services: service catalog, MQTT broker, Grafana and ngrok. The following command will set all the configuration files accordingly (replace IP address and  port with the desired ones):

``
python3 conf_ip.py -sc=192.168.1.130:8080 -br=192.168.1.130:1883 -gr=192.168.1.130:3000 -nk=192.168.1.130:4040
``

For setting ngrok, edit the configuration file:
> ngrok.yml
#### Run the services

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
