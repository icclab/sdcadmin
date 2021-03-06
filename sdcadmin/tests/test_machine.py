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
        smart_machine.dc.request.return_value = ({'foo': 'not-bar'}, None)
        smart_machine.refresh()
        self.assertEqual(getattr(smart_machine, 'foo'), 'not-bar')
        self.assertEqual(smart_machine.dc.request.call_count, 1)

    def test_is_attached_to_network(self):

        smart_machine_test_data = {'uuid': 'test',  'nics': [{'network_uuid': 'foo'}, {'network_uuid': 'bar'}]}
        smart_machine = SmartMachine(datacenter=MagicMock(), data=smart_machine_test_data)
        smart_machine.refresh = MagicMock()
        self.assertTrue(smart_machine.is_attached_to_network('foo'))
        self.assertTrue(smart_machine.is_attached_to_network('bar'))
        self.assertFalse(smart_machine.is_attached_to_network('foobar'))


    def test_update_specific_metadata(self):

        old = {'foo': 'bar'}
        new = {'foo2': 'bar2'}
        smart_machine_test_data = {'uuid': 'test',
                                   'customer_metadata': old,
                                   'internal_metadata': old,
                                   'tags': old}

        smart_machine = SmartMachine(datacenter=MagicMock(), data=smart_machine_test_data)
        smart_machine.update_metadata = MagicMock()


        smart_machine.update_customer_metadata(data=new)
        smart_machine.update_metadata.assert_called_with(field='customer_metadata', data=new)
        smart_machine.update_internal_metadata(data=new)
        smart_machine.update_metadata.assert_called_with(field='internal_metadata', data=new)
        smart_machine.update_tags(data=new)
        smart_machine.update_metadata.assert_called_with(field='tags', data=new)


    def test_update_metadata(self):
        old = {'foo': 'bar'}
        new = {'foo2': 'bar2'}
        smart_machine_test_data = {'uuid': 'test',
                                   'customer_metadata': old,
                                   'internal_metadata': old,
                                   'tags': old}
        smart_machine = SmartMachine(datacenter=MagicMock(), data=smart_machine_test_data)
        smart_machine.dc.request = MagicMock()
        smart_machine.dc.request.return_value = ({'vm_uuid': 'test'}, None)

        smart_machine.update_metadata(field='customer_metadata', data=new)
        smart_machine.dc.request.assert_called_once_with('PUT', 'vmapi',
                                                         '/vms/%s/customer_metadata' % smart_machine.uuid, data=new)
        smart_machine.dc.request.reset_mock()

        smart_machine.update_metadata(field='internal_metadata', data=new)
        smart_machine.dc.request.assert_called_once_with('PUT', 'vmapi',
                                                         '/vms/%s/internal_metadata' % smart_machine.uuid, data=new)

        smart_machine.dc.request.reset_mock()

        smart_machine.update_metadata(field='tags', data=new)
        smart_machine.dc.request.assert_called_once_with('PUT', 'vmapi',
                                                         '/vms/%s/tags' % smart_machine.uuid, data=new)

        smart_machine.dc.request.reset_mock()
