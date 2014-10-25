import sys
from psycloudtools import PsycloudJsonResultsReader
import pandas as pd

def json_to_csv(json_filename, csv_filename):

	reader = PsycloudJsonResultsReader(json_filename)
	reader.to_csv(csv_filename)


if __name__ == "__main__":

	json_to_csv(sys.argv[1], sys.argv[2])
