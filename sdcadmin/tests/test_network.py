__author__ = 'ernm'


import unittest

from mock import MagicMock
from sdcadmin.network import Network

# unit tests for classes: NicTag, Network, Nics, NetworkPools, Aggregations

class TestNetwork(unittest.TestCase):

    network_raw_data = {
            "uuid": "1275886f-3fdf-456e-bba6-28e0e2eab58f",
            "name": "admin",
            "vlan_id": 0,
            "subnet": "10.99.99.0/24",
            "netmask": "255.255.255.0",
            "provision_start_ip": "10.99.99.189",
            "provision_end_ip": "10.99.99.250",
            "resolvers": [
              "8.8.4.4",
              "8.8.8.8"
            ],
            "gateway": "10.99.99.7"
    }

    def setUp(self):
        self.stub_network = Network(datacenter=None, data=self.network_raw_data)

    def test_creation_of_network_from_raw_data(self):

        for k, v in self.network_raw_data.iteritems():
            self.assertEqual(v, getattr(self.stub_network, k))

    def test_has_required_functions(self):

        known_functions = ['delete', 'refresh']

        for function in known_functions:
            self.assertIsNotNone(getattr(self.stub_network, function))

    def test_create_network_from_uuid(self):
        dc = MagicMock()
        dc.request = MagicMock()
        dc.request.return_value = ({'uuid': 'foo', 'foo': 'bar'}, None)
        network = Network(datacenter=dc, uuid='foo')
        dc.request.assert_called_once_with('GET', 'napi', '/networks/foo')
        self.assertEqual(network.uuid, 'foo')
        self.assertEqual(network.foo, 'bar')


    def test_refresh(self):

        network_test_data = {'uuid': 'test', 'foo': 'bar'}
        network = Network(datacenter=MagicMock(), data=network_test_data)
        network.dc.request = MagicMock()
        network.dc.request.return_value = ({'foo': 'not-bar'}, None)
        network.refresh()
        self.assertEqual(getattr(network, 'foo'), 'not-bar')
        self.assertEqual(network.dc.request.call_count, 1)

