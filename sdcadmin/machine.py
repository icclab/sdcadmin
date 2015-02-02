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

import time


class Machine(object):

    uuid = ''
    brand = ''
    nics = ''

    api = 'vmapi'
    base_url = '/vms/'
    identifier_field = 'uuid'

    STATE_RUNNING = 'running'
    STATE_FAILED = 'failed'
    STATE_DESTROYED = 'destroyed'
    STATE_PROVISIONING = 'provisioning'
    STATE_STOPPED = 'stopped'

    def __init__(self, datacenter, data=None, uuid=None):

        self.dc = datacenter

        if not data:
            if not uuid:
                raise Exception('Must pass either data or uuid')
            data, response = self.dc.request('GET', self.api, self.base_url + uuid)
            if not data.get(self.identifier_field):
                return
        self._save(data)

    def _save(self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)

    def url(self):
        return self.base_url + self.uuid

    def status(self):
        status_data, _ = self.dc.request('GET', self.api, '/statuses', params={'uuids': self.uuid})
        state = status_data.get(self.uuid)
        self.state = state
        return state

    def refresh(self):
        data, _ = self.dc.request('GET', self.api, self.url())
        self._save(data)

    def is_running(self):
        return self.status() == self.STATE_RUNNING

    def is_destroyed(self):
        return self.status() == self.STATE_DESTROYED

    def is_stopped(self):
        return self.status() == self.STATE_STOPPED

    def is_attached_to_network(self, network_uuid):
        self.refresh()
        return [True for nic in self.nics if nic.get('network_uuid') == network_uuid].__len__()>=1

    def stop(self):
        raw_job_data, response = self.dc.request('POST', self.api, self.url() + '?action=stop')
        response.raise_for_status()

    def start(self):
        raw_job_data, response = self.dc.request('POST', self.api, self.url() + '?action=start')
        response.raise_for_status()

    def delete(self):
        raw_job_data, response = self.dc.request('DELETE', self.api, self.url())
        response.raise_for_status()

    def add_nic(self, network_uuid, ip=None):
        params = { 'networks' : [{'uuid': network_uuid}] }
        if ip:
            params = { 'networks' : [{'uuid': network_uuid, 'ip': ip}] }
        raw_job_data, response = self.dc.request('POST', self.api, self.url() + '?action=add_nics', data=params)
        if not raw_job_data.get('vm_uuid'):
            raise Exception('Could not attach nic to vm')
        self.refresh()

    def remove_nic(self, mac_address):
        self.refresh()
        nics = [ nic for nic in self.nics if nic['mac'] == mac_address]
        if nics.__len__() == 0:
            raise Exception('nic with provided mac address not found')
        network_uuid = nics[0].get('network_uuid')

        params = { 'macs' : [mac_address] }
        raw_job_data, response = self.dc.request('POST', self.api, self.url() + '?action=remove_nics', data=params)
        if not raw_job_data.get('vm_uuid'):
            raise Exception('Could not remove nic from vm')
        self.refresh()


    def poll_until(self, status):
        while not self.status() == status:
            if self.state == self.STATE_FAILED:
                raise Exception('Machine in failed state')
            time.sleep(1)
        self.state = status
        return

    def poll_while(self, status):
        while self.status() == status:
            if self.state == self.STATE_FAILED:
                raise Exception('Machine in failed state')
            time.sleep(1)
        self.state = status
        return




class SmartMachine(Machine):
    def __init__(self, datacenter, data=None, uuid=None):
        super(SmartMachine, self).__init__(datacenter, data, uuid)

    def __eq__(self, other):
        if isinstance(other, SmartMachine):
            return self.uuid == other.uuid
        return False


class KVMMachine(Machine):
    def __init__(self, datacenter, data=None, uuid=None):
        super(KVMMachine, self).__init__(datacenter, data, uuid)

    def __eq__(self, other):
        if isinstance(other, KVMMachine):
            return self.uuid == other.uuid
        return False
