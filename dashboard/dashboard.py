import os
import json


from psycloudclient import PsycloudClient, PsycloudAdminClient
psycloud_client = PsycloudClient("http://psycloud-server-1.appspot.com")
psycloud_aclient = PsycloudAdminClient("http://psycloud-server-1.appspot.com", "username", "password")

# Import the Flask Framework
from flask import Flask, render_template, request, redirect, url_for, abort, jsonify
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

@app.route('/', methods=['GET'])
@auth.login_required
def main_dashboard():
	exp_list = psycloud_aclient.get_experiment_list()['result']['experiments']
	exps = []
	for exp in exp_list:
		exps.append({'name':exp['experiment_name'], 'id':exp['id'],
			'num_available':len(exp['available_participants']),
			'num_active':len(exp['active_participants']),
			'num_completed':len(exp['completed_participants']),
			'num_participants':exp['num_participants']})
	return render_template('main_dashboard.html', params=exps)

@app.route('/experiment/<exp_id>', methods=['GET'])
@auth.login_required
def view_experiment(exp_id):
	exp = psycloud_aclient.get_experiment(exp_id)['result']['experiments'][0]
	return jsonify(exp)

@app.route('/experiment/<exp_id>/active', methods=['GET'])
@auth.login_required
def view_active(exp_id):
	sublist = psycloud_aclient.get_participant_list(exp_id)['result']['participants']
	active = []
	for sub in sublist:
		if sub['status'] == 'ACTIVE':
			active.append(sub)
	return render_template('active_dash.html', subs=active)

@app.route('/experiment/<exp_id>/completed', methods=['GET'])
@auth.login_required
def view_completed(exp_id):
	sublist = psycloud_aclient.get_participant_list(exp_id)['result']['participants']
	completed = []
	for sub in sublist:
		if sub['status'] == 'COMPLETED':
			completed.append(sub)
	return render_template('completed_dash.html', subs=completed, exp_id=exp_id)

@app.route('/participant/<uid>', methods=['GET'])
@auth.login_required
def view_participant(uid):
	sub = psycloud_client.get_participant(uid)['result']['participant']
	stim_list = psycloud_client.get_stimuli_list(uid)['result']['stimuli']
	resp_list = psycloud_client.get_response_list(uid)['result']['responses']
	sub['stimuli'] = stim_list
	sub['responses'] = resp_list
	return jsonify(sub)

@app.route('/experiment/<exp_id>/completed/download_data', methods=['GET'])
@auth.login_required
def download_completed_participant_data(exp_id):
	sublist = psycloud_aclient.get_experiment_data(exp_id, status='COMPLETED')['result']
	return jsonify(sublist)
	




@auth.get_password
def get_password(username):
    if username == 'username':
        return 'password'
    return None
 
# @auth.error_handler
# def unauthorized():
#     return make_response(jsonify( { 'status':403, 'message': 'Unauthorized' } ), 403)
#     # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
