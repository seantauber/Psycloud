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
appcfg.py update psycloud-master
```

####Go to the experiment dashboard
Once your server has launched, you can view the experiment dashboard at http://my-psycloud-server.appspot.com/psycloud/admin/dashboard



###Part 2: Creating and Managing Experiments

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
'''
seeing-stimset.json
psychic-stimset.json
mammals-stimset.json
'''

Here is an example of how to use the python admin client to create a new experiment using the *seeing* config file:
'''python
from psycloud_python.client import PsycloudAdminClient

# Initialize the admin client

base_url="http://my-psycloud-server.appspot.com"
username="admin"
password="defaultadminpassword"

admin_client = PsycloudAdminClient(base_url, username, password)


# Create a new experiment

experiment_name = "demo_exp_with_stimuli"
json_config_file = "seeing-stimset.json"

admin_client.create_experiment(experiment_name, json_file=json_config_file)
'''
Just like in the previous example, an experiment id will be returned by the server if everything goes well.


###Part 3: Managing Experiments on the Server



###Part 4: Setup Experiment Front-End with Psycloud Server



###Part 5: Using PsycloudJS JavaScript client



###Part 6: Downloading Experiment Data

