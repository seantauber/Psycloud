from google.appengine.ext import ndb

class Experiment(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	experiment_name = ndb.StringProperty()
	num_participants = ndb.IntegerProperty()
	available_participants = ndb.JsonProperty()
	active_participants = ndb.JsonProperty()
	completed_participants = ndb.JsonProperty()
	stalled_participants = ndb.JsonProperty()

class Participant(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	participant_index = ndb.IntegerProperty()
	status = ndb.StringProperty()
	start_time = ndb.DateTimeProperty()
	end_time = ndb.DateTimeProperty()	
	stimuli_count = ndb.IntegerProperty()
	current_stimulus = ndb.IntegerProperty()

class Stimulus(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	stimulus_index = ndb.IntegerProperty()
	variables = ndb.JsonProperty()
	stimulus_type = ndb.StringProperty()

class Response(ndb.Model):
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	stimulus_index = ndb.IntegerProperty()
	variables = ndb.JsonProperty()


class ExperimentDatastoreGoogleNDB():
	
	def __init__(self):
		pass

	def upload_experiment_data(self, experiment_data_dict):
		d = experiment_data_dict
		experiment = Experiment(
			experiment_name=d['experiment_id'],
			num_participants=d['num_participants'],
			available_participants=range(d['num_participants']),
			active_participants=[],
			completed_participants=[],
			stalled_participants=[])
		
		experiment_key = experiment.put()

		participant_list = d['participants']
		for p in participant_list:
			participant = Participant(
				parent=experiment_key,
				participant_index=p['participant_index'],
				stimuli_count=p['stimuli_count'],
				current_stimulus=0,
				status='AVAILABLE')
			
			participant_key = participant.put()

			stimuli_list = p['stimuli']
			for s in stimuli_list:
				stimulus = Stimulus(
					parent=participant_key,
					stimulus_index=s['stimulus_index'],
					variables=s['variables'],
					stimulus_type=s['html_template'])

				stimulus_key = stimulus.put()

				# response = Response(parent=stimulus_key)

				# response.put()

		return experiment_key

	def remove_experiment(self, urlsafe_experiment_id):
		experiment_key = ndb.Key(urlsafe=urlsafe_experiment_id)
		try:
			ndb.delete_multi(ndb.Query(ancestor=experiment_key).iter(keys_only = True))
			experiment_key.delete()
			return True
		except:
			return False

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



	def get_participant(self, participant_id):
		try:
			participant_key = ndb.Key(urlsafe=participant_id)
		except:
			return None
		participant = participant_key.get()
		if participant is not None:
			return participant.to_dict()
		else:
			return None

	def get_stimuli(self, participant_id, current_only=False, stimulus_number=None):
		try:
			participant_key = ndb.Key(urlsafe=participant_id)
		except:
			return None

		if current_only:
			stimulus_number = participant_key.get().current_stimulus
		
		if stimulus_number is not None:
			if stimulus_number >= 0 and stimulus_number < participant_key.get().stimuli_count:
				q = Stimulus.query(Stimulus.stimulus_index == stimulus_number, ancestor=participant_key)
			else:
				return None
		else:
			q = ndb.Query(kind='Stimulus', ancestor=participant_key)

		stimuli_list = [stimulus.to_dict() for stimulus in q.iter()]
		return stimuli_list

	def increment_and_get_next_stimulus(self, participant_id):
		try:
			participant_key = ndb.Key(urlsafe=participant_id)
		except:
			return None

		participant = participant_key.get()

		if participant.current_stimulus < (participant.stimuli_count - 1):
			participant.current_stimulus += 1
			participant.put()
			# if participant.current_stimulus < participant.stimuli_count:
			q = Stimulus.query(Stimulus.stimulus_index == participant.current_stimulus, ancestor=participant_key)
			# else:
				# return None
			
			stimuli_list = [stimulus.to_dict() for stimulus in q.iter()]
			return{'status':200, 'stimuli':stimuli_list}
		
		else:
			return{'status':400, 'e':"no more stimuli"}

	def save_response(self, participant_id, data, current_only=False, stimulus_index=None):

		try:
			participant_key = ndb.Key(urlsafe=participant_id)
		except:
			return None

		valid_response, result = self.validate_response(data)
		if not valid_response:
			return result

		participant = participant_key.get()
		if current_only:
			stimulus_index = participant.current_stimulus
		elif not stimulus_index < participant.stimuli_count:
				return {'status':400, 'e':"stimulus_index %s is out of bounds. Participant has %s stimuli."%(stimulus_index,participant.stimuli_count)}

		q = Response.query(Response.stimulus_index == stimulus_index, ancestor=participant_key)
		existing_responses = [r for r in q.iter()]
		if len(existing_responses) > 0:
			return{'status':400, 'e':"response already exists."}
		else:
			response = Response(parent=participant_key,
			stimulus_index=stimulus_index,
			variables=data['variables'])
		response.put()
		participant.last_completed_stimulus = participant.current_stimulus
		participant.put()

		return{'status':200, 'response':response.to_dict()}

	def validate_response_list(self, data):
		pass

	def validate_response(self, data):
		if not 'variables' in data:
			return False, {'status':400, 'e':"response entry must contain a 'variables' field"}
		if not type(data['variables']) == list:
			return False, {'status':400, 'e':"response['variables'] must be a list of variables"}
		for variable in data['variables']:
			if not 'name' in variable:
				return False, {'status':400, 'e':"variables must contain a 'name' field"}
			if not 'value' in variable:
				return False, {'status':400, 'e':"variables must contain a 'value' field"}
		return True, None
		



