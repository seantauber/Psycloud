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
		if r.ok:
			return r.json()
		else:
			throw_exception(r.json())

	def get_experiment_list(self):
		url = self.base_url + admin_endpoint['experiments']
		r = requests.get(url, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['experiments']
		else:
			throw_exception(r.json())

	def get_experiment(self, experiment_id):
		url = self.base_url + admin_endpoint['experiments'] + '/%s'%experiment_id
		r = requests.get(url, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['experiments']
		else:
			throw_exception(r.json())

	def delete_experiment(self, experiment_id):
		url = self.base_url + admin_endpoint['experiments'] + '/%s'%experiment_id
		r = requests.delete(url, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']
		else:
			throw_exception(r.json())

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
		if r.ok:
			return r.json()
		else:
			throw_exception(r.json())

	def get_coupons(self, experiment_id):
		url = self.base_url + admin_endpoint['coupons']%experiment_id
		r = requests.get(url, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['coupons']
		else:
			throw_exception(r.json())


class PsycloudClient():
	def __init__(self, base_url):
		self.base_url = base_url

	def register(self, experiment_id, registration_coupon=None):
		url = self.base_url + endpoint['register']%experiment_id
		if registration_coupon is not None:
			url = url + '/%s'%registration_coupon
		r = requests.post(url)
		if r.ok:
			return r.json()['result']['participant']
		else:
			throw_exception(r.json())

	def get_participant(self, participant_id):
		url = self.base_url + endpoint['participant']%participant_id
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['participant']
		else:
			throw_exception(r.json())

	def get_stimuli_list(self, participant_id):
		url = self.base_url + endpoint['stimuli']%participant_id
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['stimuli']
		else:
			throw_exception(r.json())

	def get_current_stimulus(self, participant_id):
		url = self.base_url + endpoint['stimuli']%participant_id + '/current'
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['stimuli']
		else:
			throw_exception(r.json())

	def get_stimulus(self, participant_id, stimulus_number):
		url = self.base_url + endpoint['stimuli']%participant_id + '/%s'%stimulus_number
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['stimuli']
		else:
			throw_exception(r.json())

	def increment_and_get_next_stimulus(self, participant_id):
		url = self.base_url + endpoint['stimuli']%participant_id + '/next'
		r = requests.put(url)
		if r.ok:
			return r.json()['result']['stimuli']
		else:
			throw_exception(r.json())




class BadRequest(Exception):
	pass
class UrlNotFound(Exception):
	pass
class UnexpectedError(Exception):
	pass
class Unauthorized(Exception):
	pass

def throw_exception(m):
	if m['status'] == 400:
		raise BadRequest(m['result'])
	elif m['status'] == 403:
		raise Unauthorized()
	elif m['status'] == 404:
		raise UrlNotFound()
	else:
		raise UnexpectedError(m['result'])