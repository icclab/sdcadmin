# sdcadmin

Warning: early version! 
Wrapps SDC APIs on the admin network.

## Synopsis
This python package wrapps the SmartDataCenter APIs on the admin network. It is used in the OpenStack Heat plugin [sdc-heat](https://github.com/icclab/sdc-heat).

## Usage:

```
from sdcadmin.datacenter import DataCenter
dc = DataCenter(sapi=sapi_ip)
dc.list_smart_machines()
dc.create_smart_machine(owner=user_uuid, networks=[network_uuid],
                        package=package_small, image=smartmachine_image,
                        alias='my_first_smart_machine')
```



## Motivation

***Q: Why the admin APIs instead of the cloudapi?***

A: The cloudapi of SDC requires signing each request with the users ssh private key and does not give control over resources such as networks. 

## Installation

The package is available on [pypi.python.org](https://pypi.python.org/pypi/sdcadmin/). 

```
pip install sdcadmin
```

## API Reference

\#TODO

## Tests
some very basic tests using unittest are located in ```sdcadmin/tests```.

## Contributors

Pull requests, issues and questions are more than welcome!

## License

```
# Copyright 2015 Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
```