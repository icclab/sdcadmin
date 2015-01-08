__author__ = 'ernm'

import unittest

from sdcadmin.datacenter import DataCenter
from sdcadmin.package import Package
from sdcadmin.tests.config.test_config import TestConfig

class TestPackages(unittest.TestCase):
    def setUp(self):
        self.dc = DataCenter(sapi=TestConfig.sapi_ip)

    def test_list_all_packages(self):
        packages = self.dc.list_packages()
        self.assertIsNotNone(packages)
        self.assertIsInstance(packages, list)
        self.assertGreater(packages.__len__(),0, 'no packages returned')
        for package in packages:
            self.assertIsInstance(package, Package)
            for attr in ['uuid', 'owner_uuids']:
                self.assertIsNotNone(package.__getattribute__(attr))

            self.assertGreater(package.owner_uuids.__len__(), 0, 'no owner_uuids found')


    def test_get_package_by_uuid(self):
        packages = self.dc.list_packages()
        package = packages.pop()

        package_ = self.dc.get_package(uuid=package.uuid)
        self.assertEqual(package, package_)
