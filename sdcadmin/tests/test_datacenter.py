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

from sdcadmin.tests.config.test_config import TestConfig
from sdcadmin.datacenter import DataCenter
from sdcadmin.machine import SmartMachine, KVMMachine
from sdcadmin.network import Network

from mock import MagicMock


# a wild mix of unit and integration tests
# lot of mocking missing...

class TestDataCenter(unittest.TestCase):
    def setUp(self):
        self.config = TestConfig()
        self.dc = DataCenter(sapi=self.config.sapi_ip)


    def test_known_datacenter_apis_are_visible(self):
        self.assertEqual(DataCenter.APIS, ['sapi', 'vmapi', 'fwapi', 'imgapi', 'napi', 'papi', 'workflow'])

    def test_create_with_manual_urls(self):
        self.dc2 = DataCenter('sapi', 'vmapi', 'fwapi', 'imgapi', 'napi', 'papi', 'workflow')
        for api in DataCenter.APIS:
            self.assertEqual(getattr(self.dc2, api), 'http://' + api)

    def test_create_with_sapi_url_only(self):


        self.assertEqual(self.dc.vmapi, 'http://' + self.config.vmapi_ip)
        self.assertEqual(self.dc.fwapi, 'http://' + self.config.fwapi_ip)
        self.assertEqual(self.dc.imgapi, 'http://' + self.config.imgapi_ip)
        self.assertEqual(self.dc.napi, 'http://' + self.config.napi_ip)
        self.assertEqual(self.dc.papi, 'http://' + self.config.papi_ip)
        self.assertEqual(self.dc.workflow, 'http://' + self.config.workflow_ip)


    def test_health_check_vmapi(self):
        self.assertTrue(self.dc.healthcheck_vmapi())


    def test_list_smart_machines_has_correct_type(self):

        vms = self.dc.list_smart_machines()
        if not vms:
            # TODO: mocking
            pass
        self.assertIsInstance(vms.pop(), SmartMachine)

    def test_list_kvm_machines_has_correct_type(self):

        vms = self.dc.list_kvm_machines()
        if not vms:
            # TODO: mocking
            pass
        self.assertIsInstance(vms.pop(), KVMMachine)

    def test_list_machines_has_both_types(self):
        vms = self.dc.list_machines()
        if not vms:
            # TODO: mocking
            pass
        kvmFound = False
        smFound = False

        for vm in vms:
            if isinstance(vm, SmartMachine):
                smFound = True
            if isinstance(vm, KVMMachine):
                kvmFound = True

        self.assertTrue(kvmFound)
        self.assertTrue(smFound)

    def test_get_smart_machine(self):
        vms = self.dc.list_smart_machines()
        test_vm = vms.pop()
        verify_vm = self.dc.get_smart_machine(test_vm.uuid)
        self.assertEqual(test_vm, verify_vm)

    def test_get_kvm_machine(self):
        vms = self.dc.list_kvm_machines()
        test_vm = vms.pop()
        verify_vm = self.dc.get_kvm_machine(test_vm.uuid)
        self.assertEqual(test_vm, verify_vm)

    def test_get_machine(self):
        smart_machines = self.dc.list_smart_machines()
        kvm_machines = self.dc.list_kvm_machines()

        test_sm = smart_machines.pop()
        test_kvm = kvm_machines.pop()

        test_sm_ = self.dc.get_machine(test_sm.uuid)
        self.assertEqual(test_sm, test_sm_)

        test_kvm_ = self.dc.get_machine(test_kvm.uuid)
        self.assertEqual(test_kvm, test_kvm_)

    def test_list_networks(self):

        network_dummy_data = [{'uuid': 'foo'}, {'uuid': 'bar'}]
        self.dc.request = MagicMock()
        self.dc.request.return_value = (network_dummy_data, None)
        networks = self.dc.list_networks()
        self.dc.request.assert_called_once_with('GET', 'napi', '/networks')
        self.assertEqual(networks.__len__(), 2)
        self.assertEqual(networks.pop().uuid, 'bar')
        self.assertEqual(networks.pop().uuid, 'foo')


    def test_find_next_free_vlan(self):

        self.dc.request = MagicMock()

        raw_network_data = [
            {u'vlan_id': 0},
            {u'vlan_id': 0},
            {u'vlan_id': 1337}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_vlan(), 2)

        raw_network_data = [
            {u'vlan_id': 0},
            {u'vlan_id': 1},
            {u'vlan_id': 2}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_vlan(), 3)

        raw_network_data = [
            {u'vlan_id': 2},
            {u'vlan_id': 1},
            {u'vlan_id': 0}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_vlan(), 3)

        raw_network_data = [
            {u'vlan_id': 3},
            {u'vlan_id': 1},
            {u'vlan_id': 2}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_vlan(), 4)

        raw_network_data = [{u'vlan_id': i } for i in xrange(0,4096)]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_vlan(), None)

    def test_find_next_free_network(self):

        self.dc.request = MagicMock()

        raw_network_data = [
            {u'subnet': u'192.168.2.0/24'},
            {u'subnet': u'10.0.0.0/24'},
            {u'subnet': u'10.0.1.0/24'},
            {u'subnet': u'10.0.2.0/24'}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_network(24), '10.0.3.0/24')

        raw_network_data = [
            {u'subnet': u'192.168.2.0/24'},
            {u'subnet': u'10.0.2.0/24'},
            {u'subnet': u'10.0.1.0/24'},
            {u'subnet': u'10.0.0.0/24'}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_network(24), '10.0.3.0/24')

        raw_network_data = [
            {u'subnet': u'192.168.2.0/24'},
            {u'subnet': u'10.0.0.0/23'},
            {u'subnet': u'10.0.2.0/25'}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_network(25), '10.0.2.128/25')

        raw_network_data = [
            {u'subnet': u'192.168.2.0/24'},
            {u'subnet': u'10.0.0.0/23'},
            {u'subnet': u'10.0.1.0/24'}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_network(24), '10.0.2.0/24')

        raw_network_data = [
            {u'subnet': u'192.168.2.0/24'},
            {u'subnet': u'10.0.0.0/22'}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_network(24), '10.0.4.0/24')

        raw_network_data = [
            {u'subnet': u'192.168.2.0/24'},
            {u'subnet': u'10.0.0.0/25'}
        ]
        self.dc.request.return_value = ( raw_network_data, None )
        self.assertEqual(self.dc.next_free_network(24), '10.0.1.0/24')

