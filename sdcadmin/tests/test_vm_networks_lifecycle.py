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
import uuid
import time

from sdcadmin.tests.config.test_config import TestConfig
from sdcadmin.datacenter import DataCenter
from sdcadmin.machine import SmartMachine
from sdcadmin.network import Network



# a wild mix of unit and integration tests
# lot of mocking missing...

class TestLifeCycleVMandNetwork(unittest.TestCase):
    def setUp(self):
        self.config = TestConfig()
        self.dc = DataCenter(sapi=self.config.sapi_ip)

    def test_attach_nics_to_machines(self):

        my_alias = uuid.uuid4().__str__()

        # setup vm
        smartmachine = self.dc.create_smart_machine(owner=self.config.user_uuid,
                                                   networks=[self.config.external_network_uuid],
                                                   package=self.config.package_small,
                                                   image=self.config.smartmachine_image,
                                                   alias=my_alias)


        # verify vm
        self.assertIsInstance(smartmachine, SmartMachine)
        self.assertIsInstance(smartmachine, SmartMachine)
        self.assertNotEqual(smartmachine.status(), DataCenter.STATE_RUNNING)
        self.assertFalse(smartmachine.is_running())
        smartmachine.poll_until(status=DataCenter.STATE_RUNNING)
        smartmachine.refresh()
        self.assertEqual(smartmachine.status(), DataCenter.STATE_RUNNING)
        self.assertTrue(smartmachine.is_running())

        # setup net
        my_network = self.dc.create_network(name=self.config.network_name,
                                            owner_uuids=[self.config.user_uuid],
                                            subnet=self.config.subnet,
                                            gateway=self.config.gateway,
                                            provision_start_ip=self.config.provision_start_ip,
                                            provision_end_ip=self.config.provision_end_ip,
                                            vlan_id=self.config.vlan_id,
                                            nic_tag=self.config.nic_tag,
                                            resolvers=self.config.resolvers,
                                            routes=self.config.routes,
                                            description=self.config.network_description)

        # verify net
        self.assertIsInstance(my_network, Network)
        self.assertIsNotNone(my_network.uuid)
        my_network_ = self.dc.get_network(uuid=my_network.uuid)
        self.assertEqual(my_network, my_network_)

        # add net to vm
        smartmachine.add_nic(my_network.uuid, ip=self.config.test_ip_1)
        time.sleep(30) # FIXME: add_nic has no blocking method
        smartmachine.refresh()

        self.assertTrue(smartmachine.is_attached_to_network(my_network.uuid))

        self.assertEqual(smartmachine.nics.__len__(), 2)
        self.assertEqual(smartmachine.nics[1].get('network_uuid'), my_network.uuid)
        self.assertEqual(smartmachine.nics[1].get('ip'), self.config.test_ip_1)


        smartmachine.remove_nic(mac_address=smartmachine.nics[1].get('mac'))
        time.sleep(30) # FIXME: add_nic has no blocking method
        smartmachine.refresh()

        self.assertFalse(smartmachine.is_attached_to_network(my_network.uuid))

        self.assertEqual(smartmachine.nics.__len__(), 1)

        # clean up
        my_network.delete()
        my_network_ = self.dc.get_network(uuid=my_network.uuid)
        self.assertIsNone(my_network_, 'network still exists')

        smartmachine.delete()
        smartmachine.poll_until(status=DataCenter.STATE_DESTROYED)
        self.assertEqual(smartmachine.status(), DataCenter.STATE_DESTROYED)



