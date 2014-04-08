"""`main` is the top level module for the Flask application."""

from experiment_datastore import ExperimentDatastoreGoogleNDB

datastore = ExperimentDatastoreGoogleNDB()

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask.ext.httpauth import HTTPBasicAuth
 
app = Flask(__name__, static_url_path = "")
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
auth = HTTPBasicAuth()
 
@auth.get_password
def get_password(username):
    if username == 'username':
        return 'password'
    return None
 
@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'status':403, 'message': 'Unauthorized' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


#######################################################################################
#######################################################################################
# 
# ADMINISTRATOR API 
# 
#######################################################################################
#######################################################################################

# Upload a Json file that contains the complete experiment with participants and stimuli
# how to upload a Json experiment file:
# curl -u username:password -XPOST -H 'Content-Type:application/json' -d @mammals-stimset-00.json http://localhost:8080/psycloud/admin/api/experiments/upload_all_data
@app.route('/psycloud/admin/api/experiments/upload_all_data',
	methods=['POST'])
@auth.login_required
def upload_experiment_data():
	data = request.get_json()
	experiment_key = datastore.upload_experiment_data(data)
	result = {'experiment_id': experiment_key.urlsafe()}
	return jsonify(result)

# Delete an experiment and all of its data
# how to delete an experiment:
# curl -u username:password -XDELETE http://localhost:8080/psycloud/admin/api/experiments/<experiment_id>
@app.route('/psycloud/admin/api/experiments/<experiment_id>',
	methods=['DELETE'])
@auth.login_required
def remove_experiment(experiment_id):
	result = datastore.remove_experiment(experiment_id)
	if result:
		return jsonify({ 'result': 'success' })
	else:
		return jsonify({ 'result': 'failed' })

# Retrieve all experiment data
@app.route('/psycloud/admin/api/experiments/<experiment_id>/data',
	methods=['GET'])
@auth.login_required
def get_experiment_data(experiment_id, participant_id):
	pass

# Create a new experiment
@app.route('/psycloud/admin/api/experiments',
	methods=['POST'])
@auth.login_required
def create_experiment():
	pass

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
	pass

# Save a list of participants
@app.route('/psycloud/admin/api/experiments/<experiment_id>/participants',
	methods=['POST'])
@auth.login_required
def save_participant_list(experiment_id):
	pass

# Save a participant
@app.route('/psycloud/admin/api/experiments/<experiment_id>/participants/<participant_id>',
	methods=['POST'])
@auth.login_required
def save_participant(experiment_id, participant_id):
	pass

# Modify a participant
@app.route('/psycloud/admin/api/experiments/<experiment_id>/participants/<participant_id>',
	methods=['PUT'])
@auth.login_required
def modify_participant(experiment_id, participant_id):
	pass

# Save coupons
# curl -u username:password -XPOST -H 'Content-Type:application/json' -d @reg_coupons.json http://localhost:8080/psycloud/admin/api/experiments/<experiment_id>/coupons
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
# PARTICIPANT API 
# 
#######################################################################################
#######################################################################################

# Register a new participant
# curl -XPOST http://localhost:8080/psycloud/api/experiment/<experiment_id>/register
@app.route('/psycloud/api/experiment/<experiment_id>/register',
	methods=['POST'])
def register_participant(experiment_id):
# returns a participant_id
	result = datastore.register(experiment_id)
	if result is not None:
		if result['status'] == 200:
			return valid_request('participant', result['participant'])
		elif result['status'] == 400:
			return bad_request(result['e'])
	else:
		abort(404)

# Register a new participant with registration coupon
@app.route('/psycloud/api/experiment/<experiment_id>/register/<registration_coupon>',
	methods=['POST'])
def register_participant_with_coupon(experiment_id, registration_coupon):
# returns a participant_id
# registration_code might be a mechanical turk id, for example.
	result = datastore.register(experiment_id, registration_coupon=registration_coupon)
	if result is not None:
		if result['status'] == 200:
			return valid_request('participant', result['participant'])
		elif result['status'] == 400:
			return bad_request(result['e'])
	else:
		abort(404)

# Retrieve a participant
@app.route('/psycloud/api/participants/<participant_id>',
	methods=['GET'])
def get_participant(participant_id):
	participant = datastore.get_participant(participant_id)
	if participant is not None:
		return valid_request('participant', participant)
	else:
		abort(404)

# Retrieve a list of stimuli
@app.route('/psycloud/api/participants/<participant_id>/stimuli',
	methods=['GET'])
def get_stimuli_list(participant_id):
	stimuli_list = datastore.get_stimuli(participant_id)
	if stimuli_list is not None:
		return valid_request('stimuli', stimuli_list)
	else:
		abort(404)

# Save a list of stimuli
@app.route('/psycloud/api/participants/<participant_id>/stimuli',
	methods=['POST'])
def save_stimuli_list(participant_id):
	pass

# Retrieve the current stimulus
@app.route('/psycloud/api/participants/<participant_id>/stimuli/current',
	methods=['GET'])
def get_current_stimulus(participant_id):
	stimuli_list = datastore.get_stimuli(participant_id, current_only=True)
	if stimuli_list is not None:
		return valid_request('stimuli', stimuli_list)
	else:
		abort(404)

# Save the current stimulus
@app.route('/psycloud/api/participants/<participant_id>/stimuli/current',
	methods=['POST'])
def save_current_stimulus(participant_id):
	pass

# Retrieve a specific stimulus
@app.route('/psycloud/api/participants/<participant_id>/stimuli/<int:stimulus_number>',
	methods=['GET'])
def get_stimulus_by_number(participant_id, stimulus_number):
	stimuli_list = datastore.get_stimuli(participant_id, stimulus_number=stimulus_number)
	if stimuli_list is not None:
		return valid_request('stimuli', stimuli_list)
	else:
		abort(404)

# Save a specific stimulus
@app.route('/psycloud/api/participants/<participant_id>/stimuli/<int:stimulus_number>',
	methods=['POST'])
def save_stimulus_by_number(participant_id, stimulus_number):
	pass

# Increment current stimulus index and retrieve the next stimulus
@app.route('/psycloud/api/participants/<participant_id>/stimuli/next',
	methods=['PUT'])
def increment_and_get_next_stimulus(participant_id):
	result = datastore.increment_and_get_next_stimulus(participant_id)
	if result is not None:
		if result['status'] == 200:
			return valid_request('stimuli', result['stimuli'])
		elif result['status'] == 400:
			return bad_request(result['e'])
	else:
		abort(404)

# Retrieve a list of responses
@app.route('/psycloud/api/participants/<participant_id>/responses',
	methods=['GET'])
def get_response_list(participant_id):
	pass

# Retrieve the previous N responses
@app.route('/psycloud/api/participants/<participant_id>/responses/previous/<int:n_previous>',
	methods=['GET'])
def get_previous_responses(participant_id, n_previous):
	pass

# Save a list of responses
@app.route('/psycloud/api/participants/<participant_id>/responses',
	methods=['POST'])
def save_response_list(participant_id):
	pass

# Save a specific response
@app.route('/psycloud/api/participants/<participant_id>/responses/<int:stimulus_number>',
	methods=['POST'])
def save_response(participant_id, stimulus_number):
	data = request.get_json()
	result = datastore.save_response(participant_id, data, stimulus_index=stimulus_number)
	if result is not None:
		if result['status'] == 400:
			return bad_request(result['e'])
		else:
			return valid_request('response', result['response'])
	else:
		abort(404)

# Save the current response
@app.route('/psycloud/api/participants/<participant_id>/responses/current',
	methods=['POST'])
def save_current_response(participant_id):
	data = request.get_json()
	result = datastore.save_response(participant_id, data, current_only=True)
	if result is not None:
		if result['status'] == 400:
			return bad_request(result['e'])
		else:
			return valid_request('response', result['response'])
	else:
		abort(404)

# Retrieve list of all stimuli and response data for a participant
@app.route('/psycloud/api/participants/<participant_id>/data',
	methods=['GET'])
def get_participant_data(participant_id):
	pass



#######################################################################################
#######################################################################################


def valid_request(kind_of_data, data):
	return jsonify({'status':200, 'message':'OK', 'result':{kind_of_data:data}}), 200

def bad_request(e):
    return jsonify( {'status':400, 'message':'Bad Request', 'result':e}), 400

@app.errorhandler(404)
def page_not_found(e):
    return jsonify( {'status':404, 'message':'Not Found'}), 404

@app.errorhandler(500)
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
