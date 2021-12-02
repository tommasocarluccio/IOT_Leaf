from clients_class import *

catalog=ClientsCatalog("etc/conf.json")
catalog.platforms.find_platform("Leaf_001")["associated"]=False
print(catalog.platforms.find_user("Leaf_001"))
#catalog.platforms.save()