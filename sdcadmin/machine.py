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
    STATE_RUNNING = 'running'
    STATE_FAILED = 'failed'
    STATE_DESTROYED = 'destroyed'
    STATE_PROVISIONING = 'provisioning'
    STATE_STOPPED = 'stopped'

    def __init__(self, datacenter, data=None, machine_uuid=None):

        self.dc = datacenter
        if not data:
            if not machine_uuid:
                raise ValueError('Must provide either data or machine_uuid')
            data = self.dc.request('GET', 'vmapi', '/vms/' + machine_uuid)
        self._save(data)

    def _save(self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)

    def status(self):
        status_data, _ = self.dc.request('GET', 'vmapi', '/statuses', params={'uuids': self.uuid})
        state = status_data.get(self.uuid)
        self.state = state
        return state

    def refresh(self):
        data, _ = self.dc.request('GET', 'vmapi', '/vms/' + self.uuid)
        self._save(data)

    def is_running(self):
        return self.status() == self.STATE_RUNNING

    def is_destroyed(self):
        return self.status() == self.STATE_DESTROYED

    def is_stopped(self):
        return self.status() == self.STATE_STOPPED


    def stop(self):
        raw_job_data, response = self.dc.request('POST', 'vmapi', '/vms/' + self.uuid + '?action=stop')
        response.raise_for_status()

    def start(self):
        raw_job_data, response = self.dc.request('POST', 'vmapi', '/vms/' + self.uuid + '?action=start')
        response.raise_for_status()

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

    def delete(self):
        raw_job_data, response = self.dc.request('DELETE', 'vmapi', '/vms/' + self.uuid)
        response.raise_for_status()


class SmartMachine(Machine):
    def __init__(self, datacenter, data, machine_uuid=None):
        super(SmartMachine, self).__init__(datacenter, data, machine_uuid)

    def __eq__(self, other):
        if isinstance(other, SmartMachine):
            return self.uuid == other.uuid
        return False


class KVMMachine(Machine):
    def __init__(self, datacenter, data, machine_uuid=None):
        super(KVMMachine, self).__init__(datacenter, data, machine_uuid)

    def __eq__(self, other):
        if isinstance(other, KVMMachine):
            return self.uuid == other.uuid
        return False
