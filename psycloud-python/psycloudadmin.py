import sys
from psycloud.utils import PsycloudJsonResultsReader
import pandas as pd


def json_results_to_csv(args):

	json_filename, csv_filename = args

	reader = PsycloudJsonResultsReader(json_filename)
	reader.to_csv(csv_filename)


commands = {}
commands['json_results_to_csv'] = json2csv


if __name__ == "__main__":

	cmd = sys.argv[1]
	args = sys.argv[2:]

	if cmd in commands:
		commands[cmd](args)

