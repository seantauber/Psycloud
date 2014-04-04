from google.appengine.ext import ndb

class Experiment(ndb.Model):
	experiment_name = ndb.StringProperty()
	creation_time = ndb.DateTimeProperty(auto_now_add=True)
	num_participants = ndb.IntegerProperty()
	num_participants_active = ndb.IntegerProperty()
	num_participants_completed = ndb.IntegerProperty()

class Participant(ndb.Model):
	participant_index = ndb.IntegerProperty()
	status = ndb.StringProperty()
	start_time = ndb.DateTimeProperty()
	end_time = ndb.DateTimeProperty()
	
	stimuli_count = ndb.IntegerProperty()
	last_completed_stimuli = ndb.IntegerProperty()

class Stimuli(ndb.Model):
	stimuli_index = ndb.IntegerProperty()
	variables = ndb.JsonProperty()
	stimuli_type = ndb.StringProperty()

class Response(ndb.Model):
	variables = ndb.JsonProperty()


class ExperimentDatastoreGoogleNDB():
	
	def __init__(self):
		pass

	def create_experiment(self, experiment_data_dict):
		d = experiment_data_dict
		experiment = Experiment(
			experiment_name=d['experiment_id'],
			num_participants=d['num_participants'],
			num_participants_active=0,
			num_participants_completed=0)
		
		experiment_key = experiment.put()

		participant_list = d['participants']
		for p in participant_list:
			participant = Participant(
				parent=experiment_key,
				participant_index=p['participant_index'],
				stimuli_count=p['stimuli_count'],
				last_completed_stimuli=-1)
			
			participant_key = participant.put()

			stimuli_list = p['stimuli']
			for s in stimuli_list:
				stimuli = Stimuli(
					parent=participant_key,
					stimuli_index=s['stimuli_index'],
					variables=s['variables'],
					stimuli_type=s['html_template'])

				stimuli_key = stimuli.put()

				response = Response(parent=stimuli_key)

				response.put()

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



