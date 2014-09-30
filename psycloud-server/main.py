"""`main` is the top level module for the Flask application."""

from experiment_datastore import ExperimentDatastoreGoogleNDB

datastore = ExperimentDatastoreGoogleNDB()

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
# how to upload a Json experiment file:
# curl -u username:password -XPOST -H 'Content-Type:application/json' -d @../sample_data/mammals-stimset-00.json http://localhost:8080/psycloud/admin/api/experiments/upload_all_data
@app.route('/psycloud/admin/api/experiments/upload_all_data',
	methods=['POST'])
@auth.login_required
def upload_experiment_data():
	data = request.get_json()
	experiment_key = datastore.upload_experiment_data(data)
	return valid_request('experiment_id', experiment_key.urlsafe())

# Delete an experiment and all of its data
# how to delete an experiment:
# curl -u username:password -XDELETE http://localhost:8080/psycloud/admin/api/experiments/<experiment_id>
@app.route('/psycloud/admin/api/experiments/<experiment_id>',
	methods=['DELETE'])
@auth.login_required
def remove_experiment(experiment_id):
	result = datastore.remove_experiment(experiment_id)
	if result is not None:
		if result['status'] == 400:
			return bad_request(result['e'])
		else:
			return valid_request('deleted', result['experiment_name'])
	else:
		abort(404)

# Retrieve all experiment data
@app.route('/psycloud/admin/api/experiments/<experiment_id>/data',
	methods=['GET'])
@auth.login_required
def get_experiment_data(experiment_id):
	status_filter = None
	args = request.args
	if 'status' in args:
		status_filter = args['status']
	result = datastore.get_experiment_data(experiment_id, status_filter=status_filter)
	if result is not None:
		if result['status'] == 400:
			return bad_request(result['e'])
		else:
			return valid_request('participants', result['result'])
	else:
		abort(404)

# Create a new experiment
@app.route('/psycloud/admin/api/experiments',
	methods=['POST'])
@auth.login_required
def create_experiment():
	data = request.get_json()
	if 'experiment_name' in data:
		experiment_name = data['experiment_name']
		if 'num_participants' in data:
			num_participants = data['num_participants']
			try:
				experiment_key = datastore.create_experiment(experiment_name, num_participants)
				return valid_request('experiment_id', experiment_key.urlsafe())
			except:
				abort(500)
		else:
			return bad_request('num_participants was not provided.')
	else:
		return bad_request('experiment_name was not provided.')

# Retrieve a list of experiments
# curl -u username:password -XGET http://localhost:8080/psycloud/admin/api/experiments
@app.route('/psycloud/admin/api/experiments',
	methods=['GET'])
@auth.login_required
def get_experiment_list():
	experiment_list = datastore.get_experiments()
	return valid_request('experiments', experiment_list)

# Retrieve an experiment
# curl -u username:password -XGET http://localhost:8080/psycloud/admin/api/experiments/<experiment_id>
@app.route('/psycloud/admin/api/experiments/<experiment_id>',
	methods=['GET'])
@auth.login_required
def get_experiment(experiment_id):
	experiment_list = datastore.get_experiments(experiment_id=experiment_id)
	if experiment_list is not None:
		return valid_request('experiments', experiment_list)
	else:
		abort(404)

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
	result = datastore.get_experiment_participants(experiment_id, keys_only=keys_only, status_filter=status_filter)
	if result is not None:
		if result['status'] == 400:
			return bad_request(result['e'])
		else:
			return valid_request('participants', result['result'])
	else:
		abort(404)


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
# curl -u username:password -XPOST -H 'Content-Type:application/json' -d @../sample_data/reg_coupons.json http://localhost:8080/psycloud/admin/api/experiments/<experiment_id>/coupons
@app.route('/psycloud/admin/api/experiments/<experiment_id>/coupons',
	methods=['POST'])
@auth.login_required
def save_coupons(experiment_id):
	data = request.get_json()
	result = datastore.save_coupons(experiment_id, data)
	if result is not None:
		if result['status'] == 400:
			return bad_request(result['e'])
		else:
			return valid_request('coupons', result['result'])
	else:
		abort(404)

# Retrieve coupons
# curl -u username:password -XGET http://localhost:8080/psycloud/admin/api/experiments/<experiment_id>/coupons
@app.route('/psycloud/admin/api/experiments/<experiment_id>/coupons',
	methods=['GET'])
@auth.login_required
def get_coupons(experiment_id):
	coupon_list = datastore.get_coupons(experiment_id)
	if coupon_list is not None:
		return valid_request('coupons', coupon_list)
	else:
		abort(404)


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
	experiment_list = datastore.get_experiments()
	exps = []
	for exp in experiment_list:
		exps.append({'name':exp['experiment_name'], 'id':exp['id'],
			'num_available':len(exp['available_participants']),
			'num_active':len(exp['active_participants']),
			'num_completed':len(exp['completed_participants']),
			'num_participants':exp['num_participants']})
	return render_template('main_dashboard.html', params=exps)


@app.route('/psycloud/admin/dashboard/experiment/<exp_id>', methods=['GET'])
@dashauth.login_required
def dashboard_view_experiment(exp_id):
	experiment_list = datastore.get_experiments(experiment_id=exp_id)
	if experiment_list is not None:
		experiment = experiment_list[0]
		return jsonify(experiment)
	else:
		abort(404)


def dashboard_view_participant_list(exp_id, status='COMPLETED'):
	templates = {'ACTIVE': 'active_dash.html', 'COMPLETED': 'completed_dash.html'}
	result = datastore.get_experiment_participants(exp_id, keys_only=False, status_filter=status)
	if result is not None:
		if result['status'] == 400:
			return bad_request(result['e'])
		else:
			return render_template(templates[status], exp_id=exp_id, subs=result['result'])
	else:
		abort(404)

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
	participant = datastore.get_participant(uid)
	if participant is not None:
		stimuli_list = datastore.get_stimuli(uid)
		response_list = datastore.get_responses(uid)
		participant['stimuli'] = stimuli_list
		participant['responses'] = response_list
		return jsonify(participant)
	else:
		abort(404)


@app.route('/psycloud/admin/dashboard/experiment/<exp_id>/completed/download_data', methods=['GET'])
@dashauth.login_required
def dashboard_download_completed_participant_data(exp_id):
	result = datastore.get_experiment_data(exp_id, status_filter='COMPLETED')
	# if result is not None:
	# 	if result['status'] == 400:
	# 		return bad_request(result['e'])
	# 	else:
	# 		return jsonify(result['result'])
	# else:
	# 	abort(404)

	if result is not None:
		if result['status'] == 400:
			return bad_request(result['e'])
		else:
			# return valid_request('participants', result['result'])
			return jsonify({'participants': result['result']})
	else:
		abort(404)



#######################################################################################
#######################################################################################
# 
# PARTICIPANT API VERSION 1
# 
#######################################################################################
#######################################################################################

@app.route('/psycloud/api/v1/experiment/<experiment_id>/register',
	methods=['POST'])
def register_participant(experiment_id):
	'''
	Register a new participant.
	Returns a participant_id if successful.
	Returns an error if experiment_id not found.
	'''
	result = datastore.register(experiment_id)
	if result is not None:
		if result['status'] == 200:
			return valid_request('participant', result['participant'])
		elif result['status'] == 400:
			return bad_request(result['e'])
	else:
		abort(404)

@app.route('/psycloud/api/v1/experiment/<experiment_id>/register/<registration_coupon>',
	methods=['POST'])
def register_participant_with_coupon(experiment_id, registration_coupon):
	'''
	Register a new participant with registration coupon.
	Returns a participant_id if successful.
	Returns an error if registration coupon already registered or experiment_id not found.
	registration_code might be a mechanical turk id, for example.
	'''

	result = datastore.register(experiment_id, registration_coupon=registration_coupon)
	if result is not None:
		if result['status'] == 200:
			return valid_request('participant', result['participant'])
		elif result['status'] == 400:
			return bad_request(result['e'])
	else:
		abort(404)

@app.route('/psycloud/api/v1/participant/<participant_id>/stimuli',
	methods=['GET'])
def get_stimuli_list(participant_id):
	'''Retrieves a list of stimuli.'''
	stimuli_list = datastore.get_stimuli(participant_id)
	if stimuli_list is not None:
		return valid_request('stimuli', stimuli_list)
	else:
		abort(404)

@app.route('/psycloud/api/v1/participant/<participant_id>/stimuli',
	methods=['POST'])
def save_stimuli_list(participant_id):
	'''Saves a list of stimuli.'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/stimuli/<int:stimulus_number>',
	methods=['GET'])
def get_stimulus_by_number(participant_id, stimulus_number):
	'''Retrieve a specific stimulus'''
	stimuli_list = datastore.get_stimuli(participant_id, stimulus_number=stimulus_number)
	if stimuli_list is not None:
		return valid_request('stimuli', stimuli_list)
	else:
		abort(404)

@app.route('/psycloud/api/v1/participant/<participant_id>/stimuli/<int:stimulus_number>',
	methods=['POST'])
def save_stimulus_by_number(participant_id, stimulus_number):
	'''Save a specific stimulus'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/stimuli/count',
	methods=['GET'])
def get_stimuli_count(participant_id):
	'''Returns the number of stimuli that have been saved.'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/stimuli/max_count',
	methods=['GET'])
def get_stimuli_max_count(participant_id):
	'''Returns the maximum number of stimuli that are allowed.'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/responses',
	methods=['GET'])
def get_response_list(participant_id):
	'''Retrieve a list of responses'''
	response_list = datastore.get_responses(participant_id)
	if response_list is not None:
		return valid_request('responses', response_list)
	else:
		abort(404)

@app.route('/psycloud/api/v1/participants/<participant_id>/responses',
	methods=['POST'])
def save_response_list(participant_id):
	'''Save a list of responses'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/responses/<int:stimulus_number>',
	methods=['GET'])
def get_response(participant_id, stimulus_number):
	'''Retrieve a specific response'''
	response_list = datastore.get_responses(participant_id, stimulus_number=stimulus_number)
	if response_list is not None:
		return valid_request('responses', response_list)
	else:
		abort(404)

@app.route('/psycloud/api/v1/participants/<participant_id>/responses/<int:stimulus_number>',
	methods=['POST'])
def save_response(participant_id, stimulus_number):
	'''Save a specific response'''
	data = request.get_json()
	result = datastore.save_response(participant_id, data, stimulus_index=stimulus_number)
	if result is not None:
		if result['status'] == 400:
			return bad_request(result['e'])
		else:
			return valid_request('response', result['response'])
	else:
		abort(404)

@app.route('/psycloud/api/v1/participant/<participant_id>/responses/count',
	methods=['GET'])
def get_response_count(participant_id):
	'''Returns the number of responses that have been saved.'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/stimuli/current',
	methods=['GET'])
def get_response_count(participant_id):
	'''Returns the current stimulus number.'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/stimuli/current',
	methods=['PUT'])
def get_response_count(participant_id):
	'''Sets the current stimulus number.'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/status',
	methods=['GET'])
def get_response_count(participant_id):
	'''Returns the participant status.'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/status',
	methods=['PUT'])
def get_response_count(participant_id):
	'''Sets the participant status.'''
	pass

@app.route('/psycloud/api/v1/participant/<participant_id>/confirmation_code',
	methods=['GET'])
def get_response_count(participant_id):
	'''Returns the participant confirmation code.'''
	pass



#######################################################################################
#######################################################################################
# 
# PARTICIPANT API (DEPRICATED)
# 
#######################################################################################
#######################################################################################

# # Register a new participant
# # curl -XPOST http://localhost:8080/psycloud/api/experiment/<experiment_id>/register
# @app.route('/psycloud/api/experiment/<experiment_id>/register',
# 	methods=['POST'])
# def register_participant(experiment_id):
# # returns a participant_id
# 	result = datastore.register(experiment_id)
# 	if result is not None:
# 		if result['status'] == 200:
# 			return valid_request('participant', result['participant'])
# 		elif result['status'] == 400:
# 			return bad_request(result['e'])
# 	else:
# 		abort(404)

# # Register a new participant with registration coupon
# # curl -XPOST http://localhost:8080/psycloud/api/experiment/<experiment_id>/register/<registration_coupon>
# @app.route('/psycloud/api/experiment/<experiment_id>/register/<registration_coupon>',
# 	methods=['POST'])
# def register_participant_with_coupon(experiment_id, registration_coupon):
# # returns a participant_id
# # registration_code might be a mechanical turk id, for example.
# 	result = datastore.register(experiment_id, registration_coupon=registration_coupon)
# 	if result is not None:
# 		if result['status'] == 200:
# 			return valid_request('participant', result['participant'])
# 		elif result['status'] == 400:
# 			return bad_request(result['e'])
# 	else:
# 		abort(404)

# # Retrieve a participant
# # curl -XGET http://localhost:8080/psycloud/api/participants/<participant_id>
# @app.route('/psycloud/api/participants/<participant_id>',
# 	methods=['GET'])
# def get_participant(participant_id):
# 	participant = datastore.get_participant(participant_id)
# 	if participant is not None:
# 		return valid_request('participant', participant)
# 	else:
# 		abort(404)

# # Retrieve a list of stimuli
# # curl -XGET http://localhost:8080/psycloud/api/participants/<participant_id>/stimuli
# @app.route('/psycloud/api/participants/<participant_id>/stimuli',
# 	methods=['GET'])
# def get_stimuli_list(participant_id):
# 	stimuli_list = datastore.get_stimuli(participant_id)
# 	if stimuli_list is not None:
# 		return valid_request('stimuli', stimuli_list)
# 	else:
# 		abort(404)

# # Save a list of stimuli
# @app.route('/psycloud/api/participants/<participant_id>/stimuli',
# 	methods=['POST'])
# def save_stimuli_list(participant_id):
# 	pass

# # Retrieve the current stimulus
# # curl -XGET http://localhost:8080/psycloud/api/participants/<participant_id>/stimuli/current
# @app.route('/psycloud/api/participants/<participant_id>/stimuli/current',
# 	methods=['GET'])
# def get_current_stimulus(participant_id):
# 	stimuli_list = datastore.get_stimuli(participant_id, current_only=True)
# 	if stimuli_list is not None:
# 		return valid_request('stimuli', stimuli_list)
# 	else:
# 		abort(404)

# # Save the current stimulus
# @app.route('/psycloud/api/participants/<participant_id>/stimuli/current',
# 	methods=['POST'])
# def save_current_stimulus(participant_id):
# 	pass

# # Retrieve a specific stimulus
# # curl -XGET http://localhost:8080/psycloud/api/participants/<participant_id>/stimuli/<stimulus_number>
# @app.route('/psycloud/api/participants/<participant_id>/stimuli/<int:stimulus_number>',
# 	methods=['GET'])
# def get_stimulus_by_number(participant_id, stimulus_number):
# 	stimuli_list = datastore.get_stimuli(participant_id, stimulus_number=stimulus_number)
# 	if stimuli_list is not None:
# 		return valid_request('stimuli', stimuli_list)
# 	else:
# 		abort(404)

# # Save a specific stimulus
# @app.route('/psycloud/api/participants/<participant_id>/stimuli/<int:stimulus_number>',
# 	methods=['POST'])
# def save_stimulus_by_number(participant_id, stimulus_number):
# 	pass

# # Increment current stimulus index and retrieve the next stimulus
# # curl -XPUT http://localhost:8080/psycloud/api/participants/<participant_id>/stimuli/next
# @app.route('/psycloud/api/participants/<participant_id>/stimuli/next',
# 	methods=['PUT'])
# def increment_and_get_next_stimulus(participant_id):
# 	result = datastore.increment_and_get_next_stimulus(participant_id)
# 	if result is not None:
# 		if result['status'] == 200:
# 			return valid_request('stimuli', result['stimuli'])
# 		elif result['status'] == 400:
# 			return bad_request(result['e'])
# 	else:
# 		abort(404)

# # Retrieve a list of responses
# @app.route('/psycloud/api/participants/<participant_id>/responses',
# 	methods=['GET'])
# def get_response_list(participant_id):
# 	response_list = datastore.get_responses(participant_id)
# 	if response_list is not None:
# 		return valid_request('responses', response_list)
# 	else:
# 		abort(404)

# # Retrieve a specific response
# @app.route('/psycloud/api/participants/<participant_id>/responses/<int:stimulus_number>',
# 	methods=['GET'])
# def get_response(participant_id, stimulus_number):
# 	response_list = datastore.get_responses(participant_id, stimulus_number=stimulus_number)
# 	if response_list is not None:
# 		return valid_request('responses', response_list)
# 	else:
# 		abort(404)

# # Retrieve the previous response
# @app.route('/psycloud/api/participants/<participant_id>/responses/previous',
# 	methods=['GET'])
# def get_previous_response(participant_id):
# 	response_list = datastore.get_responses(participant_id, previous_only=True)
# 	if response_list is not None:
# 		return valid_request('responses', response_list)
# 	else:
# 		abort(404)

# # Save a list of responses
# @app.route('/psycloud/api/participants/<participant_id>/responses',
# 	methods=['POST'])
# def save_response_list(participant_id):
# 	pass

# # Save a specific response
# # curl -XPOST http://localhost:8080/psycloud/api/participants/<participant_id>/response/<stimulus_number>
# @app.route('/psycloud/api/participants/<participant_id>/responses/<int:stimulus_number>',
# 	methods=['POST'])
# def save_response(participant_id, stimulus_number):
# 	data = request.get_json()
# 	result = datastore.save_response(participant_id, data, stimulus_index=stimulus_number)
# 	if result is not None:
# 		if result['status'] == 400:
# 			return bad_request(result['e'])
# 		else:
# 			return valid_request('response', result['response'])
# 	else:
# 		abort(404)

# # Save the current response
# # curl -XPOST http://localhost:8080/psycloud/api/participants/<participant_id>/response/current
# @app.route('/psycloud/api/participants/<participant_id>/responses/current',
# 	methods=['POST'])
# def save_current_response(participant_id):
# 	data = request.get_json()
# 	result = datastore.save_response(participant_id, data, current_only=True)
# 	if result is not None:
# 		if result['status'] == 400:
# 			return bad_request(result['e'])
# 		else:
# 			return valid_request('response', result['response'])
# 	else:
# 		abort(404)

# @app.route('/psycloud/api/participants/<participant_id>/completed',
# 	methods=['POST'])
# def record_as_completed(participant_id):
# 	result = datastore.record_as_completed(participant_id)
# 	if result is not None:
# 		if result['status'] == 400:
# 			return bad_request(result['e'])
# 		else:
# 			return valid_request('participant', result['participant'])
# 	else:
# 		abort(404)

# # Retrieve list of all stimuli and response data for a participant
# @app.route('/psycloud/api/participants/<participant_id>/data',
# 	methods=['GET'])
# def get_participant_data(participant_id):
# 	pass



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
