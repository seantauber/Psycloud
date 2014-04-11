Psycloud
========

To launch the REST-API server locally on Google App Engine development server:

$ dev_appserver.py REST-API

To upload the sample experiment with the python admin client:

launch python from the directory "Psycloud/python-client"

from psycloudclient import PsycloudAdminClient
admin_client = PsycloudAdminClient("http://localhost:8080", "username", "password")
admin_client.upload_data(json_filename="../sample_data/mammals-stimset-00.json")

This will take a few minutes, and will eventually return an experiment_id.

To get a list of experiments:

exp_list = admin_client.get_experiment_list()


To use the python experiment client:

from psycloudclient import PsycloudClient
client = PsycloudClient()

Register a new participant:
participant = client.register(experiment_id)

Register a new participant with an registration coupon (i.e. turk id):
participant = client.register(experiment_id, registration_coupon=turk_id)

Get the participant_id because it will be required for all future transactions:
participant_id = participant['participant_id']

Get all the stimuli for this participant:
stimuli = client.get_stimuli_list(participant_id)

Get the current stimulus:
stimuli = client.get_current_stimulus(participant_id)

Increment the current stimulus index and get the next stimulus:
stimuli = client.get_next_stimulus(participant_id)

Save a response for the current stimulus:
variables = [{'name':'R1', 'value':10}, {'name':'R2', 'value':[1,2,3,4]}]
response = {'variables':variables}
client.save_current_response(participant_id, response)




