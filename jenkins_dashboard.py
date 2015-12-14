# -*- encoding: utf-8 -*-
from flask import Flask, render_template, jsonify
from conf import SIMPLE_JOBS, JENKINS_URL, JENKINS_USER, JENKINS_PASSWORD
import requests
import json

app = Flask(__name__)


@app.route('/jenkins_dashboard')
def jenkins_dashboard():
    return render_template('jenkins_dashboard.html', simple_jobs=json.dumps(SIMPLE_JOBS))


@app.route('/data_project/<project>')
def data_project(project):
    jenkins = JenkinsInfo()
    jenkins_name = project
    num_build = jenkins.last_build(jenkins_name)
    status = jenkins.get_status(jenkins_name, num_build)

    result = {
        'project': jenkins_name,
        'build_num': jenkins.number_of_tests(jenkins_name, num_build),
        'last_execute_time': jenkins.last_build_time(jenkins_name, num_build),
        'code_coverage': jenkins.get_project_test_cover(jenkins_name, num_build),
        'status': get_color(status),
        'culprits': jenkins.get_culprits(jenkins_name, num_build)
    }
    return jsonify(**result)


def get_color(status):
    if status == 'SUCCESS':
        return '#07C40D'  # Verde
    elif status == 'UNSTABLE':
        return 'orange'
    elif status == 'BUILDING':
        return 'grey'
    else:
        return 'red'


class JenkinsInfo(object):

    def __init__(self):
        self.jenkins_url = JENKINS_URL
        self.jenkins_user = JENKINS_USER
        self.jenkins_password = JENKINS_PASSWORD
        self.s = requests.Session()
        self.s.auth = (self.jenkins_user, self.jenkins_password)

    def last_build(self, job):
        r = self.s.get('{}/job/{}/api/json'.format(self.jenkins_url, str(job)))
        return r.json()['lastBuild']['number']

    def get_status(self, job, build):
        r = self.s.get('{}/job/{}/{}/api/json'.format(self.jenkins_url, str(job), str(build)))
        if r.json()['building']:
            return 'BUILDING'
        result = r.json()['result']
        if result:
            return result
        return 'CORRUPTED'

    def get_culprits(self, job, build):
        r = self.s.get('{}/job/{}/{}/api/json'.format(self.jenkins_url, str(job), str(build)))
        culprits = ''
        if r:
            if r.json()['result'] != "SUCCESS":
                result = r.json()['culprits']
                culprits = str([str(elem['fullName']) for elem in result])
                culprits = culprits[1:-1]
        return culprits

    def last_build_time(self, job, build):
        r = self.s.get('{}/job/{}/{}/api/json'.format(self.jenkins_url, str(job), str(build)))
        ms = r.json()['duration']
        return ms/1000/60  # in minutes

    def get_project_test_cover(self, job, build):
        r = self.s.get('{}/job/{}/{}/cobertura/api/json?depth=2'.format(self.jenkins_url, str(job), str(build)))
        lines_cobertura = 0
        if r:
            lines_cobertura = r.json()['results']['elements'][3]['ratio']
        return lines_cobertura

    def number_of_tests(self, job, build):
        r = self.s.get('{}/job/{}/{}/api/json'.format(self.jenkins_url, str(job), str(build)))
        result = r.json()['actions']
        tests = [elem['totalCount'] for elem in result if 'totalCount' in elem.keys()]
        return tests[0] if tests else 0


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8077, debug=True)
