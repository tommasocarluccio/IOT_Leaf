import json 
import argparse

def set_ip(folder,filename,ip):
	file_path=folder+filename
	conf_content=json.load(open(file_path,"r"))
	conf_content['service_catalog']="http://{}/service_catalog".format(ip)
	with open(file_path,'w') as file:
		json.dump(conf_content,file, indent=4)

def set_services(services_dict):
	conf_content=json.load(open("service catalog/conf/service_catalog.json","r"))

	conf_content['service_catalog']['IP_address']=services_dict['service_catalog'].split(":")[0]
	conf_content['service_catalog']['port']=int(services_dict['service_catalog'].split(":")[1])

	conf_content['broker']['IP_address']=services_dict['broker'].split(":")[0]
	conf_content['broker']['port']=int(services_dict['broker'].split(":")[1])

	conf_content['grafana']['IP_address']=services_dict['grafana'].split(":")[0]
	conf_content['grafana']['port']=int(services_dict['grafana'].split(":")[1])
	conf_content['ngrok']="http://{}".format(services_dict['ngrok'])
	with open("service catalog/conf/service_catalog.json",'w') as file:
		json.dump(conf_content,file, indent=4)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-sc", "--service_catalog", dest = "service_catalog_ip", default = "192.168.1.130:8080")
	parser.add_argument("-br", "--broker", dest = "broker", default = "192.168.1.130:1883")
	parser.add_argument("-gr", "--grafana", dest = "grafana", default = "192.168.1.130:3000")
	parser.add_argument("-nk", "--ngrok", dest = "ngrok", default = "192.168.1.130:4040")

	args = parser.parse_args()
	
	set_ip("clients catalog/conf/","clients_catalog.json",args.service_catalog_ip)
	set_ip("profiles catalog/conf/","profiles_catalog.json",args.service_catalog_ip)
	set_ip("database adaptor/conf/","adaptor.json",args.service_catalog_ip)
	set_ip("grafana/conf/","conf.json",args.service_catalog_ip)
	set_ip("resources catalog/conf/","conf.json",args.service_catalog_ip)
	set_ip("tips catalog/conf/","conf.json",args.service_catalog_ip)

	set_ip("controls/LED_commander/conf/","conf.json",args.service_catalog_ip)
	set_ip("controls/telegram_alerting/conf/","conf.json",args.service_catalog_ip)
	set_ip("statistics/conf/","statistics_catalog.json",args.service_catalog_ip)

	set_ip("platform/display/conf/","conf.json",args.service_catalog_ip)
	set_ip("platform/led/conf/","conf.json",args.service_catalog_ip)
	set_ip("platform/room/conf/","default.json",args.service_catalog_ip)
	set_ip("platform/sensors/conf/","dht11_settings.json",args.service_catalog_ip)
	set_ip("platform/sensors/conf/","mq135_settings.json",args.service_catalog_ip)

	set_ip("bot/conf/","conf.json",args.service_catalog_ip)
	
	services_dict={"service_catalog":args.service_catalog_ip,"broker":args.broker,"grafana":args.grafana, "ngrok":args.ngrok}
	set_services(services_dict)
	print("All configurations set.\nExiting...\n")