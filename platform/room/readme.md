### Room Association

The script should be used to associate the physical hardware kit with the corresponding virtual instance created by the user.
Run the command:

> python3 room_run.py conf/default.json [platform_ID]

where [platform_ID] should be replaced with the proper platform ID. Example:

> python3 room_run.py conf/default.json Leaf_002

The system will register the new room association performed returning useful information (e.g. room_ID). If the room was previously correctly associated, request will be discarded.
