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

from sdcadmin.tests.config.test_config import TestConfig
from sdcadmin.datacenter import DataCenter
from sdcadmin.machine import SmartMachine, KVMMachine



# a wild mix of unit and integration tests
# lot of mocking missing...

class TestDataCenter(unittest.TestCase):
    def setUp(self):
        self.config = TestConfig()
        self.dc = DataCenter(sapi=self.config.sapi_ip)


    def test_smart_machine_lifecycle(self):
        # return True
        my_alias = uuid.uuid4().__str__()

        smartmachine = self.dc.create_smart_machine(owner=self.config.user_uuid,
                                                    networks=[self.config.network_uuid],
                                                    package=self.config.package_small,
                                                    image=self.config.smartmachine_image,
                                                    alias=my_alias)

        self.assertIsInstance(smartmachine, SmartMachine)
        self.assertNotEqual(smartmachine.status(), DataCenter.STATE_RUNNING)
        self.assertFalse(smartmachine.is_running())
        smartmachine.poll_until(status=DataCenter.STATE_RUNNING)
        smartmachine.refresh()
        self.assertEqual(smartmachine.status(), DataCenter.STATE_RUNNING)
        self.assertTrue(smartmachine.is_running())
        self.assertFalse(smartmachine.is_destroyed())
        smartmachine.delete()
        smartmachine.poll_until(status=DataCenter.STATE_DESTROYED)
        self.assertEqual(smartmachine.status(), DataCenter.STATE_DESTROYED)

    def test_kvm_machine_lifecycle(self):
        my_alias = uuid.uuid4().__str__()

        kvm_machine = self.dc.create_kvm_machine(owner=self.config.user_uuid,
                                                 networks=[self.config.network_uuid],
                                                 package=self.config.package_small,
                                                 image=self.config.kvm_image,
                                                 alias=my_alias)

        self.assertIsInstance(kvm_machine, KVMMachine)
        self.assertNotEqual(kvm_machine.status(), DataCenter.STATE_RUNNING)
        kvm_machine.poll_until(status=DataCenter.STATE_RUNNING)
        kvm_machine.refresh()
        self.assertEqual(kvm_machine.status(), DataCenter.STATE_RUNNING)
        kvm_machine.delete()
        kvm_machine.poll_until(status=DataCenter.STATE_DESTROYED)
        self.assertEqual(kvm_machine.status(), DataCenter.STATE_DESTROYED)


    def test_both_combined_lifecycle_and_retrieval(self):
        my_smart_machine_alias = uuid.uuid4().__str__()
        my_kvm_machine_alias = uuid.uuid4().__str__()

        smart_machine = self.dc.create_smart_machine(owner=self.config.user_uuid,
                                                     networks=[self.config.network_uuid],
                                                     package=self.config.package_small,
                                                     image=self.config.smartmachine_image,
                                                     alias=my_smart_machine_alias,
                                                     user_script="touch /test-file")

        self.assertIsInstance(smart_machine, SmartMachine)
        self.assertNotEqual(smart_machine.status(), DataCenter.STATE_RUNNING)
        self.assertFalse(smart_machine.is_running())
        smart_machine.poll_until(status=DataCenter.STATE_RUNNING)
        smart_machine.refresh()
        self.assertEqual(smart_machine.status(), DataCenter.STATE_RUNNING)
        self.assertTrue(smart_machine.is_running())
        self.assertFalse(smart_machine.is_destroyed())

        kvm_machine = self.dc.create_kvm_machine(owner=self.config.user_uuid,
                                                 networks=[self.config.network_uuid],
                                                 package=self.config.package_small,
                                                 image=self.config.kvm_image,
                                                 alias=my_kvm_machine_alias,
                                                 user_script="touch /test-file")

        self.assertIsInstance(kvm_machine, KVMMachine)
        self.assertNotEqual(kvm_machine.status(), DataCenter.STATE_RUNNING)
        kvm_machine.poll_until(status=DataCenter.STATE_RUNNING)
        self.assertEqual(kvm_machine.status(), DataCenter.STATE_RUNNING)
        kvm_machine.refresh()

        smart_machine = self.dc.get_machine(my_smart_machine_alias)
        self.assertIsInstance(smart_machine, SmartMachine)
        self.assertEqual(smart_machine, smart_machine)

        kvm_machine_ = self.dc.get_machine(my_kvm_machine_alias)
        self.assertIsInstance(kvm_machine_, KVMMachine)
        self.assertEqual(kvm_machine_, kvm_machine)

        smart_machine.delete()
        smart_machine.poll_until(status=DataCenter.STATE_DESTROYED)
        self.assertEqual(smart_machine.status(), DataCenter.STATE_DESTROYED)
        kvm_machine.delete()
        kvm_machine.poll_until(status=DataCenter.STATE_DESTROYED)
        self.assertEqual(kvm_machine.status(), DataCenter.STATE_DESTROYED)

