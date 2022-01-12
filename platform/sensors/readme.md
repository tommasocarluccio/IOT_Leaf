### Sensors configuration

Each sensor can be run by using the default script and by specifying the sensor name to correctly import the corresponing class, as well as platform_ID, room_ID and pin/port.
General command:

> python3 main.py [platform_ID] [room_ID] [sensor_name] [pin]

In particular, to run the gas sensor for a testing platform which input is coming from the serial port:

> python3 main.py Leaf_002 room_1 mq5 /dev/ttyACM0

For the temperature and humidity sensor:

> python3 main.py Leaf_002 room_1 dht11 4
