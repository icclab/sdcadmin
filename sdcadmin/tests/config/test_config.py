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


class TestConfig(object):
    # @hn:
    # for service in sapi vmapi fwapi imgapi napi papi workflow;
    # do
    #   vmadm get $( sdc-vmname $service ) | json nics.0.ip
    # done
    sapi_ip = '10.0.0.26'
    vmapi_ip = '10.0.0.21'
    fwapi_ip = '10.0.0.20'
    imgapi_ip = '10.0.0.15'
    napi_ip = '10.0.0.4'
    papi_ip = '10.0.0.23'
    workflow_ip = '10.0.0.13'

    #@adminui: manual retrieval
    user_uuid = 'ca50e0a6-0f87-c911-fb01-e139514f760f'
    package_small = 'a8c2033d-e8eb-c17e-83ce-b10e36f1339b'
    package_big = '395ecfd6-3050-4082-ea25-9b51ad72873d'
    smartmachine_image = '859e9466-7ef4-11e4-b103-27886e7d9a7d'
    kvm_image = 'b1df4936-7a5c-11e4-98ed-dfe1fa3a813a'
    network_uuid = 'f27c02f1-5b4c-4ef1-b463-59c7e60f02e5'

