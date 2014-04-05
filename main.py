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
    return make_response(jsonify( { 'message': 'Unauthorized access' } ), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


####################################################
# EXPERIMENT ADMINISTRATOR API 
####################################################

# Upload a Json file that contains the complete experiment with participants and stimuli
# how to upload a Json experiment file:
# curl -u username:password -XPOST -H 'Content-Type:application/json' -d @mammals-stimset-00.json http://localhost:8080/webexperiment/admin/api/v0.1/upload_experiment
@app.route('/webexperiment/admin/api/upload_experiment',
	methods=['POST'])
@auth.login_required
def upload_experiment():
	data = request.get_json()
	experiment_key = datastore.upload_experiment(data)
	url_string = experiment_key.urlsafe()
	response = {'experiment_id': experiment_key.urlsafe()}
	return jsonify(response)

# Delete an experiment and all of its data
# how to delete an experiment:
# curl -u username:password -XDELETE http://localhost:8080/webexperiment/admin/api/v0.1/experiment/<experiment_id>
@app.route('/webexperiment/admin/api/experiment/<urlsafe_experiment_id>',
	methods=['DELETE'])
@auth.login_required
def remove_experiment(urlsafe_experiment_id):
	result = datastore.remove_experiment(urlsafe_experiment_id)
	if result:
		return jsonify({ 'result': 'success' })
	else:
		return jsonify({ 'result': 'failed' })

# Create a new experiment
@app.route('/webexperiment/admin/api/experiment',
	methods=['POST'])
@auth.login_required
def create_experiment():
	pass

# Retrieve a list of experiments
@app.route('/webexperiment/admin/api/experiment',
	methods=['GET'])
@auth.login_required
def get_experiment_list():
	pass

# Retrieve an experiment
@app.route('/webexperiment/admin/api/experiment/<experiment_id>',
	methods=['GET'])
@auth.login_required
def get_experiment(experiment_id):
	pass

# Modify an experiment
@app.route('/webexperiment/admin/api/experiment/<experiment_id>',
	methods=['PUT'])
@auth.login_required
def modify_experiment(experiment_id):
	pass

# Retrieve a list of participants
@app.route('/webexperiment/admin/api/experiment/<urlsafe_experiment_id>/participants',
	methods=['GET'])
@auth.login_required
def get_participant_list(urlsafe_experiment_id):
	pass

# Save a list of participants
@app.route('/webexperiment/admin/api/experiment/<urlsafe_experiment_id>/participants',
	methods=['POST'])
@auth.login_required
def save_participant_list(urlsafe_experiment_id):
	pass

# Save a participant
@app.route('/webexperiment/admin/api/experiment/<urlsafe_experiment_id>/participants<participant_id>',
	methods=['POST'])
@auth.login_required
def save_participant(urlsafe_experiment_id, participant_id):
	pass

# Modify a participant
@app.route('/webexperiment/admin/api/experiment/<urlsafe_experiment_id>/participants<participant_id>',
	methods=['PUT'])
@auth.login_required
def modify_participant(urlsafe_experiment_id, participant_id):
	pass



####################################################
# PARTICIPANT API 
####################################################


# Register a new participant
@app.route('/webexperiment/api/experiment/<urlsafe_experiment_id>/participants/register',
	methods=['POST'])
@auth.login_required
def register_participant(urlsafe_experiment_id):
	pass

# Register a new participant with registration code
@app.route('/webexperiment/api/experiment/<urlsafe_experiment_id>/participants/register/<registration_code>',
	methods=['POST'])
@auth.login_required
def register_participant_with_code(urlsafe_experiment_id, registration_code):
	pass

# PARTICIPANT API TODO
# POST		/participants/register												Register a new participant
# POST		/participants/register/[registration_code]							Register a new participant

# GET		/participants/[participant_id]										Retrieve a participant


# GET		/participants/[participant_id]/stimuli								Retrieve list of stimuli
# GET		/participants/[participant_id]/stimuli/current						Retrieve the current stimulus
# GET		/participants/[participant_id]/stimuli/[stimulus_number]			Retrieve a specific stimulus

# POST		/participants/[participant_id]/stimuli								Save a list of stimuli
# POST		/participants/[participant_id]/stimuli/current						Save the current stimulus
# POST		/participants/[participant_id]/stimuli/[stimulus_number]			Save a specific stimulus

# PUT		/participants/[participant_id]/stimuli/increment					Increment stimulus index and return next stimulus


# GET		/participants/[participant_id]/responses							Retrieve list of responses
# GET		/participants/[participant_id]/responses/previous					Retrieve previous response
# GET		/participants/[participant_id]/responses/previous/[n]				Retrieve list of previous [n] responses
# GET		/participants/[participant_id]/responses/[stimulus_id]				Retrieve the response for a specific stimulus

# POST		/participants/[participant_id]/responses							Save a list of responses
# POST		/participants/[participant_id]/responses/current					Save a response for the current stimuli
# PUT		/participants/[participant_id]/responses/[stimulus_id]				Update the response for a specific stimulus

# GET		/participants/[participant_id]/data									Retrieve list of stimuli and response data


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def page_not_found(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
