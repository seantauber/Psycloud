import numpy as np
import pandas as pd
import json

class PsycloudJsonResultsReader:

	def __init__(self, json_filename=None, results_dict=None):
		if json_filename is not None:
			self.json_filename = json_filename
			self.read_json()
		elif results_dict is not None:
			self. results_dict = results_dict
		else:
			raise Exception('No data provided.')
		self.build_header()
		self.build_data_matrix()
		self.create_data_frame()

	def read_json(self):
		f = open(self.json_filename, 'rb')
		self.results_dict = json.load(f)
		f.close()

	def to_csv(self, fname):
		self.data_frame.to_csv(fname, index=False)

	def build_header(self):
		
		self.header = ['participant_index', 'stimulus_index', 'stimulus_type', 'response_time']

		for participant in self.results_dict['participants']:
			stimulus_vars = self.get_variable_set(participant['stimuli'])
			response_vars = self.get_variable_set(participant['responses'])

		self.header += stimulus_vars + response_vars


	def build_data_matrix(self):
		
		self.data_matrix = np.array(self.header, dtype=object).reshape([1,len(self.header)])

		for participant in self.results_dict['participants']:
			self.extract_data(participant['participant_index'], participant['stimuli'])
			self.extract_data(participant['participant_index'], participant['responses'])

	def create_data_frame(self):
		self.data_frame = pd.DataFrame(self.data_matrix[1:], columns=self.header)

	def extract_data(self, participant_index, stim_list):

		for item in stim_list:

			# Search for existing datarows with this participant/stimulus combination
			existing_data_row = self.search_by_columns(['participant_index', 'stimulus_index'],
				[participant_index, item['stimulus_index']])

			# Check if any of the rows matched the criteria
			if existing_data_row.any():
				# There was a matching row. Get the row number.
				row = existing_data_row.nonzero()[0][0]
			else:
				# There were no matching rows. Create and initialize a new row
				self.new_datarow(participant_index, item)
				row = -1

			# Extract all of the variables for this item and add them to the data matrix
			for var_name in item['variables'].keys():
				if type(item['variables'][var_name]) == list:
					for i, val in enumerate(item['variables'][var_name]):
						self.set_value(row, "%s.%i" % (var_name, i), val)
				else:
					self.set_value(row, var_name, item['variables'][var_name])


	def new_datarow(self, participant_index, item):
		# Append a new row to the data matrix
		self.data_matrix = np.vstack([ self.data_matrix, np.empty(self.data_matrix.shape[1], dtype=object)])
		row = -1 # index of the new row

		# Initialize some of the values in the new row 
		self.set_value(row, 'participant_index', participant_index)
		self.set_value(row, 'stimulus_index', item['stimulus_index'])

		# If the item has a stimulus_type then it's a stimulus and we should record the type.
		# Otherwise, it's a response and we should record the time of the response
		if 'stimulus_type' in item:
			# this is a stimulus item
			self.set_value(row, 'stimulus_type', item['stimulus_type'])
		else:
			# this is a response item
			self.set_value(row, 'response_time', item['creation_time'])

	def set_value(self, row, col_name, value):
		col = self.get_column_number(col_name)
		self.data_matrix[row, col] = value
			
	def search_by_columns(self, col_names, values):
		return np.array( [self.search_by_column(col_name, val) for col_name, val in zip(col_names, values)] ).all(axis=0)
	
	def search_by_column(self, col_name, value):
		col = self.get_column_number(col_name)
		return self.data_matrix[:, col] == value

	def get_column_number(self, col_name):
		return self.header.index(col_name)

	def get_variable_set(self, stim_list):
		var_set = set()
		for item in stim_list:
			for var in item['variables'].keys():
				if type(item['variables'][var]) == list:
					for i in range(len(item['variables'][var])):
						var_set.add("%s.%i" % (var, i))
				else:
					var_set.add(var)
		return list(var_set)
