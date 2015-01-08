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

from sdcadmin.job import Job
from sdcadmin.datacenter import DataCenter
from sdcadmin.tests.config.test_config import TestConfig


class TestJob(unittest.TestCase):
    def verify_job_object(self, job):
        self.assertIsInstance(job, Job)
        self.assertIsNotNone(job.uuid)
        self.assertIsNotNone(job.workflow)
        self.assertIsNotNone(job.workflow_uuid)

    def setUp(self):
        self.config = TestConfig()
        self.dc = DataCenter(sapi=self.config.sapi_ip)

    def test_retrieve_all_jobs(self):
        all_jobs = self.dc.list_jobs()

        self.assertNotEqual(0, all_jobs.__len__())
        self.assertIsInstance(all_jobs, list)
        for job in all_jobs:
            self.assertIsInstance(job, Job)

    def test_create_job_from_raw_data(self):
        all_jobs = self.dc.list_jobs()
        job_uuid = all_jobs.pop().uuid
        raw_job_data, _ = self.dc.request('GET', 'workflow', '/jobs/' + job_uuid)
        my_job = Job(datacenter=self.dc, data=raw_job_data)
        self.verify_job_object(my_job)

    def test_create_job_from_uuid(self):
        all_jobs = self.dc.list_jobs()
        job_uuid = all_jobs.pop().uuid
        my_job = Job(datacenter=self.dc, uuid=job_uuid)
        self.verify_job_object(my_job)

    def test_retrieve_job_by_id(self):
        all_jobs = self.dc.list_jobs()
        test_job = all_jobs.pop()
        test_job_uuid = test_job.uuid
        verify_job = self.dc.get_job(uuid=test_job_uuid)
        self.assertEqual(test_job, verify_job)