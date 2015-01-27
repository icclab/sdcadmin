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
__author__ = 'ernm'

import unittest

from sdcadmin.datacenter import DataCenter
from sdcadmin.network import Network
from sdcadmin.tests.config.test_config import TestConfig


# a wild mix of unit and integration tests
# lot of mocking missing...

class TestLifeCycleNetwork(unittest.TestCase):
    def setUp(self):
        self.config = TestConfig()
        self.dc = DataCenter(sapi=self.config.sapi_ip)

    def test_network_lifecycle(self):
        my_network = self.dc.create_network(name='foo_net', owner_uuids=[self.config.user_uuid], subnet='10.10.0.0/24',
                                            gateway='10.10.0.100', provision_start_ip='10.10.0.101',
                                            provision_end_ip='10.10.0.200', vlan_id='1337', nic_tag='customer',
                                            resolvers=['8.8.8.8', '8.8.4.4'], routes={'10.11.0.0/24': '10.10.0.50'},
                                            description='foo_net_desc')

        self.assertIsInstance(my_network, Network)
        self.assertIsNotNone(my_network.uuid)

        my_network_ = self.dc.get_network(uuid=my_network.uuid)
        self.assertEqual(my_network, my_network_)

        my_network.delete()
        my_network_ = self.dc.get_network(uuid=my_network.uuid)
        self.assertIsNone(my_network_)



