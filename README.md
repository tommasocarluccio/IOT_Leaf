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
Eventually, services communications are based on HTTP and MQTT protocols, ensuring a distributed system which load can be splitted among different nodes.

## Getting started
It is suggested to use a virtual **Python 3** environment, installing the necessary requirements:

``
pip3 install -r requirements.txt
``
