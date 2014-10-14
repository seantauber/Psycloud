from google.appengine.ext import ndb
from datetime import datetime
from uuid import uuid4
from base64 import urlsafe_b64encode

from custom_exceptions import DuplicateEntryError, ResourceError, DataFormatError


class Experiment(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	short_id = ndb.StringProperty()
	experiment_name = ndb.StringProperty()
	num_participants = ndb.IntegerProperty()

class Participant(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	short_id = ndb.StringProperty()
	conf_code = ndb.StringProperty()
	participant_index = ndb.IntegerProperty()
	status = ndb.StringProperty()
	start_time = ndb.DateTimeProperty()
	end_time = ndb.DateTimeProperty()	
	stimuli_count = ndb.IntegerProperty()
	max_number_stimuli = ndb.IntegerProperty()
	current_stimulus = ndb.IntegerProperty()
	registration_coupon = ndb.JsonProperty()
	details = ndb.JsonProperty()

class Stimulus(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	stimulus_index = ndb.IntegerProperty()
	variables = ndb.JsonProperty()
	stimulus_type = ndb.StringProperty()

class Response(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	stimulus_index = ndb.IntegerProperty()
	variables = ndb.JsonProperty()

class RegistrationCoupon(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	coupon_type = ndb.StringProperty()
	coupon_value = ndb.StringProperty()




class AdminDatastore():

	SHORT_CODE_LENGTH = 16

	def __init__(self):
		pass


	def create_experiment(self, experiment_name, num_participants, max_number_stimuli):
		'''
		Create a new experiment with the specified experiment_name.
		The new experiment contains num_participants participants, each
		with no stimuli and set to AVAILABLE status.
		'''
		experiment = Experiment(
			experiment_name=experiment_name,
			short_id=urlsafe_b64encode(str(uuid4()))[:self.SHORT_CODE_LENGTH],
			num_participants=num_participants)

		experiment_key = experiment.put()

		participant_entities = []
		for i in range(num_participants):
			participant_entities.append(
				Participant(
				parent=experiment_key,
				short_id=urlsafe_b64encode(str(uuid4()))[:self.SHORT_CODE_LENGTH],
				conf_code=urlsafe_b64encode(str(uuid4()))[:self.SHORT_CODE_LENGTH],
				participant_index=i,
				stimuli_count=0,
				current_stimulus=0,
				max_number_stimuli=max_number_stimuli,
				status='AVAILABLE'))
			
		participant_keys = ndb.put_multi(participant_entities)

		return experiment_key


	def create_experiment_from_data(self, experiment_data_dict):
		d = experiment_data_dict
		experiment = Experiment(
			experiment_name=d['experiment_name'],
			short_id=urlsafe_b64encode(str(uuid4()))[:self.SHORT_CODE_LENGTH],
			num_participants=d['num_participants'])
		
		experiment_key = experiment.put()

		participant_list = d['participants']
		participant_entities = []
		for p in participant_list:
			participant_entities.append(
				Participant(
				parent=experiment_key,
				short_id=urlsafe_b64encode(str(uuid4()))[:self.SHORT_CODE_LENGTH],
				conf_code=urlsafe_b64encode(str(uuid4()))[:self.SHORT_CODE_LENGTH],
				participant_index=p['participant_index'],
				stimuli_count=p['stimuli_count'],
				current_stimulus=0,
				max_number_stimuli=p['stimuli_count'],
				status='AVAILABLE'))
			
		participant_keys = ndb.put_multi(participant_entities)

		stimulus_entities = []
		for i,p in enumerate(participant_list):
			stimuli = p['stimuli']
			for s in stimuli:
				stimulus_entities.append(
					Stimulus(
					parent=participant_keys[i],
					stimulus_index=s['stimulus_index'],
					variables=s['variables'],
					stimulus_type=s['stimulus_type']))

		ndb.put_multi(stimulus_entities)

		return experiment_key


	def remove_experiment(self, experiment_id):

		experiment_key = self._key_from_urlsafe_id(experiment_id)

		experiment = experiment_key.get()
		experiment_name = experiment.experiment_name

		ndb.delete_multi(ndb.Query(ancestor=experiment_key).iter(keys_only = True))
		experiment_key.delete()
		return True


	def get_experiments(self, experiment_id=None):
		if experiment_id is None:
			q = ndb.Query(kind='Experiment')
			experiment_list = [dict( {'id':i.key.urlsafe()}.items() + i.to_dict().items() ) for i in q.iter()]
			return experiment_list
		else:
			experiment_key = self._key_from_urlsafe_id(experiment_id)
			experiment = experiment_key.get()
			return experiment.to_dict()


	def get_participants(self, experiment_id, keys_only=False, status_filter=None, get_data=False):

		experiment_key = self._key_from_urlsafe_id(experiment_id)

		if status_filter is None:
			q = Participant.query(ancestor=experiment_key).fetch(keys_only=keys_only)
		else:
			q = Participant.query(Participant.status == status_filter, ancestor=experiment_key).fetch(keys_only=keys_only)

		if keys_only:
			participants = [p.urlsafe() for p in q]
		else:
			participants = [p.to_dict() for p in q]
			for i,qi in enumerate(q):
				participants[i].update({'id':qi.key.urlsafe()})

		return participants


	def get_data(self, experiment_id, status_filter=None):

		experiment_key = self._key_from_urlsafe_id(experiment_id)

		if status_filter is None:
			q_part = Participant.query(ancestor=experiment_key)
		else:
			q_part = Participant.query(Participant.status == status_filter, ancestor=experiment_key)

		q_stim = Stimulus.query(ancestor=experiment_key)
		q_resp = Response.query(ancestor=experiment_key)

		#build participant hashtable
		participants = {}
		for p in q_part:
			participants[p.key.urlsafe()] = p.to_dict()
			participants[p.key.urlsafe()]['stimuli'] = []
			participants[p.key.urlsafe()]['responses'] = []

		#merge experiment data with participant data
		for s in q_stim:
			if participants.has_key(s.key.parent().urlsafe()):
				participants[s.key.parent().urlsafe()]['stimuli'].append(s.to_dict())
		for r in q_resp:
			if participants.has_key(r.key.parent().urlsafe()):
				participants[r.key.parent().urlsafe()]['responses'].append(r.to_dict())

		# Return a list of dictionaries, each containing all data for a participant
		return participants.values()


	def save_coupons(self, experiment_id, data):

		experiment_key = self._key_from_urlsafe_id(experiment_id)

		coupon_entities = [ RegistrationCoupon(
			parent=experiment_key,
			coupon_type=c['coupon_type'],
			coupon_value=c['coupon_value']) for c in data['coupons'] ]

		ndb.put_multi(coupon_entities)
		
		return [ coupon.to_dict() for coupon in coupon_entities ]


	def get_coupons(self, experiment_id):

		experiment_key = self._key_from_urlsafe_id(experiment_id)

		q = RegistrationCoupon.query(ancestor=experiment_key)
		coupon_list = [coupon.to_dict() for coupon in q.iter()]
		return coupon_list


	def _key_from_urlsafe_id(self, urlsafe_id):
		'''
		Utility function that creates an NDB key from a urlsafe entity id
		'''
		return ndb.Key(urlsafe=urlsafe_id)




class ClientDatastoreUtilityMixin():

	def __init__():
		pass

	def _lookup_experiment(self, short_id):

		q = Experiment.query(Experiment.short_id==short_id).fetch(keys_only=True)
		if len(q) != 0:
			experiment_key = q[0]
		else:
			raise LookupError('Experiment not found.')

		return experiment_key


	def _lookup_participant(self, short_id):

		q = Participant.query(Participant.short_id==short_id).fetch(keys_only=True)
		if len(q) != 0:
			participant_key = q[0]
		else:
			raise LookupError('Participant not found.')

		return participant_key

	def _lookup_participant_by_index(self, participant_index):

		q = Participant.query(Participant.participant_index==participant_index).fetch(keys_only=True)
		if len(q) != 0:
			participant_key = q[0]
		else:
			raise LookupError('Participant not found.')

		return participant_key


	def _get_participant_index_list_by_status(self, experiment_short_id, status_filter):

		experiment_key = self._lookup_experiment(experiment_short_id)
		q = Participant.query(Participant.status == status_filter, ancestor=experiment_key)
		participant_index_list = [p.participant_index for p in q.iter()]
		participant_index_list.sort()
		return participant_index_list


	def _available_participant_indices(self, experiment_short_id):
		return self._get_participant_index_list_by_status(experiment_short_id, 'AVAILABLE')

	def _active_participant_indices(self, experiment_short_id):
		return self._get_participant_index_list_by_status(experiment_short_id, 'ACTIVE')

	def _completed_participant_indices(self, experiment_short_id):
		return self._get_participant_index_list_by_status(experiment_short_id, 'COMPLETED')

	def _stalled_participant_indices(self, experiment_short_id):
		return self._get_participant_index_list_by_status(experiment_short_id, 'STALLED')


	def _get_participant_key(self, participant_short_id):
		'''
		Gets a participant key.
		'''
		participant_key = self._lookup_participant(participant_short_id)
		return participant_key


	def _get_participant(self, participant_short_id):
		'''
		Gets a participant.
		'''
		# Get the participant key and then load using the get method
		return self._get_participant_key(participant_short_id).get()


	def _get_participant_key_by_index(self, participant_index):
		'''
		Gets a participant key based on the participant index.
		'''
		participant_key = self._lookup_participant_by_index(participant_index)
		return participant_key


	def _get_participant_by_index(self, participant_index):
		'''
		Gets a participant based on the participant index.
		'''
		# Get the participant key and then load using the get method
		return self._get_participant_key_by_index(participant_index).get()


	def _update_participant_status(self, participant, new_status):
		'''
		Assumes participant is a Participant entity and updates its status.
		
		DOES NOT save the participant to the database.

		'''
		# Record the start time if this is the participant's initial activation
		if participant.status == 'AVAILABLE' and new_status == 'ACTIVE':
			participant.start_time = datetime.now()

		# Record the end time if the participant is complete
		elif participant.status == 'COMPLETED':
			participant.end_time = datetime.now()
		
		# Save the new status
		participant.status = new_status


	def _update_participant_registration_coupon(self, participant, coupon):
		'''
		Assumes participant is a Participant entity and updates its registration coupon.
		
		DOES NOT save the participant to the database.
		'''
		# set the participants registratino coupon and save the participant
		participant.registration_coupon = coupon


	def _register_coupon_to_experiment(self, experiment_key, coupon):
		'''
		Create a new coupon entity for the experiment
		'''
		# Create a new coupon for the experiment and save
		coupon = RegistrationCoupon(parent=experiment_key, coupon_value=coupon)
		coupon.put()





class ClientDatastore(ClientDatastoreUtilityMixin):
	
	VALID_STATUS_LIST = ['AVAILABLE', 'ACTIVE', 'COMPLETED', 'STALLED']
	SHORT_CODE_LENGTH = 16

	def __init__(self):
		pass


	def get_participant(self, participant_short_id):
		'''
		Returns a dictionary representation of a participant entity
		'''
		return self._get_participant(participant_short_id).to_dict()

	
	def register(self, experiment_short_id, registration_coupon=None):
		'''
		Activate and return a participant from the list of available participants.
		If registratin coupon is provided, it is registered with the experiment unless it
		has previously been registered... in which case an exception is raised.
		'''

		experiment_key = self._lookup_experiment(experiment_short_id)
		experiment = experiment_key.get()

		if registration_coupon is not None:
			q = RegistrationCoupon.query(RegistrationCoupon.coupon_value==registration_coupon, ancestor=experiment_key).fetch()
			if len(q) != 0:
				raise DuplicateEntryError('The registration coupon was already used.')

		# Get a list of available participant indices, and then take the first one
		available_list = self._available_participant_indices(experiment_short_id)
		if len(available_list):
			particpant_index = available_list[0]
		else:
			raise ResourceError('The experiment is full. Registration failed.')

		# Load the participant_key and participant
		participant_key = self._get_participant_key_by_index(particpant_index)
		participant = participant_key.get()

		# Set participant status to active
		self._update_participant_status(participant, 'ACTIVE')

		if registration_coupon is not None:
			# Set the participant registration coupon
			self._update_participant_registration_coupon(participant, registration_coupon)
			# Register and save the coupon with the experiment
			experiment_key = participant_key.parent()
			self._register_coupon_to_experiment(experiment_key, registration_coupon)

		# Save the participant entity
		participant.put()

		# Return the participant short_id
		return participant.short_id


	def get_status(self, participant_short_id):
		'''
		Returns the participant's current status.
		'''
		return self._get_participant(participant_short_id).status


	def get_max_number_stimuli(self, participant_short_id):
		'''
		Returns the maximum number of stimuli for the participant.
		'''
		return self._get_participant(participant_short_id).max_number_stimuli


	def get_current_stimulus(self, participant_short_id):
		'''
		Returns the current stimulus number for the participant.
		'''
		return self._get_participant(participant_short_id).current_stimulus


	def get_confirmation_code(self, participant_short_id):
		'''
		Returns the participant's confirmation code.
		'''
		return self._get_participant(participant_short_id).conf_code


	def set_current_stimulus(self, participant_short_id, current_stimulus):
		'''
		Sets the current stimulus number for the participant.
		'''

		# Load the participant
		participant = self._get_participant(participant_short_id)

		# Make sure index is in bounds
		if current_stimulus not in range(0, participant.max_number_stimuli):
			raise IndexError('Stimulus index out of range.')

		participant.current_stimulus = current_stimulus
		participant.put()
		return True

	
	def set_status(self, participant_short_id, new_status):
		'''
		Sets the participant's current status and moves the participant number to the
		appropriate status list for the experiment.
		'''

		# Make sure the new status is valid
		if new_status not in self.VALID_STATUS_LIST:
			raise ValueError('%s is not a valid status.' % new_status)

		# Load the participant
		participant = self._get_participant(participant_short_id)

		# Update the status
		self._update_participant_status(participant, new_status)

		# Save the participant
		participant.put()
		return True


	def set_registration_coupon(self, participant_short_id, coupon):
		'''
		Sets the participant's registration coupon and saves the coupon to list
		of all coupons for the experiment.
		'''
		# Load the participant
		participant = self._get_participant(participant_short_id)
		
		# set the participants registration coupon
		self._update_participant_registration_coupon(participant, coupon)

		# Save the participant
		participant.put()

		# Add the coupon to the experiment coupon list
		experiment_key = participant.parent
		self._register_coupon_to_experiment(experiment_key, coupon)
		return True


	def get_stimuli(self, participant_short_id, stimulus_number=None):
		'''
		Returns a list of stimuli.
		List contains all existing stimuli if stimulus_number is None.
		Otherwise list contains one stimulus specified by stimulus_number. 
		'''

		participant_key = self._get_participant_key(participant_short_id)
		
		if stimulus_number is not None:
			# Check if the stimulus number is out of range
			if stimulus_number not in range(0, participant_key.get().max_number_stimuli):
				raise IndexError('Stimulus index out of range.')

			# Query the database to get the stimulus
			q = Stimulus.query(Stimulus.stimulus_index == stimulus_number, ancestor=participant_key)

		else:
			# Query the database to get all stimuli
			q = ndb.Query(kind='Stimulus', ancestor=participant_key)

		# Convert the stimuli returned by the query to a list of dictionaries
		stimuli_list = [stimulus.to_dict() for stimulus in q.iter()]

		# Check if we are getting all stimuli or if the list of stimuli is not empty
		if stimulus_number is None or len(stimuli_list) > 0:
			# It's ok to return an empty list if we were getting all stimuli
			return stimuli_list
		else:
			# If we were getting a specific stimulus, then returning an empty list not allowed
			raise LookupError('Stimulus %s not found.' % stimulus_number)


	def get_responses(self, participant_short_id, stimulus_number=None):
		'''
		Returns a list of responses.
		List contains all existing responses if stimulus_number is None.
		Otherwise list contains one response specified by stimulus_number. 
		'''

		participant_key = self._get_participant_key(participant_short_id)
		
		if stimulus_number is not None:
			# Check if the stimulus number is out of range
			if stimulus_number not in range(0, participant_key.get().max_number_stimuli):
				raise IndexError('Stimulus index out of range.')

			# Query the database to get the response
			q = Response.query(Response.stimulus_index == stimulus_number, ancestor=participant_key)

		else:
			# Query the database to get all responses
			q = ndb.Query(kind='Response', ancestor=participant_key)

		# Convert the responses returned by the query to a list of dictionaries
		response_list = [response.to_dict() for response in q.iter()]

		# Check if we are getting all responses or if the list of responses is not empty
		if stimulus_number is None or len(response_list) > 0:
			# It's ok to return an empty list if we were getting all responses
			return response_list
		else:
			# If we were getting a specific response, then returning an empty list not allowed
			raise LookupError('Response %s not found.' % stimulus_number)


	def save_responses(self, participant_short_id, data):
		'''
		Saves a list of responses.

		Assumes data contains a list of responses, where each response is
		a dictionary with the following items:
		
		stimulus_index: the stimulus index for the response
		variables: a dictionary where each key-value pair is a variable name and value.
		
		Raises an exception if the stimulus_index of any of the responses already exists.
		'''

		# Check if the participant exists
		participant_key = self._get_participant_key(participant_short_id)

		# Get a list of the stimulus_index for each response to be saved
		new_response_indices = [response['stimulus_index'] for response in data]

		# Check if any of the stimulus indices are out of range
		participant = participant_key.get()
		for ind in new_response_indices:
			if not ind in range(0, participant.max_number_stimuli):
				raise IndexError('Stimulus index out of range.')

		# Check if any of the responses already exist
		q = Response.query(Response.stimulus_index.IN(new_response_indices), ancestor=participant_key)
		existing_responses = [r for r in q.iter()]
		if len(existing_responses) > 0:
			raise DuplicateEntryError('One or more responses with the specified stimulus index already exists. Nothing was saved.')

		# Create a list of new Response entities for datastore
		response_entities = []
		for response in data:
			response_entities.append(
				Response(
				parent=participant_key,
				stimulus_index=response['stimulus_index'],
				variables=response['variables']))

		# Save the list of responses to the datastore
		ndb.put_multi(response_entities)

		# Return a list of saved responses
		return [response.to_dict() for response in response_entities]


	def save_stimuli(self, participant_short_id, data):
		'''
		Saves a list of stimuli.

		Assumes data contains a list of stimuli, where each stimulus is
		a dictionary with the following items:
		
		stimulus_index: the stimulus index for the response
		variables: a dictionary where each key-value pair is a variable name and value.
		stimulus_type: a string label indicating the type of stimulus
		
		Raises an exception if the stimulus_index of any of the stimuli already exists.
		'''

		# Check if the participant exists
		participant_key = self._get_participant_key(participant_short_id)

		# Get a list of the stimulus_index for each stimulus to be saved
		new_stimulus_indices = [response['stimulus_index'] for response in data]

		# Check if any of the stimulus indices are out of range
		participant = participant_key.get()
		for ind in new_stimulus_indices:
			if not ind in range(0, participant.max_number_stimuli):
				raise IndexError('Stimulus index out of range.')

		# Check if any of the stimuli already exist
		q = Stimulus.query(Stimulus.stimulus_index.IN(new_stimulus_indices), ancestor=participant_key)
		existing_stimuli = [r for r in q.iter()]
		if len(existing_stimuli) > 0:
			raise DuplicateEntryError('One or more stimuli with the specified stimulus index already exists. Nothing was saved.')

		# Create a list of new Stimulus entities for datastore
		stimulus_entities = []
		for stimulus in data:
			stimulus_entities.append(
				Stimulus(
				parent=participant_key,
				stimulus_index=stimulus['stimulus_index'],
				variables=stimulus['variables'],
				stimulus_type=stimulus['stimulus_type']))

		# Save the list of stimuli to the datastore
		ndb.put_multi(stimulus_entities)

		# Return a list of saved stimuli
		return [stimulus.to_dict() for stimulus in stimulus_entities]



		