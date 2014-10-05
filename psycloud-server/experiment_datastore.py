from google.appengine.ext import ndb
from datetime import datetime
from uuid import uuid4
from base64 import urlsafe_b64encode

class Experiment(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	short_id = ndb.StringProperty()
	experiment_name = ndb.StringProperty()
	num_participants = ndb.IntegerProperty()
	available_participants = ndb.JsonProperty()
	active_participants = ndb.JsonProperty()
	completed_participants = ndb.JsonProperty()
	stalled_participants = ndb.JsonProperty()

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


class ExperimentDatastoreGoogleNDB():
	
	VALID_STATUS_LIST = ['AVAILABLE', 'ACTIVE', 'COMPLETED', 'STALLED']
	SHORT_CODE_LENGTH = 16

	def __init__(self):
		pass

	def lookup_experiment(self, short_id):
		try:
			q = Experiment.query(Experiment.short_id==short_id).fetch(keys_only=True)
			if len(q) != 0:
				experiment_key = q[0]
			else:
				print "DEBUG: Experiment lookup returned no results"
				return None
		except:
			print "DEBUG: Experiment lookup resulted in exception"
			raise
			return None
		return experiment_key

	def lookup_participant(self, short_id):
		try:
			q = Participant.query(Participant.short_id==short_id).fetch(keys_only=True)
			if len(q) != 0:
				participant_key = q[0]
			else:
				return None
		except:
			return None
		return participant_key

	def create_experiment(self, experiment_name, num_participants, max_number_stimuli):
		'''
		Create a new experiment with the specified experiment_name.
		The new experiment contains num_participants participants, each
		with no stimuli and set to AVAILABLE status.
		'''
		experiment = Experiment(
			experiment_name=experiment_name,
			short_id=urlsafe_b64encode(str(uuid4()))[:self.SHORT_CODE_LENGTH],
			num_participants=num_participants,
			available_participants=range(num_participants)[::-1],
			active_participants=[],
			completed_participants=[],
			stalled_participants=[])

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


	def upload_experiment_data(self, experiment_data_dict):
		d = experiment_data_dict
		experiment = Experiment(
			experiment_name=d['experiment_name'],
			short_id=urlsafe_b64encode(str(uuid4()))[:self.SHORT_CODE_LENGTH],
			num_participants=d['num_participants'],
			available_participants=range(d['num_participants'])[::-1],
			active_participants=[],
			completed_participants=[],
			stalled_participants=[])
		
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
				max_number_stimuli=p['stimuli_count']
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
		try:
			experiment_key = ndb.Key(urlsafe=experiment_id)
		except:
			return None

		experiment = experiment_key.get()
		experiment_name = experiment.experiment_name

		try:
			ndb.delete_multi(ndb.Query(ancestor=experiment_key).iter(keys_only = True))
			experiment_key.delete()
			return {'status':200, 'experiment_name':experiment_name}
		except:
			return {'status':400, 'e':"Unable to delete experiment"}

	def get_experiment_from_urlsafe_id(self, urlsafe_experiment_id):
		experiment_key = ndb.Key(urlsafe=urlsafe_experiment_id)
		experiment = experiment_key.get()
		return experiment

	def get_experiments(self, experiment_id=None):
		if experiment_id is None:
			q = ndb.Query(kind='Experiment')
			experiment_list = [dict( {'id':i.key.urlsafe()}.items() + i.to_dict().items() ) for i in q.iter()]
		else:
			try:
				experiment_key = ndb.Key(urlsafe=experiment_id)
				experiment = experiment_key.get()
				experiment_list = [ experiment.to_dict() ]
			except:
				return None
		return experiment_list

	def get_experiment_participants(self, experiment_id, keys_only=False, status_filter=None, get_data=False):
		try:
			experiment_key = ndb.Key(urlsafe=experiment_id)
		except:
			return None

		try:
			if status_filter is None:
				q = Participant.query(ancestor=experiment_key).fetch(keys_only=keys_only)
			else:
				q = Participant.query(Participant.status == status_filter, ancestor=experiment_key).fetch(keys_only=keys_only)
		except:
			return {'status':400, 'e':"Something went wrong"}

		if keys_only:
			participants = [p.urlsafe() for p in q]
		else:
			participants = [p.to_dict() for p in q]
			for i,qi in enumerate(q):
				participants[i].update({'id':qi.key.urlsafe()})

		return {'status':200, 'result':participants}

	
	def get_experiment_data(self, experiment_id, status_filter=None):
		try:
			experiment_key = ndb.Key(urlsafe=experiment_id)
		except:
			return None

		try:
			if status_filter is None:
				q_part = Participant.query(ancestor=experiment_key)
			else:
				q_part = Participant.query(Participant.status == status_filter, ancestor=experiment_key)
		except:
			return {'status':400, 'e':"Something went wrong while fetching participants"}

		try:
			q_stim = Stimulus.query(ancestor=experiment_key)
		except:
			return {'status':400, 'e':"Something went wrong while fetching stimuli"}
		try:
			q_resp = Response.query(ancestor=experiment_key)
		except:
			return {'status':400, 'e':"Something went wrong while fetching responses"}

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

		return {'status':200, 'result':participants.values()}



	def save_coupons(self, experiment_id, data):
		try:
			experiment_key = ndb.Key(urlsafe=experiment_id)
		except:
			return None

		try:
			for c in data['coupons']:
				coupon = RegistrationCoupon(
					parent=experiment_key,
					coupon_type=c['coupon_type'],
					coupon_value=c['coupon_value'])
				coupon.put()
		except:
			return {'status':400, 'e':"Something went wrong"}
		return {'status':200, 'result':self.get_coupons(experiment_id)}

	def get_coupons(self, experiment_id):
		try:
			experiment_key = ndb.Key(urlsafe=experiment_id)
		except:
			return None
		q = RegistrationCoupon.query(ancestor=experiment_key)
		coupon_list = [coupon.to_dict() for coupon in q.iter()]
		return coupon_list
	
	def register(self, experiment_short_id, registration_coupon=None):

		experiment_key = self.lookup_experiment(experiment_short_id)
		if experiment_key is None:
			return None
		else:
			experiment = experiment_key.get()

		if registration_coupon is not None:
			q = RegistrationCoupon.query(RegistrationCoupon.coupon_value==registration_coupon, ancestor=experiment_key).fetch()
			if len(q) != 0:
				return {'status':400, 'e':"Duplicate registration coupon"}

		try:
			particpant_index = experiment.available_participants.pop()
			experiment.put()
		except IndexError:
			return {'status':400, 'e':"No available participants"}

		try:
			q = Participant.query(Participant.participant_index==particpant_index, ancestor=experiment_key).fetch()
			participant = q[0]
			# participant = participant_key.get()

			participant.status = 'ACTIVE'
			participant.start_time = datetime.now()
			if registration_coupon is not None:
				participant.registration_coupon = registration_coupon
			participant.put()

			coupon = RegistrationCoupon(parent=experiment_key, coupon_value=registration_coupon)
			coupon.put()
			
			p = participant.to_dict()
			# p.update({'id':participant.key.urlsafe()})
		except:
			# Something went wrong. Undo participant activation
			experiment.available_participants.append(particpant_index)
			experiment.put()
			return {'status':400, 'e':"Unable to activate participant"}

		experiment.active_participants.append(particpant_index)
		experiment.put()

		return {'status':200, 'participant':p}


	def get_participant_key(self, participant_short_id):
		'''
		Gets a participant key.
		'''

		# Check if the participant exists
		participant_key = self.lookup_participant(participant_short_id)
		if participant_key is None:
			raise LookupError('Participant not found.')
		return participant_key

	def get_participant(self, participant_short_id):
		'''
		Gets a participant.
		'''
		# Get the participant key and then load using the get method
		return get_participant_key(participant_short_id).get()


	def get_status(self, participant_short_id):
		'''
		Returns the participant's current status.
		'''
		return self.get_participant(participant_short_id).status


	def get_max_number_stimuli(self, participant_short_id):
		'''
		Returns the maximum number of stimuli for the participant.
		'''
		return self.get_participant(participant_short_id).max_number_stimuli


	def get_current_stimulus(self, participant_short_id):
		'''
		Returns the current stimulus number for the participant.
		'''
		return self.get_participant(participant_short_id).current_stimulus


	def get_confirmation_code(self, participant_short_id):
		'''
		Returns the participant's confirmation code.
		'''
		return self.get_participant(participant_short_id).conf_code


	def set_current_stimulus(self, participant_short_id, current_stimulus):
		'''
		Sets the current stimulus number for the participant.
		'''

		# Load the participant
		participant = self.get_participant(participant_short_id)

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
		participant = self.get_participant(participant_short_id)

		# Record the start time if this is the participant's initial activation
		if participant.status == 'AVAILABLE' and new_status == 'ACTIVE':
			participant.start_time = datetime.now()

		# Record the end time if the participant is complete
		elif participant.status == 'COMPLETED':
			participant.end_time = datetime.now()
		
		# Save the new status
		participant.status = new_status
		participant.put()
		return True

		

	def get_stimuli(self, participant_short_id, stimulus_number=None):
		'''
		Returns a list of stimuli.
		List contains all existing stimuli if stimulus_number is None.
		Otherwise list contains one stimulus specified by stimulus_number. 
		'''

		participant_key = self.get_participant_key(participant_short_id)
		
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

		participant_key = self.get_participant_key(participant_short_id)
		
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


	# def increment_and_get_next_stimulus(self, participant_short_id):
	# 	participant_key = self.lookup_participant(participant_short_id)
	# 	if participant_key is None:
	# 		return None

	# 	participant = participant_key.get()

	# 	if participant.current_stimulus < (participant.stimuli_count - 1):
	# 		participant.current_stimulus += 1
	# 		participant.put()
	# 		# if participant.current_stimulus < participant.stimuli_count:
	# 		q = Stimulus.query(Stimulus.stimulus_index == participant.current_stimulus, ancestor=participant_key)
	# 		# else:
	# 			# return None
			
	# 		stimuli_list = [stimulus.to_dict() for stimulus in q.iter()]
	# 		return{'status':200, 'stimuli':stimuli_list}
		
	# 	else:
	# 		return{'status':400, 'e':"no more stimuli"}


	# def save_response(self, participant_short_id, data, current_only=False, stimulus_index=None):

	# 	participant_key = self.lookup_participant(participant_short_id)
	# 	if participant_key is None:
	# 		return None

	# 	valid_response, result = self.validate_response(data)
	# 	if not valid_response:
	# 		return result

	# 	participant = participant_key.get()
	# 	if current_only:
	# 		stimulus_index = participant.current_stimulus
	# 	elif not stimulus_index < participant.stimuli_count:
	# 			return {'status':400, 'e':"stimulus_index %s is out of bounds. Participant has %s stimuli."%(stimulus_index,participant.stimuli_count)}

	# 	q = Response.query(Response.stimulus_index == stimulus_index, ancestor=participant_key)
	# 	existing_responses = [r for r in q.iter()]
	# 	if len(existing_responses) > 0:
	# 		return{'status':400, 'e':"response already exists."}
	# 	else:
	# 		response = Response(parent=participant_key,
	# 		stimulus_index=stimulus_index,
	# 		variables=data['variables'])
	# 	response.put()
	# 	participant.last_completed_stimulus = participant.current_stimulus
	# 	participant.put()

	# 	return{'status':200, 'response':response.to_dict()}


	def save_responses(self, participant_short_id, data):
		'''
		** NEW VERSION **
		Saves a list of responses.

		Assumes data contains a list of responses, where each response is
		a dictionary with the following items:
		
		stimulus_index: the stimulus index for the response
		variables: a dictionary where each key-value pair is a variable name and value.
		
		Raises an exception if the stimulus_index of any of the responses already exists.
		'''

		# Check if the participant exists
		participant_key = self.lookup_participant(participant_short_id)
		if participant_key is None:
			raise LookupError('Participant not found.')

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
		** NEW VERSION **
		Saves a list of stimuli.

		Assumes data contains a list of stimuli, where each stimulus is
		a dictionary with the following items:
		
		stimulus_index: the stimulus index for the response
		variables: a dictionary where each key-value pair is a variable name and value.
		stimulus_type: a string label indicating the type of stimulus
		
		Raises an exception if the stimulus_index of any of the stimuli already exists.
		'''

		# Check if the participant exists
		participant_key = self.lookup_participant(participant_short_id)
		if participant_key is None:
			raise LookupError('Participant not found.')

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


	# def get_responses(self, participant_short_id, previous_only=False, stimulus_number=None):
	# 	participant_key = self.lookup_participant(participant_short_id)
	# 	if participant_key is None:
	# 		return None

	# 	if previous_only:
	# 		previous_stimuli_number = participant_key.get().current_stimulus - 1
	# 		if previous_stimuli_number >= 0:
	# 			q = Response.query(Response.stimulus_index == previous_stimuli_number, ancestor=participant_key).fetch()
	# 			if len(q) == 1:
	# 				response_list = [q[0].to_dict()]
	# 				return response_list
	# 			else:
	# 				return None
	# 		else:
	# 			return None
		
	# 	if stimulus_number is not None:
	# 		if stimulus_number >= 0 and stimulus_number < participant_key.get().stimuli_count:
	# 			q = Response.query(Response.stimulus_index == stimulus_number, ancestor=participant_key)
	# 		else:
	# 			return None
	# 	else:
	# 		q = ndb.Query(kind='Response', ancestor=participant_key)

	# 	response_list = [response.to_dict() for response in q.iter()]
	# 	return response_list

	def record_as_completed(self, participant_short_id):
		participant_key = self.lookup_participant(participant_short_id)
		if participant_key is None:
			return None

		participant = participant_key.get()
		if participant.status != 'ACTIVE':
			return{'status':400, 'e':"Participant not active."}

		response_list = self.get_responses(participant_short_id)

		if len(response_list) == participant.stimuli_count:
			participant.status = 'COMPLETED'
			participant.end_time = datetime.now()
			experiment = participant_key.parent().get()
			experiment.completed_participants.append(participant.participant_index)
			experiment.active_participants.remove(participant.participant_index)
			experiment.put()
			participant.put()
			return{'status':200, 'participant':participant.to_dict()}
		else:
			return{'status':400, 'e':"All responses have not been recorded for this participant."}

	# def validate_response_list(self, data):
	# 	pass

	def validate_response(self, data):
		if not 'variables' in data:
			return False, {'status':400, 'e':"response entry must contain a 'variables' field"}
		# if not type(data['variables']) == dict:
		# 	return False, {'status':400, 'e':"response['variables'] must be a dictionary of variables"}
		# for variable in data['variables']:
		# 	if not 'name' in variable:
		# 		return False, {'status':400, 'e':"variables must contain a 'name' field"}
		# 	if not 'value' in variable:
		# 		return False, {'status':400, 'e':"variables must contain a 'value' field"}
		return True, None
		

class DuplicateEntryError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class DataFormatError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

