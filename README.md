# sdcadmin

Early version! 
Wrapps SDC APIs on the admin network.

## Usage:

```
from sdcadmin.datacenter import DataCenter
dc = DataCenter(sapi=sapi_ip)
dc.list_smart_machines()
dc.create_smart_machine(owner=user_uuid, networks=[network_uuid],
                        package=package_small, image=smartmachine_image,
                        alias='my_first_smart_machine')
```
