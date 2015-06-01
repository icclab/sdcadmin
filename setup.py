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

from setuptools import setup

setup(
    name='sdcadmin',
    version='0.3',
    packages=['sdcadmin', 'sdcadmin.tests', 'sdcadmin.tests.config'],
    url='https://github.com/icclab/sdcadmin',
    license='Apache License, Version 2.0',
    author='ernm',
    author_email='ernm@zhaw.ch',
    description='API wrapper for the SDC APIs on the admin network',
    install_requires=[
        'requests>=2.5.1',
        'netaddr>=0.7.12'
    ]
)
