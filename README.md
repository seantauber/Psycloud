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
admin_client.upload_data(json_filename="../sample_data/mammals-stimset-00.json")
```

This will take a few minutes, and will eventually return an experiment_id.


#### Getting a list of experiments:

```python
exp_list = admin_client.get_experiment_list()
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



