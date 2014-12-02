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



###Part 2: Uploading and Managing Experiments


###Part 3: Downloading Experiment Data

