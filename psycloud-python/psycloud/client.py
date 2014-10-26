"""Psycloud Python Client"""
import requests
import json


JSON_HEADER = {'content-type': 'application/json'}


admin_endpoint = {}
admin_endpoint['experiment_upload'] = '/psycloud/admin/api/experiments/upload_all_data'
admin_endpoint['experiment_data'] = '/psycloud/admin/api/experiments/%s/data'
admin_endpoint['experiments'] = '/psycloud/admin/api/experiments'
admin_endpoint['participants'] = '/psycloud/admin/api/experiments/%s/participants'
admin_endpoint['coupons'] = '/psycloud/admin/api/experiments/%s/coupons'


endpoint = {}
endpoint['participant'] = '/psycloud/api/participant/'
endpoint['current_status'] = '/psycloud/api/participant/%s/current_status/'
endpoint['confirmation_code'] = '/psycloud/api/participant/%s/confirmation_code/'
endpoint['stimuli'] = '/psycloud/api/participant/%s/stimuli/'
endpoint['stimulus'] = '/psycloud/api/participant/%s/stimuli/%s'
endpoint['responses'] = '/psycloud/api/participant/%s/responses/'
endpoint['response'] = '/psycloud/api/participant/%s/responses/%s'
endpoint['max_stimulus_count'] = '/psycloud/api/participant/%s/stimuli/max_count/'
endpoint['current_stimulus'] = '/psycloud/api/participant/%s/stimuli/current/'


class PsycloudAdminClient():
	def __init__(self, base_url, username, password, endpoint=admin_endpoint):
		self.base_url = base_url
		self.username = username
		self.password = password
		self.endpoint = endpoint

	def create_experiment(self, experiment_name, num_participants, max_number_stimuli):
		url = self.base_url + self.endpoint['experiments']
		data = {
		'experiment_name': experiment_name,
		'num_participants': num_participants,
		'max_number_stimuli': max_number_stimuli
		}
		r = requests.post(url, data=json.dumps(data), headers=JSON_HEADER, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['experiment_id']
		else:
			raise Exception(r.text)

	def create_iterated_experiment(self, experiment_name, num_participants, config):
		url = self.base_url + self.endpoint['experiments']
		data = {
		'experiment_type': 'iterated',
		'experiment_name': experiment_name,
		'num_participants': num_participants,
		'config': config
		}
		r = requests.post(url, data=json.dumps(data), headers=JSON_HEADER, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['experiment_id']
		else:
			raise Exception(r.text)

	def upload_data(self, data_dict=None, json_filename=None):
		url = self.base_url + self.endpoint['experiment_upload']
		if data_dict is not None:
			data = data_dict
		elif json_filename is not None:
			f = open(json_filename, 'rb')
			data = json.load(f)
			f.close()
		r = requests.post(url, data=json.dumps(data), headers=JSON_HEADER, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['experiment_id']
		else:
			raise Exception(r.text)

	def get_experiment_list(self):
		url = self.base_url + self.endpoint['experiments']
		r = requests.get(url, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['experiments']
		else:
			raise Exception(r.text)

	def get_experiment(self, experiment_id):
		url = self.base_url + self.endpoint['experiments'] + '/%s'%experiment_id
		r = requests.get(url, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['experiment']
		else:
			raise Exception(r.text)

	def delete_experiment(self, experiment_id):
		url = self.base_url + self.endpoint['experiments'] + '/%s'%experiment_id
		r = requests.delete(url, auth=(self.username, self.password))
		if r.ok:
			return True
		else:
			raise Exception(r.text)

	def save_coupons(self, experiment_id,  data_dict=None, json_filename=None):
		url = self.base_url + self.endpoint['coupons']%experiment_id
		if data_dict is not None:
			data = data_dict
		elif json_filename is not None:
			f = open(json_filename, 'rb')
			data = json.load(f)
			f.close()
		r = requests.post(url, data=json.dumps(data), headers=JSON_HEADER, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['coupons']
		else:
			raise Exception(r.text)

	def get_coupons(self, experiment_id):
		url = self.base_url + self.endpoint['coupons']%experiment_id
		r = requests.get(url, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['coupons']
		else:
			raise Exception(r.text)

	def get_participant_list(self, experiment_id, keys_only=False, status=None):
		url = self.base_url + self.endpoint['participants']%experiment_id
		d = {}
		if keys_only:
			d.update({'keys_only':True})
		if status is not None:
			d.update({'status':status})
		r = requests.get(url, params=d, auth=(self.username, self.password))
		if r.ok:
			return r.json()['result']['participants']
		else:
			raise Exception(r.text)

	def get_experiment_data(self, experiment_id, status=None):
		url = self.base_url + self.endpoint['experiment_data']%experiment_id
		d = {}
		if status is not None:
			d.update({'status':status})
		r = requests.get(url, params=d, auth=(self.username, self.password), timeout=60.)
		if r.ok:
			return r.json()['result']['participants']
		else:
			raise Exception(r.text)




class PsycloudClient():

	def __init__(self, base_url, endpoint=endpoint):
		self.base_url = base_url
		self.endpoint = endpoint

	def register(self, experiment_id, registration_coupon=None):
		url = self.base_url + self.endpoint['participant']
		data = {'experiment_id': experiment_id, 'registration_coupon': registration_coupon}
		r = requests.post(url, data=json.dumps(data), headers=JSON_HEADER)
		if r.ok:
			return r.json()['result']['participant_id']
		else:
			raise Exception(r.text)

	def get_stimuli(self, participant_id):
		url = self.base_url + self.endpoint['stimuli'] % participant_id
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['stimuli']
		else:
			raise Exception(r.text)

	def get_stimulus(self, participant_id, stimulus_index):
		url = self.base_url + self.endpoint['stimulus'] % (participant_id, stimulus_index)
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['stimulus']
		else:
			raise Exception(r.text)

	def get_responses(self, participant_id):
		url = self.base_url + self.endpoint['responses'] % participant_id
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['responses']
		else:
			raise Exception(r.text)

	def get_response(self, participant_id, stimulus_index):
		url = self.base_url + self.endpoint['response'] % (participant_id, stimulus_index)
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['response']
		else:
			raise Exception(r.text)

	def get_current_stimulus(self, participant_id):
		url = self.base_url + self.endpoint['current_stimulus'] % participant_id
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['stimulus_index']
		else:
			raise Exception(r.text)

	def get_current_status(self, participant_id):
		url = self.base_url + self.endpoint['current_status'] % participant_id
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['current_status']
		else:
			raise Exception(r.text)

	def get_max_stimulus_count(self, participant_id):
		url = self.base_url + self.endpoint['max_stimulus_count'] % participant_id
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['max_count']
		else:
			raise Exception(r.text)

	def get_confirmation_code(self, participant_id):
		url = self.base_url + self.endpoint['confirmation_code'] % participant_id
		r = requests.get(url)
		if r.ok:
			return r.json()['result']['confirmation_code']
		else:
			raise Exception(r.text)


	def save_response(self, participant_id, stimulus_index, response):
		url = self.base_url + self.endpoint['response'] % (participant_id, stimulus_index)
		r = requests.post(url, data=json.dumps(response), headers=JSON_HEADER)
		if r.ok:
			return r.json()['result']['response']
		else:
			raise Exception(r.text)

	def save_responses(self, participant_id, response_list):
		url = self.base_url + self.endpoint['responses'] % participant_id
		r = requests.post(url, data=json.dumps(response_list), headers=JSON_HEADER)
		if r.ok:
			return r.json()['result']['responses']
		else:
			raise Exception(r.text)

	def save_stimulus(self, participant_id, stimulus_index, stimulus):
		url = self.base_url + self.endpoint['stimulus'] % (participant_id, stimulus_index)
		r = requests.post(url, data=json.dumps(stimulus), headers=JSON_HEADER)
		if r.ok:
			return r.json()['result']['stimulus']
		else:
			raise Exception(r.text)

	def save_stimuli(self, participant_id, stimulus_list):
		url = self.base_url + self.endpoint['stimuli'] % participant_id
		r = requests.post(url, data=json.dumps(stimulus_list), headers=JSON_HEADER)
		if r.ok:
			return r.json()['result']['stimuli']
		else:
			raise Exception(r.text)

	def set_current_stimulus(self, participant_id, stimulus_index):
		url = self.base_url + self.endpoint['current_stimulus'] % participant_id
		data = {'stimulus_index': stimulus_index}
		r = requests.put(url, data=json.dumps(data), headers=JSON_HEADER)
		if r.ok:
			return True
		else:
			raise Exception(r.text)

	def set_current_status(self, participant_id, status):
		url = self.base_url + self.endpoint['current_status'] % participant_id
		data = {'current_status': status}
		r = requests.put(url, data=json.dumps(data), headers=JSON_HEADER)
		if r.ok:
			return True
		else:
			raise Exception(r.text)





