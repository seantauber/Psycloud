"""Psycloud Python Client"""
import requests
import json

admin_endpoint = {}
admin_endpoint['experiment_upload'] = '/psycloud/admin/api/experiments/upload_all_data'
admin_endpoint['experiment_data'] = '/psycloud/admin/api/experiments/%s/data'
admin_endpoint['experiments'] = '/psycloud/admin/api/experiments'
admin_endpoint['participants'] = '/psycloud/admin/api/experiments/%s/participants'
admin_endpoint['coupons'] = '/psycloud/admin/api/experiments/%s/coupons'

endpoint = {}
endpoint['register'] = '/psycloud/api/experiment/%s/register'
endpoint['participant'] = '/psycloud/api/participants/%s'
endpoint['stimuli'] = '/psycloud/api/participants/%s/stimuli'
endpoint['responses'] = '/psycloud/api/participants/%s/responses'
endpoint['data'] = '/psycloud/api/participants/%s/data'


class PsycloudAdminClient():
	def __init__(self, base_url, username, password):
		self.base_url = base_url
		self.username = username
		self.password = password

	def upload_data(self, data_dict=None, json_filename=None):
		url = self.base_url + admin_endpoint['experiment_upload']
		headers = {'content-type': 'application/json'}
		if data_dict is not None:
			data = data_dict
		elif json_filename is not None:
			f = open(json_filename, 'rb')
			data = json.load(f)
			f.close()
		r = requests.post(url, data=json.dumps(data), headers=headers, auth=(self.username, self.password))
		return r.json()

	def get_experiment_list(self):
		url = self.base_url + admin_endpoint['experiments']
		r = requests.get(url, auth=(self.username, self.password))
		r.raise_for_status()
		return r.json()['result']['experiments']

	def get_experiment(self, experiment_id):
		url = self.base_url + admin_endpoint['experiments'] + '/%s'%experiment_id
		r = requests.get(url, auth=(self.username, self.password))
		r.raise_for_status()
		return r.json()['result']['experiments']

	def delete_experiment(self, experiment_id):
		url = self.base_url + admin_endpoint['experiments'] + '/%s'%experiment_id
		r = requests.delete(url, auth=(self.username, self.password))
		r.raise_for_status()
		return True

	def save_coupons(self, experiment_id,  data_dict=None, json_filename=None):
		url = self.base_url + admin_endpoint['coupons']%experiment_id
		headers = {'content-type': 'application/json'}
		if data_dict is not None:
			data = data_dict
		elif json_filename is not None:
			f = open(json_filename, 'rb')
			data = json.load(f)
			f.close()
		r = requests.post(url, data=json.dumps(data), headers=headers, auth=(self.username, self.password))
		return r.json()

	def get_coupons(self, experiment_id):
		url = self.base_url + admin_endpoint['coupons']%experiment_id
		r = requests.get(url, auth=(self.username, self.password))
		r.raise_for_status()
		return r.json()['result']['coupons']


# TODO: Implement Psycloud Client
class PsycloudClient():
	def __init__(self, base_url):
		self.base_url = base_url



