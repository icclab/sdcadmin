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

    # vm
    #@adminui: manual retrieval
    user_uuid = '72f70341-b227-4051-befd-b0d5e1588a6d'
    package_small = 'b1abec1a-80e5-ea9e-e091-8f2d67feb252'
    package_big = '930896af-bf8c-48d4-885c-6573a94b1853'
    smartmachine_image = '62f148f8-6e84-11e4-82c5-efca60348b9f'
    kvm_image = '02dbab66-a70a-11e4-819b-b3dc41b361d6'
    external_network_uuid = 'f3d68d27-e311-491a-9c7f-d2a8d386e6e6'

    # network
    network_name='foo_net'
    nic_tag = 'customer'
    subnet='10.10.0.0/24'
    gateway='10.10.0.100'
    provision_start_ip='10.10.0.101'
    provision_end_ip='10.10.0.200'
    vlan_id='1337'
    resolvers=['8.8.8.8', '8.8.4.4']
    routes={'10.11.0.0/24': '10.10.0.50'}
    network_description='foo_net_desc'
    test_ip_1='10.10.0.121'
    test_ip_2='10.10.0.122'
    test_ip_3='10.10.0.123'
    test_ip_4='10.10.0.124'

