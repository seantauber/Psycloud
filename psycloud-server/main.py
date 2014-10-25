"""`main` is the top level module for the Flask application."""

from experiment_datastore_google import AdminDatastore, ClientDatastore, IteratedClientDatastore

admin_datastore = AdminDatastore()
client_datastore = ClientDatastore()
iterated_client_datastore = IteratedClientDatastore()

from flask import Flask, jsonify, abort, request, make_response, url_for, render_template
from flask.ext.httpauth import HTTPBasicAuth
 
app = Flask(__name__, static_url_path = "")
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
auth = HTTPBasicAuth()
dashauth = HTTPBasicAuth()



#######################################################################################
#######################################################################################
# 
# ADMINISTRATOR API 
# 
#######################################################################################
#######################################################################################

# Upload a Json file that contains the complete experiment with participants and stimuli
@app.route('/psycloud/admin/api/experiments/upload_all_data',
	methods=['POST'])
@auth.login_required
def upload_experiment_data():
	data = request.get_json()
	try:
		experiment_key = admin_datastore.create_experiment_from_data(data)
		return valid_request('experiment_id', experiment_key.urlsafe())
	except Exception, e:
		raise
		return bad_request(str(e))

# Delete an experiment and all of its data
@app.route('/psycloud/admin/api/experiments/<experiment_id>',
	methods=['DELETE'])
@auth.login_required
def remove_experiment(experiment_id):
	try:
		admin_datastore.remove_experiment(experiment_id)
		return valid_request('deleted experiment', experiment_id)
	except Exception, e:
		raise
		return bad_request(str(e))


# Retrieve all experiment data
@app.route('/psycloud/admin/api/experiments/<experiment_id>/data',
	methods=['GET'])
@auth.login_required
def get_experiment_data(experiment_id):
	status_filter = None
	args = request.args
	if 'status' in args:
		status_filter = args['status']
	try:
		participant_list = admin_datastore.get_data(experiment_id, status_filter=status_filter)
		return valid_request('participants', participant_list)
	except Exception, e:
		raise
		return bad_request(str(e))



def create_iterated_experiment(data):

	experiment_name = data['experiment_name']
	num_participants = data['num_participants']
	config = data['config']

	try:
		experiment_key = admin_datastore.create_iterated_experiment(experiment_name,
			num_participants, config)
		return valid_request('experiment_id', experiment_key.urlsafe())
	except Exception, e:
		raise
		return bad_request(str(e))


# Create a new experiment
@app.route('/psycloud/admin/api/experiments',
	methods=['POST'])
@auth.login_required
def create_experiment():
	
	data = request.get_json()

	if 'experiment_type' in data:
		if data['experiment_type'] == 'iterated':
			return create_iterated_experiment(data)

	experiment_name = data['experiment_name']
	num_participants = data['num_participants']
	max_number_stimuli = data['max_number_stimuli']
	try:
		experiment_key = admin_datastore.create_experiment(experiment_name,
			num_participants, max_number_stimuli)
		return valid_request('experiment_id', experiment_key.urlsafe())
	except Exception, e:
		raise
		return bad_request(str(e))


# Retrieve a list of experiments
@app.route('/psycloud/admin/api/experiments',
	methods=['GET'])
@auth.login_required
def get_experiment_list():
	try:
		experiment_list = admin_datastore.get_experiments()
		return valid_request('experiments', experiment_list)
	except Exception, e:
		raise
		return bad_request(str(e))

# Retrieve an experiment
@app.route('/psycloud/admin/api/experiments/<experiment_id>',
	methods=['GET'])
@auth.login_required
def get_experiment(experiment_id):
	try:
		experiment = datastore.get_experiments(experiment_id=experiment_id)
		return valid_request('experiment', experiment)
	except Exception, e:
		raise
		return bad_request(str(e))

# Modify an experiment
@app.route('/psycloud/admin/api/experiments/<experiment_id>',
	methods=['PUT'])
@auth.login_required
def modify_experiment(experiment_id):
	pass

# Retrieve a list of participants
@app.route('/psycloud/admin/api/experiments/<experiment_id>/participants',
	methods=['GET'])
@auth.login_required
def get_participant_list(experiment_id):
	keys_only = False
	status_filter = None
	args = request.args
	if 'keys_only' in args:
		keys_only = bool(args['keys_only'])
	if 'status' in args:
		status_filter = args['status']

	try:
		participant_list = admin_datastore.get_participants(experiment_id, keys_only=keys_only, status_filter=status_filter)
		return valid_request('participants', participant_list)
	except Exception, e:
		raise
		return bad_request(str(e))


# Save a list of participants
@app.route('/psycloud/admin/api/experiments/<experiment_id>/participants',
	methods=['POST'])
@auth.login_required
def save_participant_list(experiment_id):
	pass

# Save a participant
@app.route('/psycloud/admin/api/experiments/<experiment_id>/participants/<participant_index>',
	methods=['POST'])
@auth.login_required
def save_participant(experiment_id, participant_index):
	pass

# Modify a participant
@app.route('/psycloud/admin/api/experiments/<experiment_id>/participants/<participant_id>',
	methods=['PUT'])
@auth.login_required
def modify_participant(experiment_id, participant_id):
	pass

# Save coupons
@app.route('/psycloud/admin/api/experiments/<experiment_id>/coupons',
	methods=['POST'])
@auth.login_required
def save_coupons(experiment_id):
	data = request.get_json()
	try:
		coupon_list = admin_datastore.save_coupons(experiment_id, data)
		return valid_request('coupons', coupon_list)
	except Exception, e:
		raise
		return bad_request(str(e))
	

# Retrieve coupons
@app.route('/psycloud/admin/api/experiments/<experiment_id>/coupons',
	methods=['GET'])
@auth.login_required
def get_coupons(experiment_id):
	try:
		coupon_list = admin_datastore.get_coupons(experiment_id)
		return valid_request('coupons', coupon_list)
	except Exception, e:
		raise
		return bad_request(str(e))



#######################################################################################
#######################################################################################
# 
# ADMINISTRATOR DASHBOARD 
# 
#######################################################################################
#######################################################################################


@app.route('/psycloud/admin/dashboard', methods=['GET'])
@dashauth.login_required
def dashboard_main():
	try:
		experiment_list = admin_datastore.get_experiments(include_participant_counts=True)
		exps = []
		for exp in experiment_list:
			exps.append({'name': exp['experiment_name'], 'id':exp['id'], 'type':exp['experiment_type'],
				'num_available': exp['num_available'],
				'num_active': exp['num_active'],
				'num_completed': exp['num_completed'],
				'num_participants': exp['num_participants']})
		return render_template('main_dashboard.html', params=exps)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/admin/dashboard/experiment/<exp_id>', methods=['GET'])
@dashauth.login_required
def dashboard_view_experiment(exp_id):
	try:
		experiment = admin_datastore.get_experiments(experiment_id=exp_id)
		return jsonify(experiment)
	except Exception, e:
		raise
		return bad_request(str(e))


def dashboard_view_participant_list(exp_id, status='COMPLETED'):
	templates = {'ACTIVE': 'active_dash.html', 'COMPLETED': 'completed_dash.html'}
	try:
		participant_list = admin_datastore.get_participants(exp_id, keys_only=False, status_filter=status)
		return render_template(templates[status], exp_id=exp_id, subs=participant_list)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/admin/dashboard/experiment/<exp_id>/active', methods=['GET'])
@dashauth.login_required
def dashboard_view_active(exp_id):
	return dashboard_view_participant_list(exp_id, status='ACTIVE')

@app.route('/psycloud/admin/dashboard/experiment/<exp_id>/completed', methods=['GET'])
@dashauth.login_required
def dashboard_view_completed(exp_id):
	return dashboard_view_participant_list(exp_id, status='COMPLETED')


@app.route('/psycloud/admin/dashboard/participant/<uid>', methods=['GET'])
@dashauth.login_required
def dashboard_view_participant(uid):
	try:
		participant = client_datastore.get_participant(uid)
		participant['stimuli'] = client_datastore.get_stimuli(uid)
		participant['responses'] = client_datastore.get_responses(uid)
		return jsonify(participant)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/admin/dashboard/experiment/<exp_id>/completed/download_data', methods=['GET'])
@dashauth.login_required
def dashboard_download_completed_participant_data(exp_id):
	try:
		completed_participant_list = admin_datastore.get_data(exp_id, status_filter='COMPLETED')
		return jsonify({'participants': completed_participant_list})
	except Exception, e:
		raise
		return bad_request(str(e))


#######################################################################################
#######################################################################################
# 
# PARTICIPANT API
# 
#######################################################################################
#######################################################################################


@app.route('/psycloud/api/participant/',
	methods=['POST'])
def register_participant():
	'''
	Register a new participant.
	Assumes json input contains an experiment_id and optional registration_coupon
	Returns a participant_short_id if successful.
	Returns an error if registration coupon already registered or experiment_id not found.
	registration_code might be a mechanical turk id, for example.
	'''

	data = request.get_json()

	experiment_id = data['experiment_id']

	if 'registration_coupon' in data:
		registration_coupon = data['registration_coupon']
	else:
		registration_coupon = None

	try:
		short_id = client_datastore.register(experiment_id, registration_coupon=registration_coupon)
		return valid_request('participant_id', short_id)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/stimuli/',
	methods=['GET'])
def get_stimuli_list(participant_id):
	'''Retrieves a list of stimuli.'''

	try:
		stimulus_list = client_datastore.get_stimuli(participant_id)
		return valid_request('stimuli', stimulus_list)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/stimuli/',
	methods=['POST'])
def save_stimuli_list(participant_id):
	'''Saves a list of stimuli.'''
	
	stimuli_to_save = request.get_json()
	try:
		saved_stimuli = client_datastore.save_stimuli(participant_id, stimuli_to_save)
		return valid_request('stimuli', saved_stimuli)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/stimuli/<int:stimulus_number>',
	methods=['GET'])
def get_stimulus_by_number(participant_id, stimulus_number):
	'''Retrieve a specific stimulus'''

	try:
		stimulus_list = client_datastore.get_stimuli(participant_id, stimulus_number=stimulus_number)
		return valid_request('stimulus', stimulus_list[0])
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/stimuli/<int:stimulus_number>',
	methods=['POST'])
def save_stimulus_by_number(participant_id, stimulus_number):
	'''Save a specific stimulus'''
	
	stimulus_to_save = request.get_json()
	stimulus_to_save['stimulus_index'] = stimulus_number
	try:
		saved_stimuli = client_datastore.save_stimuli(participant_id, [stimulus_to_save])
		return valid_request('stimulus', saved_stimuli[0])
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/stimuli/max_count/',
	methods=['GET'])
def get_stimuli_max_count(participant_id):
	'''Returns the maximum number of stimuli that are allowed.'''
	
	try:
		max_count = client_datastore.get_max_number_stimuli(participant_id)
		return valid_request('max_count', max_count)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/responses/',
	methods=['GET'])
def get_response_list(participant_id):
	'''Retrieve a list of responses'''

	try:
		response_list = client_datastore.get_responses(participant_id)
		return valid_request('responses', response_list)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/responses/',
	methods=['POST'])
def save_response_list(participant_id):
	'''Save a list of responses'''
	
	responses_to_save = request.get_json()
	try:
		saved_responses = client_datastore.save_responses(participant_id, responses_to_save)
		return valid_request('responses', saved_responses)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/responses/<int:stimulus_number>',
	methods=['GET'])
def get_response(participant_id, stimulus_number):
	'''Retrieve a specific response'''

	try:
		response_list = client_datastore.get_responses(participant_id, stimulus_number=stimulus_number)
		return valid_request('response', response_list[0])
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/responses/<int:stimulus_number>',
	methods=['POST'])
def save_response(participant_id, stimulus_number):
	'''Save a specific response'''
	
	response_to_save = request.get_json()
	response_to_save['stimulus_index'] = stimulus_number
	try:
		saved_responses = client_datastore.save_responses(participant_id, [response_to_save])
		return valid_request('response', saved_responses[0])
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/stimuli/current/',
	methods=['GET'])
def get_current_stimulus_index(participant_id):
	'''Returns the current stimulus number.'''
	
	try:
		stimulus_index = client_datastore.get_current_stimulus(participant_id)
		return valid_request('stimulus_index', stimulus_index)
	except Exception, e:
		raise
		return bad_request(str(e))

@app.route('/psycloud/api/participant/<participant_id>/stimuli/current/',
	methods=['PUT'])
def set_current_stimulus_index(participant_id):
	'''Sets the current stimulus number.'''
	
	data = request.get_json()
	stimulus_index = data['stimulus_index']
	try:
		client_datastore.set_current_stimulus(participant_id, stimulus_index)
		return valid_request('stimulus_index', stimulus_index)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/current_status/',
	methods=['GET'])
def get_participant_status(participant_id):
	'''Returns the participant status.'''
	
	try:
		current_status = client_datastore.get_status(participant_id)
		return valid_request('current_status', current_status)
	except Exception, e:
		raise
		return bad_request(str(e))

@app.route('/psycloud/api/participant/<participant_id>/current_status/',
	methods=['PUT'])
def set_participant_status(participant_id):
	'''Sets the participant status.'''
	data = request.get_json()
	current_status = data['current_status']
	try:
		client_datastore.set_status(participant_id, current_status)
		return valid_request('current_status', current_status)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/details/',
	methods=['GET'])
def get_participant_details(participant_id):
	'''Returns the participant details.'''
	
	try:
		details = client_datastore.get_details(participant_id)
		return valid_request('details', details)
	except Exception, e:
		raise
		return bad_request(str(e))

@app.route('/psycloud/api/participant/<participant_id>/details/',
	methods=['PUT'])
def set_participant_details(participant_id):
	'''Sets the participant details.'''
	data = request.get_json()
	details = data['details']
	try:
		client_datastore.set_details(participant_id, details)
		return valid_request('details', details)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/confirmation_code/',
	methods=['GET'])
def get_confirmation_code(participant_id):
	'''Returns the participant confirmation code.'''
	
	try:
		confirmation_code = client_datastore.get_confirmation_code(participant_id)
		return valid_request('confirmation_code', confirmation_code)
	except Exception, e:
		raise
		return bad_request(str(e))



#######################################################################################
#######################################################################################
# 
# ITERATED PARTICIPANT API
# 
#######################################################################################
#######################################################################################

@app.route('/psycloud/api/participant/<participant_id>/chain_types/',
	methods=['GET'])
def get_iterated_chain_types(participant_id):
	'''Returns the available iterated chain types for the participant'''

	try:
		chain_types = iterated_client_datastore.get_chain_types(participant_id)
		return valid_request('chain_types', chain_types)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/chain/<chain_type>/',
	methods=['GET'])
def get_sample_from_chain(participant_id, chain_type):
	'''Returns a sample from the chain specified by chain_type'''

	try:
		sample = iterated_client_datastore.get_sample_from_chain(participant_id, chain_type)
		return valid_request('sample', sample)
	except Exception, e:
		raise
		return bad_request(str(e))


@app.route('/psycloud/api/participant/<participant_id>/chain/<chain_type>/',
	methods=['POST'])
def save_sample_to_chain(participant_id, chain_type):
	'''Saves a new sample from the chain specified by chain_type'''

	new_sample = request.get_json()

	try:
		saved_sample = iterated_client_datastore.save_sample_to_chain(participant_id,
			chain_type, new_sample)
		return valid_request('sample', saved_sample)
	except Exception, e:
		raise
		return bad_request(str(e))




#######################################################################################
#######################################################################################
# 
# EXPERIMENT SERVER
# 
#######################################################################################
#######################################################################################

@app.route('/experiment/<exp_short_id>', methods=['GET'])
def experiment_start(exp_short_id):
	'''Serves up an experiment'''
	return render_template('experiment.html', expId=exp_short_id)



#######################################################################################
#######################################################################################


@auth.get_password
def get_password(username):
    if username == 'psycloud':
        return 'psycloud'
    return None

@dashauth.get_password
def get_password(username):
    if username == 'dashboard':
        return 'dashboard'
    return None
 
@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'status':403, 'message': 'Unauthorized' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog

def valid_request(kind_of_data, data):
	return jsonify({'status':200, 'message':'OK', 'result':{kind_of_data:data}}), 200

def bad_request(e):
    return jsonify( {'status':400, 'message':'Bad Request', 'result':e}), 400

@app.errorhandler(404)
def page_not_found(e):
    return jsonify( {'status':404, 'message':'Not Found'}), 404

@app.errorhandler(500)
def page_not_found(e):
    # return 'Sorry, unexpected error: {}'.format(e), 500
    return jsonify( {'status':500, 'message':'Unexpected Error', 'result':e}), 500
