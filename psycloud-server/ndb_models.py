from google.appengine.ext import ndb

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