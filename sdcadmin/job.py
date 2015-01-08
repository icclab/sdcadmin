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


class Job(object):
    uuid = ''
    workflow = ''
    workflow_uuid = ''

    def __init__(self, datacenter, data=None, uuid=None):

        self.dc = datacenter

        if not data:
            if not uuid:
                raise ValueError('Must provide either data or uuid')
            data, _ = self.dc.request('GET', 'workflow', '/jobs/' + uuid)
        self._save(data)

    def _save(self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)

    def __eq__(self, other):
        if isinstance(other, Job):
            return self.uuid == other.uuid
        return False