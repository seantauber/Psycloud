# Psycloud

### Deploying the server to Google App Engine
To launch the REST-API server locally on Google App Engine development server:

```
$ cd Psycloud
$ dev_appserver.py REST-API
```

## Admin client
This client will is used to administer a web experiment from your local computer.
Currently there is only a Python admin client. Javascript and R clients will be added in the future.

#### Uploading an entire experiment from a file

Launch python from within the python-client directory.
```
$ cd Psycloud/python-client
$ python
```

Instantiate the admin client and upload the example experiment file *mammals-stimset-00.json*
```python
from psycloudclient import PsycloudAdminClient
admin_client = PsycloudAdminClient("http://localhost:8080", "username", "password")
req = admin_client.upload_data(json_filename="../sample_data/mammals-stimset-01.json")
```

This will return a JSON formatted response object which is assigned to *req*:
```python
> req
{u'message': u'OK',
 u'result': {u'experiment_id': u'MDAyNjBkNTEtNzU4OS00MjhmLWE5YmEtNDg5M2Q0ZjAyNGNi'},
 u'status': 200}
```
The request object contains the http status --- 200 indicates that everything went OK, otherwise the message will contain more details. If everything went ok, the result field will contain the id for the experiment you just created and can be accessed from the request object like this
```python
if req['status'] == 200:
	exp_id = req['result']['experiment_id']
else:
	# there was a problem with the request
```

An alternative to uploading a json file is to pass a dictionary object containing the information in the json file.
```python
req = admin_client.upload_data(data_dict=experiment_data)
```

#### Format of experiment data dictionary/json
The *experiment_data* dictionary should be a set of nested dictionaries. The top level dictionary has the following format:
```python
{
'experiment_name': experiment_name,
'num_participants': number_of_participants,
'participants': list_of_participants
}
```
Each item in the list_of_participants is a dictionary with the format:
```python
{
'participant_index': participant_index,
'stimuli_count': number_stimuli,
'stimuli': list_of_stimuli
}
```
Each item in the list_of_stimuli is a dictionary with the format:
```python
{
'stimulus_index': stimulus_index,
'stimulus_type': stimulus_type_label,
'variables': list_of_variables
}
```
Each stimulus_type can correspond to an html template or javascript function that renders that stimuli. This allows for a mixture of stimulus types within an experiment and provides a great deal of flexibility when implementing new experiments.

Each item in the list_of_variables is a dictionary where each key is the name of a variable. The value for each key corresponds to the variable's value and can be scalar or a list. There can be any number of key value pairs, each representing a variable. In the example below there are two variables, X and Y, where Y is a vector and X is scalar. The variables can be anything, it's up to you to handle them properly with your web based experiment.
```python
{
'Y': [1,2,3,4,5,'six'],
'X': 'scalarvalue'
}
```

#### Getting a list of experiments:
You can request a list of experiments and associated experiment info like this
```python
req = admin_client.get_experiment_list()
if req['status'] == 200:
	exp_info = req['result']['experiments'] #this is a list of experiments
else:
	#request error
```
Or you can use a specific experiment id like this
```python
req = admin_client.get_experiment(expid)
if req['status'] == 200:
	exp_info = req['result']['experiments'][0] # We know there is only one item in the experiment list, so we just grab it at index 0
```

## Experiment client
This client provides an interface for your web experiment to communicate with the REST-API server. It allows you to load and recieve experiment data (stimuli, responses, etc). The Python client allows for Python based web experiments. The Javascript client will allow for JS based web experiments.

#### Get an instance of the experiment client
```python
from psycloudclient import PsycloudClient
client = PsycloudClient()
```

#### Register a new participant:
```python
participant = client.register(experiment_id)
```
#### Register a new participant with an registration coupon (i.e. turk id)
```python
participant = client.register(experiment_id, registration_coupon=turk_id)
```
#### Get the participant_id (it will be required for all future transactions)
```python
participant_id = participant['participant_id']
```
#### Get all the stimuli for this participant
```python
stimuli = client.get_stimuli_list(participant_id)
```
#### Get the current stimulus
```python
stimuli = client.get_current_stimulus(participant_id)
```
#### Increment the current stimulus index and get the next stimulus
```python
stimuli = client.get_next_stimulus(participant_id)
```
#### Save a response for the current stimulus
```python
example_vars = [{'name':'R1', 'value':10}, {'name':'R2', 'value':[1,2,3,4]}]
response = {'variables':example_vars}
client.save_current_response(participant_id, response)
```



