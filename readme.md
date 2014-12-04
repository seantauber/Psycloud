#Psycloud
A backend experiment server for AppEngine with Javascript and Python remote client libraries


###Part 1: Getting started
Requirements:

1. You already have a Google AppEngine account and know how to create and manage new and existing apps. 

2. You have installed the necessary commandline tools for deploying AppEngine apps from your local machine.

3. You have Python 2.X installed.

4. Your python installation has pip package mananger installed


####Set up AppEngine
Create a new AppEnging app that will be used as your experiment server. Let's assume that the name of your app is **my-psycloud-server**.

####Clone Psycloud repository to your local machine
Clone or download the zip of the psycloud repo to a directory on your local machine.
http://github.com/seantauber/psycloud

####Install requirements
The server is written in Python, and has dependencies which must be installed before it can be deployed. These dependencies are specified in the file `requirements.txt` and must be installed in a folder called `lib/`

Create the lib folder inside the psycloud rep folder that you just downloaded:
```
mkdir lib
```

Install the requirements in the `lib/` folder:
```
pip install -r requirements.txt -t lib/
```

####Configure server
In order to configure the AppEngine app id, open the file `app.yaml` and replace the default application id with your application id:

So change this:
```
application: your-application-id-here
```
To this:
```
application: my-psycloud-server
```

The next step is to change the default administrator login information for the psycloud server. To do this, open the file `server.cfg` and change the passwords (and usernames if you wish) for admin (used for remote api calls) and dashboard (used for web dashboard).
```
{
	"adminuser": "admin",
	"adminpass": "defaultadminpassword",
	"dashuser": "admin",
	"dashpass": "defaultdashboardpassword"
}
```


####Upload Psycloud Server to AppEngine
You are now ready to launch the server on AppEngine!

You can either use the Google AppEngine launcher program, or the command line. To use the command line from within the psycloud folder use the following command:
```
appcfg.py update .
```
If you are outside of the psycloud directory replace the `.` with the path to the psycloud folder:
```
appcfg.py update /local/path/to/psycloud/server/
```

####Go to the experiment dashboard
Once your server has launched, you can view the experiment dashboard at http://my-psycloud-server.appspot.com/psycloud/admin/dashboard



###Part 2: Creating Experiments

####Installing psycloud-python client

The psycloud-python client is required in order to remotely administer the experiment server from your local machine. Some administrative functions -- such as viewing active experiments, participants, and downloading data -- are also available through the web-based admin dashboard. Creating new experiments and uploading stimuli are currently only possible through the python client.

You can either clone or download the python client to a local repository from https://github.com/seantauber/psycloud-python or you can install it as a package in your local python distribution using a package manager such as pip:
```
pip install https://github.com/seantauber/psycloud-python/zipball/master#egg=psycloud_python
```

**Note:** The psycloud-python client has dependencies on the following packages: *requests*, *numpy*, and *pandas*. You will need to ensure these packages are installed in your python distribution. All of these packages are pre-configured in the highly recommended [Anaconda Python Distribution](https://store.continuum.io/cshop/anaconda/).


In the next section I will demonstrate how the psycloud python client can be used to create new experiments on the server. A later section will provide more detail about how the python client can be used to administer your experiment server from a python shell on your local machine.


####Creating a new experiment *without* pre-allocated stimuli

You can create an experiment in which you create and save the stimuli for each participant at runtime using the JavaScript client. However, you are required to specify the maximum number of participants and the maximum number of stimuli per participant. The following python script creates a new experiment.

```python
from psycloud_python.client import PsycloudAdminClient

# Initialize the admin client

base_url="http://my-psycloud-server.appspot.com"
username="admin"
password="defaultadminpassword"

admin_client = PsycloudAdminClient(base_url, username, password)


# Create a new experiment

experiment_name = "demo_exp_without_stimuli"
num_participants = 200
max_number_stimuli = 100

admin_client.create_experiment(experiment_name, num_participants, max_num_stimuli)
```

If you enter the last line in a python shell, and all goes well, a unique experiment id will be returned by the server indicating that the experiment creation was successful.


####Creating a new experiment *with* pre-allocated stimuli

In some cases you may want to create an experiment in which all of the participants and stimuli are preset. When new participants begin your experiment, they will be assigned to the next available preset participant and the preset stimuli can simply be loaded directly from the server.

In order to create an experiment with preset participant and stimuli, you must create an experiment configuration file containing all of the participant and stimulus data. This file should be in JSON format. The details of how to format this file are provided in a later section of this readme. The following sample config files are provided in the [psycloud_python github repo](https://github.com/seantauber/psycloud-python/tree/master/sample_data)
```
seeing-stimset.json
psychic-stimset.json
mammals-stimset.json
```

Here is an example of how to use the python admin client to create a new experiment using the *seeing* config file:
```python
from psycloud_python.client import PsycloudAdminClient

# Initialize the admin client

base_url="http://my-psycloud-server.appspot.com"
username="admin"
password="defaultadminpassword"

admin_client = PsycloudAdminClient(base_url, username, password)


# Create a new experiment

experiment_name = "demo_exp_with_stimuli"
json_config_filename = "seeing-stimset.json"

admin_client.create_experiment(experiment_name, json_file=json_config_filename)
```
Just like in the previous example, an experiment id will be returned by the server if everything goes well.


###Part 3: Managing Experiments

The python admin client allows you to list and delete existing experiments, as well as getting information about participants. The web dashboard for your server -- which is found at http://my-psycloud-server.appspot.com/psycloud/admin/dashboard -- provides a convenient way to see a list of your existing experiments, including participants who are ACTIVE, AVAILABLE, COMPLETED, etc. The Dashboard also allows you to inspect individual participant data and download all the data for completed participants. You can do all of these things and more using the python client, but I will only cover listing and deleting experiments with the python client because deletion is not currently possible using the dashboard.


####Listing experiments
You can get a list of all existing experiments using either the web dashboard, or with the following python command:
```python
admin_client.get_experiment_list()
```
Each experiment has an *id* which is used to identify the experiment internally for administrative purposes, and a *short_id* which is used as a public reference in the url that participants will use to access the experiment over the web (more on this later). 


####Deleting experiments
You can easily delete an experiment using its long internal *id*:
```python
exp_id = 'ag5zfnBzeWNsb3VkZGVtb3IXCxIKRXhwZXJpbWVudBiAgICA'
admin_client.delete_experiment(exp_id)
```
The above code will delete everything associated with the experiment including all participants and data.


###Part 4: Setup Experiment Front-End with Psycloud Server

You can host multiple experiments on the server at the same time. You can have multiple *types* of experiments, where each type has a particular user interface and front-end resources (html, JavaScript, images, etc). You can also have multiple *instances* of each type of experiment. Each instance of the same type would use the same user interface but would have a separate database on the server. This is useful if you need to run the same experiment multiple times with different participants.

####Setting up experiment types

You can setup an experiment type by placing the front-end resources in specific folders on the psycloud server. Let's say your experiment type is called *my_exp_type*. First create a new subfolder called my_exp_type in the existing folder ./templates/

You will notice that there are already some existing types in this folder, *demo_exp_type_1* and *demo_exp_type_2*.

The main html landing page for your experiment should be placed in the new folder you just created, and should be called *index.html*. This html file needs to have some special templating code (the code between double curly brackets {{ }}) that the server will be automatically rendered by the server at runtime. You should start by copying the *index.html* file from one of the demo types and leave the template code in place. Below is an example of the basic template file for *demo_exp_type_1*.

```html
<html>
	<head>
		<title>Psycloud JavaScript Client Demo</title>
	</head>
	<body>

		<script>
			var expId = "{{ expId }}";
			var expKind = "{{ expKind }}";

			var expJsDir = "{{ url_for('.static', filename='experiments/'+expKind+'/js/') }}"
			var expResourceDir = "{{ url_for('.static', filename='experiments/'+expKind+'/resources/') }}"
		</script>

		<!-- jQuery -->
		<script src="{{url_for('.static', filename='js/jquery.min.js')}}"></script>
		
		<!-- PsycloudJS -->
		<script src="{{url_for('.static', filename='js/PsycloudJS/psycloud.js')}}"></script>

		<script>
		 	participant = new StandardParticipant(expId, "../../");
		</script>
	</body>
</html>
```

Let's assume that we previously created a new experiment as described in Part 2, and that this experiment will be of type *demo_exp_type_1*. The Url for this experiment -- **this is the link you will give to participants** -- depends on both the experiment type and the experiment *short_id*:
```
http://my-psycloud-server.appspot.com/experiment/<experiment_type>/<experiment_short_id>
```
We can find the experiment short_id either by listing the experiments using the python client, or using the web dashboard. In our example, the *short_id* is:
```python
short_id = "NjNhOGUwMzgtZWRk"
```
and so the Url for the experiment is:

```
http://my-psycloud-server.appspot.com/experiment/demo_exp_type_1/NjNhOGUwMzgtZWRk
```

Here is what happens when we navigate to this Url in a browser, and the *index.html* template code is rendered by the server:
```html
<html>
	<head>
		<title>Psycloud JavaScript Client Demo</title>
	</head>
	<body>

		<script>
			var expId = "NjNhOGUwMzgtZWRk";
			var expKind = "demo_exp_type_1";

			var expJsDir = "/experiments/demo_exp_type_1/js/"
			var expResourceDir = "/experiments/demo_exp_type_1/resources/"
		</script>

		<!-- jQuery -->
		<script src="/js/jquery.min.js"></script>
		
		<!-- PsycloudJS -->
		<script src="/js/PsycloudJS/psycloud.js"></script>

		<script>
		 	participant = new StandardParticipant(expId, "../../");
		</script>
	</body>
</html>
```

A number of useful JavaScript variables have been automatically defined in the *index.html* file. The most important is the creation of the *participant* JavaScript client which you will use to interact with the psycloud server (details on using the JS client are in Part 5).

The other important variables are expJsDir (the relative path to the JS code for your experiment) and expResourceDir (the relative path to other resources for your experiment such as images, html, etc.)

In your psycloud server directory, you will need to go to ./static/experiments/ and create a new subfolder for your experiment type. You will find that there are already folders for the demo experiment types. Each of these experiment type folders then contain additional subfolders for JavaScript and other resources.

To summarize, in the case of an experiment of type *demo_exp_type_1*, the main Html for the front end (with template code) goes in the following path on psycloud server:
```
templates/experiments/demo_exp_type_1/index.html
``` 
Your custom JavaScript code for the experiment front end, and also additional resources such as stimuli images, etc would go in the following paths on psycloud server:
```
static/experiments/demo_exp_type_1/js/
static/experiments/demo_exp_type2/resources/
```
You can reference your JavaScript files and resources from within the main *index.html* file using the relative path variables that were created for you: *expJsDir* and *expResourceDir*.


**Note:** Once you have added or modified folders or files in the templates/ or static/ folders you will need to push the updates to AppEngine:
```
appcfg.py update /local/path/to/psycloud/server/
```


###Part 5: Using PsycloudJS JavaScript client

While creating the custom Html and JavaScript for your experiment front-end, you can use the *participant* object -- which is the psycloud JavaScript client -- that was created in the main *index.html* template. This section outlines the basic functionality of this object.

**participant.register**(*coupon*)

**participant.get_stimuli**()

**participant.save_stimuli**(*stimuli*)

**participant.get_stimulus**(*stimulusIndex*)

**participant.save_stimulus**(*stimulusIndex*, *stimulus*)

**participant.get_responses**()

**participant.save_responses**(*responses*)

**participant.get_response**(*stimulusIndex*)

**participant.save_response**(*stimulusIndex*, *response*)

**participant.get_current_stimulus**()

**participant.set_current_stimulus**(*stimulusIndex*)

**participant.get_max_stimulus_count**()

**participant.get_status**()

**participant.set_status**(*status*)

**participant.get_details**()

**participant.set_details**(*details*)

**participant.get_confirmation_code**()



#### A Quick JavaScript Client Demo
This quick tutorial demonstrates the creation of a new experiment with preallocated participants using JSON config file. It then shows how to use the Psycloud JavaScript client to interact with the server.

First we create a new exeriment, *myexperiment*, and then get a list of all the experiments in order to find the *short_id*. The experiment is created using the *seeing-stimset.json* configuration file that can be found [here](https://github.com/seantauber/psycloud-python/tree/master/sample_data) in the psycloud-python repository.

```python
In [16]: admin_client.create_experiment_with_participants('myexperiment', json_file="seeing-stimset.json")
Out[16]: u'ag5zfnBzeWNsb3VkZGVtb3IXCxIKRXhwZXJpbWVudBiAgICA3pCBCgw'

In [17]: admin_client.get_experiment_list()
Out[17]: 
[{u'creation_time': u'Thu, 04 Dec 2014 01:49:52 GMT',
  u'experiment_name': u'myexperiment',
  u'experiment_type': u'standard',
  u'id': u'ag5zfnBzeWNsb3VkZGVtb3IXCxIKRXhwZXJpbWVudBiAgICA3pCBCgw',
  u'num_participants': 100,
  u'short_id': u'OGZjM2FkNjQtM2U2'},
 {u'creation_time': u'Wed, 03 Dec 2014 04:05:08 GMT',
  u'experiment_name': u'demo-exp-without-stimuli',
  u'experiment_type': u'standard',
  u'id': u'ag5zfnBzeWNsb3VkZGVtb3IXCxIKRXhwZXJpbWVudBiAgICA-O2dCgw',
  u'num_participants': 200,
  u'short_id': u'NjNhOGUwMzgtZWRk'}]
```

We will use the *demo_exp_type_1* type for our experiment, and above you can see that the *short_id* is *'OGZjM2FkNjQtM2U2'*. Therefore, the Url for the experiment is,
```
http://my-psycloud-server.appspot.com/experiment/demo_exp_type_1/OGZjM2FkNjQtM2U2
```
Replace all of the values in the above Url with your own values, and navigate to this Url in your web browser (Chrome recommended).

The webpage will be blank, but you can open the JavaScript console in order to test out the Psycloud JavaScript client. Below is a JavaScript console session.

```javascript

> participant
< StandardParticipant {expId: "OGZjM2FkNjQtM2U2", baseUrl: "../../", registered: false, endpoint: Object, urlFor: function…}

> participant.register('fake-turk-id-000');
< Paticipant registered.
< undefined

> current_stim = participant.get_current_stimulus();
< 0

> stim = participant.get_stimulus(current_stim);
< Object {creation_time: "Thu, 04 Dec 2014 01:49:55 GMT", stimulus_index: 0, stimulus_type: "circle_star_scene", variables: Object}

> stim.variables
< Object {T: 0, X: 232}

> response = {variables:{resp:0, reactionTime:200}};
< Object {variables: Object}

> participant.save_response(current_stim, response);
< Object {creation_time: "Thu, 04 Dec 2014 02:33:19 GMT", stimulus_index: 0, variables: Object}

> saved_resp = participant.get_response(current_stim);
< Object {creation_time: "Thu, 04 Dec 2014 02:33:19 GMT", stimulus_index: 0, variables: Object}

> saved_resp.variables
< Object {reactionTime: 200, resp: 0}

> current_stim = participant.set_current_stimulus(current_stim+1);
< 1

> stim = participant.get_stimulus(current_stim);
< Object {creation_time: "Thu, 04 Dec 2014 01:49:55 GMT", stimulus_index: 1, stimulus_type: "circle_star_scene", variables: Object}

> stim.variables
< Object {T: 90, X: 45}

> participant.get_response(1)
< 500 (Internal Server Error)
< undefined

> participant.save_response(current_stim, response)
< Object {creation_time: "Thu, 04 Dec 2014 02:35:42 GMT", stimulus_index: 1, variables: Object}

> num_stim = participant.get_max_stimulus_count();
< 49

> participant.get_details();
< null

> participant.set_details({sex:'F', age:30, country:'USA'});
< Object {age: 30, country: "USA", sex: "F"}

> participant.get_details();
< Object {age: 30, country: "USA", sex: "F"}

> participant.get_status()
< "ACTIVE"

> conf_code = participant.get_confirmation_code();
< "NTdmOWNiMjQtZDlj"

> participant.set_status('COMPLETED');
< "COMPLETED"

> participant.get_status()
< "COMPLETED"

```

###Part 6: Downloading Experiment Data

The easiest way to download data for all completed participants is through the web admin dashboard. Login to the dashboard and then find the row for the experiment for which you would like to download data. Click the number indicating the number of participants in the "Completed" column. This will bring up a list of completed participants. Click the link for "Download Data" and save as a ```.json``` file.

####Reformating the data
The JSON file containing your data is in an inconvenient format for data analysis. The psycloud python client comes with a utility for reformatting these files. 

The [pyscloud_python repo](https://github.com/seantauber/psycloud-python/tree/master/psycloud_python) has a utility called ```expadmin.py```. Assuming your data is in a file called ```mydata.json```, you can convert it using the command line like this:
```
python expadmin.py json_results_to_csv mydata.json mydata.csv 
```

Alternatively, you can use the python shell:
```python
from psycloud_python import expadmin

expadmin.json_results_to_csv(['mydata.json', 'mydata.csv'])
```

If you would like to try this out on some preexisting data, there is a demo data file [here](https://github.com/seantauber/psycloud-python/blob/master/sample_data/psychic-results.json).


###Appendix A: Formating the Experiment Configuration JSON File

The JSON file used for preallocating participants and stimuli consists of a series of nested key-value dictionaries. The top level dictionary has the following format:
```python
{
'experiment_name': experiment_name,
'num_participants': number_of_participants,
'participants': list_of_participants
}
```
Each item in the ```list_of_participants``` is a dictionary with the format:
```python
{
'participant_index': participant_index,
'stimuli_count': number_stimuli,
'stimuli': list_of_stimuli
}
```
Each item in the ```list_of_stimuli``` is a dictionary with the format:
```python
{
'stimulus_index': stimulus_index,
'stimulus_type': stimulus_type_label,
'variables': dictionary_of_variables
}
```
Each stimulus_type can correspond to an html template or javascript function that renders that stimuli. This allows for a mixture of stimulus types within an experiment and provides a great deal of flexibility when implementing new experiments.

Each item in the ```dictionary_of_variables``` is a key-value pair, where each key is the name of a variable. The value for each key corresponds to the variable's value and can be scalar or a list. There can be any number of key value pairs, each representing a variable. In the example below there are three variables, ```X```, ```Y``` and ```responseTime```, where ```Y``` is a vector and ```X```, ```Z``` are scalar values. The variables can be anything, it's up to you to handle them properly in your front-end experiment code.
```python
{
'Y': [1,2,3,4,5,'six'],
'X': 'scalarvalue',
'responseTime': 200
}
```

The following sample config files are provided in the [psycloud_python github repo](https://github.com/seantauber/psycloud-python/tree/master/sample_data)
```
seeing-stimset.json
psychic-stimset.json
mammals-stimset.json
```

