# -*- encoding: utf-8 -*-
"""
    Configuration file
"""

# List of jobs to show in the dashboard
SIMPLE_JOBS = ['Job_example_1', 'Job_example_2']

# Job structure to let dashboard work
JOBS = {'Job_example_1': {'jenkins': 'Job_example_1'},
        'Job_example_2': {'jenkins': 'Job_example_2'}}

# Jenkins credentials
JENKINS_URL = 'http://jenkins.paradigmatecnologico.com'  # Jenkins url to connect
JENKINS_USER = 'example_user'  # Jenkins user to connect
JENKINS_PASSWORD = 'example_password'  # Jenkins password to connect
