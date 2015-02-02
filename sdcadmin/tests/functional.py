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
import time

from sdcadmin.tests.config.test_config import TestConfig


class LifecycleTest(unittest.TestCase):
    def test_create_retrieve_save_delete(self):
        # John is a user who wants to use this library to manage kvm and smart machines on a SDC
        # he was given a user account which he should use as the owner of his systems:
        # user John, password: johnpass1, user-uuid: 9d5ae03c-d64a-ea5b-b020-9ae6e3b6bb9e
        user_uuid = TestConfig.user_uuid

        # John was also given:
        # the sapi URL
        sapi_ip = TestConfig.sapi_ip
        # and 2 package-uuids:
        package_small = TestConfig.package_small
        package_big = TestConfig.package_big

        # the image-uuid for a smartmachine:
        smartmachine_image = TestConfig.smartmachine_image
        kvm_image = TestConfig.kvm_image

        # and the external network:
        external_network_uuid = TestConfig.external_network_uuid


        # John, curious as he is, imports the library
        from sdcadmin.datacenter import DataCenter

        # John creates a datacenter with the sapi information he was provided
        dc = DataCenter(sapi=sapi_ip)
        self.assertTrue(dc.healthcheck_vmapi())

        # John does not want his machines to be public. He looks around for other networks
        self.assertGreater(dc.list_networks().__len__(), 1)

        # John creates his own network
        my_network = dc.create_network(name='john_net', owner_uuids=[user_uuid],
                                       subnet=TestConfig.subnet,
                                       gateway=TestConfig.gateway,
                                       provision_start_ip=TestConfig.provision_start_ip,
                                       provision_end_ip=TestConfig.provision_end_ip,
                                       vlan_id=TestConfig.vlan_id,
                                       nic_tag=TestConfig.nic_tag,
                                       resolvers=TestConfig.resolvers,
                                       routes=TestConfig.routes,
                                       description='john_net for john')
        my_network_uuid = my_network.uuid
        self.assertIsNotNone(my_network)
        self.assertIsNotNone(my_network_uuid)


        # John retrieves his network
        my_network_ = dc.get_network(my_network_uuid)
        self.assertEqual(my_network, my_network_)



        # John sees no machines created yet for his user that are running
        all_my_vms = dc.list_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        all_my_smart_machines = dc.list_smart_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        all_my_kvm_machines = dc.list_kvm_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        self.assertEqual(all_my_smart_machines.__len__() + all_my_kvm_machines.__len__(), 0, 'VMs for this Owner exist')


        # John creates a first smartmachine and is pleased
        my_first_smart_machine = dc.create_smart_machine(owner=user_uuid, networks=[external_network_uuid],
                                                         package=package_small, image=smartmachine_image,
                                                         alias='my_first_smart_machine')
        self.assertIsNotNone(my_first_smart_machine.status())
        self.assertIsNotNone(my_first_smart_machine.uuid)

        # John wonders if the machine is created, so he retrieves it another time
        my_first_smartmachine_ = dc.get_smart_machine(uuid=my_first_smart_machine.uuid)
        self.assertEqual(my_first_smart_machine, my_first_smartmachine_)

        # John realizes he was to fast, his machine is still provisioning
        self.assertNotEqual(dc.STATE_RUNNING, my_first_smart_machine.status())

        # John decides to call a method that waits until the provisioning is done
        my_first_smart_machine.poll_until(status=dc.STATE_RUNNING)
        self.assertEqual(dc.STATE_RUNNING, my_first_smart_machine.status())

        # John sees his smart machine created and is happy for a moment
        all_my_vms = dc.list_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        all_my_smart_machines = dc.list_smart_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        self.assertEqual(all_my_vms.__len__(), 1)
        self.assertEqual(all_my_smart_machines.__len__(), 1)

        # John wants to provision another machine, this time he wants to try a KVM machine
        # John provisions his second machine
        my_first_kvm_machine = dc.create_kvm_machine(user_uuid, [external_network_uuid], package_small, kvm_image,
                                                     'my_first_kvm_machine')
        self.assertIsNotNone(my_first_kvm_machine)

        # John calls the wait method again and waits patiently
        self.assertNotEqual(my_first_kvm_machine.status(), dc.STATE_RUNNING)
        my_first_kvm_machine.poll_until(dc.STATE_RUNNING)
        self.assertEqual(my_first_kvm_machine.status(), dc.STATE_RUNNING)

        # John gets exited as he sees his second machine, this time a KVM machine as well
        all_my_vms = dc.list_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        all_my_kvm_machines = dc.list_kvm_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        self.assertEqual(all_my_vms.__len__(), 2)
        self.assertEqual(all_my_kvm_machines.__len__(), 1)

        # John wants to give his machines access to his private network
        my_first_kvm_machine.add_nic(network_uuid=my_network_uuid, ip=TestConfig.test_ip_1)

        # John grabs a coffee
        time.sleep(30) # FIXME: add_nic has no blocking method

        self.assertTrue(my_first_kvm_machine.is_attached_to_network(my_network_uuid))
        my_first_kvm_machine.refresh()
        my_first_kvm_machine.remove_nic(my_first_kvm_machine.nics[1].get('mac'))
        time.sleep(30)  # FIXME: add_nic has no blocking method
        my_first_kvm_machine.refresh()
        self.assertFalse(my_first_kvm_machine.is_attached_to_network(my_network_uuid))


        my_first_smart_machine.add_nic(network_uuid=my_network_uuid, ip=TestConfig.test_ip_2)
        time.sleep(30)
        self.assertTrue(my_first_smart_machine.is_attached_to_network(my_network_uuid))

        # John does a quick refresh
        my_first_smart_machine.refresh()

        # John wants to remove the external network from his machine again.
        my_first_smart_machine.remove_nic(my_first_smart_machine.nics[1].get('mac'))

        # John grabs another coffee
        time.sleep(30)

        self.assertFalse(my_first_smart_machine.is_attached_to_network(my_network_uuid))


        # John now gets tired, he did provision 2 servers after all.
        # He decides to remove the kvm machine first
        my_first_kvm_machine.delete()

        # John calls the method to wait until it is gone.
        self.assertNotEqual(my_first_kvm_machine.status(), dc.STATE_DESTROYED)
        my_first_kvm_machine.poll_until(dc.STATE_DESTROYED)
        self.assertEqual(my_first_kvm_machine.status(), dc.STATE_DESTROYED)

        # John grins as the kvm machine is destroyed. to be sure that it is gone for sure, he lists his vms
        # and only sees the smart machine remaining
        all_my_vms = dc.list_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        all_my_smart_machines = dc.list_smart_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        all_my_kvm_machines = dc.list_kvm_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        self.assertEqual(all_my_vms.__len__(), 1)
        self.assertEqual(all_my_smart_machines.__len__(), 1)
        self.assertEqual(all_my_kvm_machines.__len__(), 0)

        # John, with a tear in his eye, goes on to  destroy his beloved awesome smart machine.
        # goodbye sweet prince he whispers to himself
        my_first_smart_machine.delete()
        self.assertNotEqual(my_first_smart_machine.status(), dc.STATE_DESTROYED)
        my_first_smart_machine.poll_until(dc.STATE_DESTROYED)
        self.assertEqual(my_first_smart_machine.status(), dc.STATE_DESTROYED)


        # John realises what he has done and questions life and his very existence.
        # After a few moments of regret, he wants to be sure that all VMs are destroyed.
        all_my_vms = dc.list_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        all_my_smart_machines = dc.list_smart_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        all_my_kvm_machines = dc.list_kvm_machines(owner_uuid=user_uuid, state=dc.STATE_RUNNING)
        self.assertEqual(all_my_vms.__len__(), 0)
        self.assertEqual(all_my_smart_machines.__len__(), 0)
        self.assertEqual(all_my_kvm_machines.__len__(), 0)

        # John keeps on rampaging and deletes his john_net.
        my_network.delete()
        my_network = dc.get_network(uuid=my_network_uuid)
        self.assertIsNone(my_network)




        # John sees his work, two destroyed machines and decides to go to bed

