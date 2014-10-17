// Psycloud Javascript Client


function Participant(expId, baseUrl) {

	this.expId = expId;
	this.baseUrl = baseUrl;

	if ( this.expId in sessionStorage ){
		this.participantId = sessionStorage[this.expId];
		this.registered = true;
	} else {
		this. registered = false;
	}

	this.endpoint = {};
	this.endpoint['participant'] = 'psycloud/api/participant/';
	this.endpoint['details'] = 'psycloud/api/participant/<part_id>/details/';
	this.endpoint['current_status'] = 'psycloud/api/participant/<part_id>/current_status/';
	this.endpoint['confirmation_code'] = 'psycloud/api/participant/<part_id>/confirmation_code/';

	
	this.urlFor = function(endpointName, params){

		params = params || {};

		url = this.baseUrl + this.endpoint[endpointName];
		url = url.replace('<part_id>', this.participantId);
		
		if ('stimulusIndex' in params){
			url = url.replace('<stim_id>', params.stimulusIndex);
		}
		
		return url;
	};


	this.register = function(coupon) {

		var participant = this;

		if ( participant.registered ){
			console.log("Participant is already registered.");
		}
		else{

			url = participant.urlFor('participant');

			data = {experiment_id: participant.expId};
			if (coupon !== undefined) {
				participant.registrationCoupon = coupon;
				data['registration_coupon'] = coupon;
			}

			$.ajax({
			    type: "POST",
			    url: url,
			    data: JSON.stringify(data),
			    contentType: "application/json; charset=utf-8",
			    dataType: "json",
			    async: false,
			    cache: false,
			    success: function(data){
			    	participant.participantId = data.result.participant_id;
			    	participant.registered = true;
			    	// persist the registration for the session
			    	sessionStorage[participant.expId] = participant.participantId;
			    	console.log("Paticipant registered.");
			    },
			    error: function(errMsg) {
			        console.log("Participant registration failed.");
			        console.log(errMsg);
			    }
			});

		}
	};


	this.get_status = function() {

		var participant = this;
		var status;

		if ( participant.registered ) {

			url = participant.urlFor('current_status');

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	status = data.result.current_status;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return status;

		} else {
			console.log('Unable to get current status because participant is not registered.')
		}

	};

	this.set_status = function(status) {

		var participant = this;
		var savedStatus;

		if ( participant.registered ) {

			url = participant.urlFor('current_status');

			$.ajax({
			    type: "PUT",
			    url: url,
			    data: JSON.stringify( {current_status: status} ),
			    contentType: "application/json; charset=utf-8",
			    dataType: "json",
			    async: false,
			    cache: false,
			    success: function(data){
			    	savedStatus = data.result.current_status;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return savedStatus;

		} else {
			console.log('Unable to save status because participant is not registered.')
		}

	};



	this.get_details = function() {

		var participant = this;
		var details;

		if ( participant.registered ) {

			url = participant.urlFor('details');

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	details = data.result.details;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return details;

		} else {
			console.log('Unable to get details because participant is not registered.')
		}

	};

	this.set_details = function(details) {

		var participant = this;
		var savedDetails;

		if ( participant.registered ) {

			url = participant.urlFor('details');

			$.ajax({
			    type: "PUT",
			    url: url,
			    data: JSON.stringify( {details: details} ),
			    contentType: "application/json; charset=utf-8",
			    dataType: "json",
			    async: false,
			    cache: false,
			    success: function(data){
			    	savedDetails = data.result.details;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return savedDetails;

		} else {
			console.log('Unable to save details because participant is not registered.')
		}

	};


	this.get_confirmation_code = function() {

		var participant = this;
		var confCode;

		if ( participant.registered ) {

			url = participant.urlFor('confirmation_code');

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	confCode = data.result.confirmation_code;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return confCode;

		} else {
			console.log('Unable to get confirmation code because participant is not registered.')
		}

	};

}



function StandardParticipant(expId, baseUrl) {

	Participant.call(this, expId, baseUrl);

	this.endpoint['stimuli'] = 'psycloud/api/participant/<part_id>/stimuli/';
	this.endpoint['stimulus'] = 'psycloud/api/participant/<part_id>/stimuli/<stim_id>';
	this.endpoint['responses'] = 'psycloud/api/participant/<part_id>/responses/';
	this.endpoint['response'] = 'psycloud/api/participant/<part_id>/responses/<stim_id>';
	this.endpoint['max_stimulus_count'] = 'psycloud/api/participant/<part_id>/stimuli/max_count/';
	this.endpoint['current_stimulus'] = 'psycloud/api/participant/<part_id>/stimuli/current/';


	this.get_stimuli = function() {

		var participant = this;
		var stimuli;

		if ( participant.registered ) {

			url = participant.urlFor('stimuli');

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	stimuli = data.result.stimuli;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return stimuli;

		} else {
			console.log('Unable to get stimuli because participant is not registered.')
		}

	};

	this.save_stimuli = function(stimuli) {

		var participant = this;
		var savedStimuli;

		if ( participant.registered ) {

			url = participant.urlFor('stimuli');

			$.ajax({
			    type: "POST",
			    url: url,
			    data: JSON.stringify(stimuli),
			    contentType: "application/json; charset=utf-8",
			    dataType: "json",
			    async: false,
			    cache: false,
			    success: function(data){
			    	savedStimuli = data.result.stimuli;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return savedStimuli;

		} else {
			console.log('Unable to save stimuli because participant is not registered.')
		}

	};


	this.get_stimulus = function(stimulusIndex) {

		var participant = this;
		var stimulus;

		if ( participant.registered ) {

			url = participant.urlFor('stimulus', {stimulusIndex: stimulusIndex});

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	stimulus = data.result.stimulus;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return stimulus;

		} else {
			console.log('Unable to get stimulus because participant is not registered.')
		}

	};

	this.save_stimulus = function(stimulusIndex, stimulus) {

		var participant = this;
		var savedStimulus;

		if ( participant.registered ) {

			url = participant.urlFor('stimulus', {stimulusIndex: stimulusIndex});

			$.ajax({
			    type: "POST",
			    url: url,
			    data: JSON.stringify(stimulus),
			    contentType: "application/json; charset=utf-8",
			    dataType: "json",
			    async: false,
			    cache: false,
			    success: function(data){
			    	savedStimulus = data.result.stimulus;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return savedStimulus;

		} else {
			console.log('Unable to save stimulus because participant is not registered.')
		}

	};



	this.get_responses = function() {

		var participant = this;
		var responses;

		if ( participant.registered ) {

			url = participant.urlFor('responses');

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	responses = data.result.responses;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return responses;

		} else {
			console.log('Unable to get responses because participant is not registered.')
		}

	};

	this.save_responses = function(responses) {

		var participant = this;
		var savedResponses;

		if ( participant.registered ) {

			url = participant.urlFor('responses');

			$.ajax({
			    type: "POST",
			    url: url,
			    data: JSON.stringify(responses),
			    contentType: "application/json; charset=utf-8",
			    dataType: "json",
			    async: false,
			    cache: false,
			    success: function(data){
			    	savedResponses = data.result.responses;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return savedResponses;

		} else {
			console.log('Unable to save responses because participant is not registered.')
		}

	};


	this.get_response = function(stimulusIndex) {

		var participant = this;
		var response;

		if ( participant.registered ) {

			url = participant.urlFor('response', {stimulusIndex: stimulusIndex});

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	response = data.result.response;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return response;

		} else {
			console.log('Unable to get response because participant is not registered.')
		}

	};

	this.save_response = function(stimulusIndex, response) {

		var participant = this;
		var savedResponse;

		if ( participant.registered ) {

			url = participant.urlFor('response', {stimulusIndex: stimulusIndex});

			$.ajax({
			    type: "POST",
			    url: url,
			    data: JSON.stringify(response),
			    contentType: "application/json; charset=utf-8",
			    dataType: "json",
			    async: false,
			    cache: false,
			    success: function(data){
			    	savedResponse = data.result.response;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return savedResponse;

		} else {
			console.log('Unable to save response because participant is not registered.')
		}

	};



	this.get_current_stimulus = function() {

		var participant = this;
		var stimulusIndex;

		if ( participant.registered ) {

			url = participant.urlFor('current_stimulus');

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	stimulusIndex = data.result.stimulus_index;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return stimulusIndex;

		} else {
			console.log('Unable to get current stimulus because participant is not registered.')
		}

	};

	this.set_current_stimulus = function(stimulusIndex) {

		var participant = this;
		var savedStimulusIndex;

		if ( participant.registered ) {

			url = participant.urlFor('current_stimulus');

			$.ajax({
			    type: "PUT",
			    url: url,
			    data: JSON.stringify( {stimulus_index: stimulusIndex} ),
			    contentType: "application/json; charset=utf-8",
			    dataType: "json",
			    async: false,
			    cache: false,
			    success: function(data){
			    	savedStimulusIndex = data.result.stimulus_index;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return savedStimulusIndex;

		} else {
			console.log('Unable to set current stimulus because participant is not registered.')
		}

	};


	this.get_max_stimulus_count = function() {

		var participant = this;
		var maxStimulusCount;

		if ( participant.registered ) {

			url = participant.urlFor('max_stimulus_count');

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	maxStimulusCount = data.result.max_count;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return maxStimulusCount;

		} else {
			console.log('Unable to get max stimulus count because participant is not registered.')
		}

	};

}



function IteratedParticipant(expId, baseUrl) {

	Participant.call(this, expId, baseUrl);

	this.endpoint['chain_types'] = 'psycloud/api/participant/<part_id>/chain_types/';
	

	this.get_chain_types = function() {
		var participant = this;
		var chainTypes;

		if ( participant.registered ) {

			url = participant.urlFor('chain_types');

			$.ajax({
			    type: "GET",
			    url: url,
			    async: false,
			    cache: false,
			    success: function(data){
			    	chainTypes = data.result.chain_types;
			    },
			    error: function(errMsg) {
			        console.log(errMsg);
			    }
			});

			return chainTypes;

		} else {
			console.log('Unable to get chain types because participant is not registered.')
		}
	};

}



var sampleStim = {stimulus_index:0, variables:{a:[1,2,3], b:100}, stimulus_type:'stim'};
var sampleResp = {stimulus_index:0, variables:{y:['a','b','c'], z:false} };


