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

import json

import requests

from netaddr import IPNetwork

from .machine import SmartMachine, KVMMachine, Machine
from .network import Network
from .job import Job
from .package import Package


class DataCenter(object):
    APIS = ['sapi', 'vmapi', 'fwapi', 'imgapi', 'napi', 'papi', 'workflow']
    default_headers = {'Content-Type': 'application/json'}
    STATE_RUNNING = Machine.STATE_RUNNING
    STATE_FAILED = Machine.STATE_FAILED
    STATE_DESTROYED = Machine.STATE_DESTROYED
    STATE_PROVISIONING = Machine.STATE_PROVISIONING
    STATE_STOPPED = Machine.STATE_STOPPED
    TENANT_NET = '10.0.0.0/8'
    TENANT_NIC_TAG = 'customer'

    def request(self, method, api, path, headers=None, data=None, **kwargs):
        full_path = getattr(self, api) + path
        request_headers = {}
        request_headers.update(self.default_headers)
        if headers:
            request_headers.update(headers)
        jdata = None
        if data:
            jdata = json.dumps(data)

        resp = requests.request(method, full_path, headers=request_headers, data=jdata, **kwargs)
        if resp.content:
            if resp.headers['content-type'] == 'application/json':
                return (json.loads(resp.content), resp)
            else:
                return (resp.content, resp)
        else:
            return (None, resp)

    def get_ip_for_service(self, service):
        resp, _ = self.request('GET', 'sapi', '/services', params={'name': service})
        if not resp:
            raise EnvironmentError('Could not receive service information for service %s' % service)
        service = resp.pop()
        resp, _ = self.request('GET', 'sapi', '/instances', params={'service_uuid': service.get('uuid')})
        if not resp:
            raise EnvironmentError('Could not retrieve instance information for service uuid %s' % service.get('uuid'))
        instance = resp.pop()
        return instance.get('metadata').get('ADMIN_IP')

    def __init__(self, sapi, vmapi=None, fwapi=None, imgapi=None, napi=None, papi=None, workflow=None):
        self.sapi = 'http://' + sapi

        self.vmapi = 'http://' + (vmapi or self.get_ip_for_service('vmapi'))
        self.fwapi = 'http://' + (fwapi or self.get_ip_for_service('fwapi'))
        self.imgapi = 'http://' + (imgapi or self.get_ip_for_service('imgapi'))
        self.napi = 'http://' + (napi or self.get_ip_for_service('napi'))
        self.papi = 'http://' + (papi or self.get_ip_for_service('papi'))
        self.workflow = 'http://' + (workflow or self.get_ip_for_service('workflow'))

    def healthcheck_vmapi(self):
        health_data, _ = self.request('GET', 'vmapi', '/ping')

        return health_data.get('status') == 'OK'

    # FIXME: Code smell, duplication
    def list_smart_machines(self, owner_uuid=None, state=None):
        params = {'brand': 'joyent'}
        if owner_uuid:
            params.update({'owner_uuid': owner_uuid})
        if state:
            params.update({'state': state})
        raw_vms = self.__list_machines(params)
        return [SmartMachine(datacenter=self, data=raw_vm) for raw_vm in raw_vms]

    def list_machines(self, owner_uuid=None, state=None):

        smart_machines = self.list_smart_machines(owner_uuid, state)
        kvm_machines = self.list_kvm_machines(owner_uuid, state)
        return smart_machines + kvm_machines

    def list_kvm_machines(self, owner_uuid=None, state=None):
        params = {'brand': 'kvm'}
        if owner_uuid:
            params.update({'owner_uuid': owner_uuid})
        if state:
            params.update({'state': state})
        raw_vms = self.__list_machines(params)
        return [KVMMachine(datacenter=self, data=raw_vm) for raw_vm in raw_vms]

    def __list_machines(self, params):
        vms, _ = self.request('GET', 'vmapi', '/vms', params=params)
        return vms

    def create_smart_machine(self, owner, networks, package, image, alias=None, user_script=""):

        params = {'brand': 'joyent', 'owner_uuid': owner, 'networks': networks, 'billing_id': package,
                  'image_uuid': image}

        if alias:
            params.update({'alias': alias})

        metadata = {}
        if user_script:
            metadata.update({'user-script': user_script})

        raw_job_data = self.__create_machine(params)
        # TODO: error handling
        if not raw_job_data.get('vm_uuid'):
            raise Exception('Could not create SmartMachine')
        vm_uuid = raw_job_data.get('vm_uuid')
        vm = self.get_smart_machine(vm_uuid)
        vm.creation_job_uuid = raw_job_data.get('job_uuid')
        return vm

    def create_kvm_machine(self, owner, networks, package, image, alias=None, user_script=""):
        package_obj = Package(datacenter=self, uuid=package)

        params = {'brand': 'kvm',
                  'owner_uuid': owner,
                  'networks': networks,
                  'billing_id': package,
                  'disks': [{'image_uuid': image},
                            {'size': package_obj.quota}]}
        if alias:
            params.update({'alias': alias})
        metadata = {}
        if user_script:
            metadata.update({'user-script': user_script})

        raw_job_data = self.__create_machine(params)
        if not raw_job_data.get('vm_uuid'):
            raise Exception('Could not create KVM VM')
        vm_uuid = raw_job_data.get('vm_uuid')
        vm = self.get_kvm_machine(vm_uuid)
        vm.creation_job_uuid = raw_job_data.get('job_uuid')
        return vm

    def __create_machine(self, params):
        raw_job_data, _ = self.request('POST', 'vmapi', '/vms', data=params)
        return raw_job_data

    def get_smart_machine(self, uuid):
        return SmartMachine(self, uuid=uuid)

    def get_kvm_machine(self, uuid):
        return KVMMachine(self, uuid=uuid)

    def get_machine(self, uuid):
        machine = None
        # retrieve a Class Machine object to check its brand
        temp_machine = Machine(self, uuid=uuid)
        if temp_machine.brand == 'joyent':
            machine = SmartMachine(self, uuid=uuid)
        if temp_machine.brand == 'kvm':
            machine = KVMMachine(self, uuid=uuid)
        if machine:
            if machine.uuid:
                return machine

    def list_jobs(self):
        raw_job_data, _ = self.request('GET', 'workflow', '/jobs')
        return [Job(datacenter=self, data=job) for job in raw_job_data]

    def get_job(self, uuid):
        job = Job(self, uuid=uuid)
        if job.uuid:
            return job

    def list_packages(self):
        raw_package_data, _ = self.request('GET', 'papi', '/packages')
        return [Package(datacenter=self, data=package) for package in raw_package_data]

    def get_package(self, uuid):
        package = Package(self, uuid=uuid)
        if package.uuid:
            return package

    def list_networks(self):
        raw_network_data, _ = self.request('GET', 'napi', '/networks')
        return [Network(datacenter=self, data=network) for network in raw_network_data]

    def get_network(self, uuid):
        network = Network(self, uuid=uuid)
        if network.uuid:
            return network

    def create_network(self, name, owner_uuids, subnet, provision_start_ip, provision_end_ip, nic_tag,
                       gateway=None, vlan_id=0, resolvers=None, routes=None,  description=None):

        params = {'name': name,
                  'owner_uuids': owner_uuids,
                  'subnet': subnet,
                  'provision_start_ip': provision_start_ip,
                  'provision_end_ip': provision_end_ip,
                  'nic_tag': nic_tag,
                  'vlan_id': vlan_id}

        if gateway:
            params.update({'gateway': gateway})
        if resolvers:
            params.update({'resolvers': resolvers})
        if routes:
            params.update({'routes': routes})
        if description:
            params.update({'description': description})

        raw_job_data = self.__create_network(params)
        if not raw_job_data.get('uuid'):
            raise Exception('Could not create network')
        return Network(datacenter=self, data=raw_job_data)

    def create_smart_network(self, name, owner_uuids, mask_bits=24, description=None):
        vlan_id = self.next_free_vlan()
        subnet = self.next_free_network(mask_bits)
        net = IPNetwork(subnet)

        return self.create_network(name=name, owner_uuids=owner_uuids, subnet=subnet, provision_start_ip=net[1].__str__(),
                                   provision_end_ip=net[-2].__str__(), nic_tag=self.TENANT_NIC_TAG, vlan_id=vlan_id,
                                   description=description)


    def __create_network(self, params):
        raw_job_data, _ = self.request('POST', 'napi', '/networks', data=params)
        return raw_job_data

    def next_free_vlan(self):
        used_vlans = [network.vlan_id for network in self.list_networks()]
        for vlan in xrange(2, 4096):
            if not vlan in used_vlans:
                return vlan
        return None

    def next_free_network(self, mask_bits=24):

        used_subnets = [IPNetwork(network.subnet) for network in self.list_networks()]
        possible_subnets = IPNetwork(self.TENANT_NET).subnet(mask_bits)
        for candidate in possible_subnets:
            if not any([any([ip in subnet for ip in list(candidate)]) for subnet in used_subnets]):
                return candidate.__str__()
