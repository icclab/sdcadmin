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

from mock import MagicMock
from sdcadmin.machine import SmartMachine, KVMMachine


class TestMachine(unittest.TestCase):
    def test_creation_from_raw_data(self):

        smart_machine_test_data = {'uuid': 'test', 'foo': 'bar'}
        kvm_machine_test_data = {'uuid': 'test', 'foo': 'bar'}
        smart_machine = SmartMachine(datacenter=None, data=smart_machine_test_data)
        kvm_machine = KVMMachine(datacenter=None, data=kvm_machine_test_data)

        for k, v in smart_machine_test_data.iteritems():
            self.assertEqual(v, getattr(smart_machine, k))

        for k, v in kvm_machine_test_data.iteritems():
            self.assertEqual(v, getattr(kvm_machine, k))


    def test_refresh(self):

        smart_machine_test_data = {'uuid': 'test', 'foo': 'bar'}
        smart_machine = SmartMachine(datacenter=MagicMock(), data=smart_machine_test_data)
        smart_machine.dc.request = MagicMock()
        smart_machine.dc.request.return_value = {'foo': 'not-bar'}
        smart_machine.refresh()
        self.assertEqual(getattr(smart_machine, 'foo'), 'not-bar')
        self.assertEqual(smart_machine.dc.request.call_count, 1)

