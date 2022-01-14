import json 
import argparse

def set_ip(folder,filename,ip):
	file_path=folder+filename
	conf_content=json.load(open(file_path,"r"))
	conf_content['service_catalog']="http://{}/service_catalog".format(ip)
	with open(file_path,'w') as file:
		json.dump(conf_content,file, indent=4)

if __name__ == '__main__':
	parser.add_argument("-service", "--service_catalog", dest = "service_catalog_ip", default = "192.168.1.130:8080")
	parser.add_argument("-broker", "--broker", dest = "broker", default = "192.168.1.130:1883")
	parser.add_argument("-grafana", "--grafana", dest = "grafana", default = "192.168.1.130:4000")

	set_ip("clients catalog/conf/","clients_catalog.json",service_catalog_ip)
	set_ip("profiles catalog/conf/","profiles_catalog.json",service_catalog_ip)
	set_ip("database adaptor/conf/","adaptor.json",service_catalog_ip)
	set_ip("grafana/conf/","conf.json",service_catalog_ip)
	set_ip("resources catalog/conf/","conf.json",service_catalog_ip)
	set_ip("tips catalog/conf/","conf.json",service_catalog_ip)

	set_ip("controls/LED_commander/conf/","conf.json",service_catalog_ip)
	set_ip("controls/telegram_alerting/conf/","conf.json",service_catalog_ip)
	set_ip("statistics/conf/","statistics_catalog.json",service_catalog_ip)

	set_ip("platform/display/conf/","conf.json",service_catalog_ip)
	set_ip("platform/led/conf/","conf.json",service_catalog_ip)
	set_ip("platform/room/conf/","default.json",service_catalog_ip)
	set_ip("platform/sensors/conf/","dht11_settings.json",service_catalog_ip)
	set_ip("platform/sensors/conf/","mq135_settings.json",service_catalog_ip)

	set_ip("bot/conf/","conf.json",service_catalog_ip)