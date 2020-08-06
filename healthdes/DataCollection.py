""" HealthDES - A python library to support discrete event simulation in health and social care """

import pandas as pd  # modin

from io import StringIO
from csv import DictWriter

# Import local libraries
# pylint: disable=relative-beyond-top-level
from .Check import CheckList


class DataCollection:
    """ Class to collect data from across the simulation

    Data collection can be period (driven by periodic simpy event process)
    or logged by other parts of the simulation.

    Data collection writes to an in-memory csv file, which may be converted to a pandas DataFrame

    """
    # TODO: Implement some form of memory management to flush in-memory csv to disk/database if
    #       memory tight
    # TODO: Apache Arrow: Consider using, however, doesn't always support windows.

    # TODO: Update parameters at init to use param dictionary.
    def __init__(self, env, simulation_name=None, simulation_run=None):
        """ Create a class to collect data within a simulation run

        Keyword parameters:
        env                 simpy environment
        simulation_name     The name for this simulation
        simulation_run      The sequence number for this run of the simulation

        """
        self.env = env
        self.simulation_name = simulation_name
        self.simulation_run = simulation_run

        # All the memory tables referenced from dictionary
        self.memory_file = {}
        self.memory_writer = {}
        self.counters = {}

    """ Template for periodic reporting

    The callback function returns a dictionary of data to be included within the report.
    The values in this dictionary must be available when the periodic reporting is initialised
    as the callback will be called to create the column headers for the report.

    def periodic_reporting_callback(self):
        ### Callback to collect data for periodic reporting ###
        return {'quanta_concentration': self.quanta_concentration}

    This method initialises the periodic report and sets the report name, callback function (above)
    and the number of time periods between data collections.

    def initialise_periodic_reporting(self):
        ### Initialise periodic reporting ###

        data_set_name = 'unique name for the report'
        callback = self.periodic_reporting_callback
        periods = 1 # Number of period between data collections

        self.dc.create_period_reporting(data_set_name, callback, periods)
    """

    def create_period_reporting(self, data_set_name, callback, periods):
        """ Register a periodic report

        Keyword parameters:
        data_set_name           The name for the data set to be recorded
        callback                Function to call periodically to collect data
        periods                 The number of periods between data collections

        Note data collection is triggered when the model first starts
        """
        CheckList.fail_if_this_key_in_the_dictionary(data_set_name, self.memory_file)

        column_dictionary = callback()
        CheckList.is_a_dictionary(column_dictionary)

        header_list = []
        for key, _ in column_dictionary.items():
            header_list.append(key)

        header_list.insert(0, 'time')
        header_list.insert(0, 'simulation_run')
        header_list.insert(0, 'simulation_name')

        # Create a new memory file into which data will be stored as CSV file
        self.memory_file[data_set_name] = StringIO()
        self.memory_writer[data_set_name] = DictWriter(self.memory_file[data_set_name],
                                                       header_list,
                                                       restval='Null',
                                                       extrasaction='raise')

        self.memory_writer[data_set_name].writeheader()

        self.env.process(self.periodic_reporting(data_set_name, callback, periods))

    def periodic_reporting(self, data_set_name, callback, periods):
        """ Add a new periodic reporting process

        Keyword parameters:
        data_set_name           The name of the dataset into which data stored
        callback                The method to call to fetch the data
        periods                 The number of periods between fetches of data
        """
        while True:
            data = callback()
            data['time'] = self.env.now
            data['simulation_run'] = self.simulation_run
            data['simulation_name'] = self.simulation_name
            self.memory_writer[data_set_name].writerow(data)

            yield self.env.timeout(periods)

    def log_reporting(self, data_set_name, column_dictionary):
        """ Log data submitted by the simulation

        Keyword parameters:
        data_set_name           The name of the dataset into which data stored
        column_dictionary       The method to call to fetch the data
         """

        CheckList.is_a_dictionary(column_dictionary)

        # If the report doesn't already exist, create a new report
        if not (data_set_name in self.memory_file):
            header_list = []
            for key, _ in column_dictionary.items():
                header_list.append(key)

            header_list.insert(0, 'time')
            header_list.insert(0, 'simulation_run')
            header_list.insert(0, 'simulation_name')

            # Create a new memory file into which data will be stored as CSV file
            self.memory_file[data_set_name] = StringIO()
            self.memory_writer[data_set_name] = DictWriter(self.memory_file[data_set_name],
                                                           header_list,
                                                           restval='Null',
                                                           extrasaction='raise')

            self.memory_writer[data_set_name].writeheader()

        # Write data to memory file
        column_dictionary['time'] = self.env.now
        column_dictionary['simulation_run'] = self.simulation_run
        column_dictionary['simulation_name'] = self.simulation_name
        self.memory_writer[data_set_name].writerow(column_dictionary)

    def counter_increment(self, data_set_name, amount=None):
        """Increment counter

        Keyword parameters:
        data_set_name           The name of the dataset into which data stored
         """
        # If the report doesn't already exist, create a new report
        if not (data_set_name in self.counters):
            self.counters[data_set_name] = 0

        amount = amount if amount else 1

        self.counters[data_set_name] += amount

    def counter_decrement(self, data_set_name, amount=None):
        """Decrement counter

        Keyword parameters:
        data_set_name           The name of the dataset into which data stored
         """
        # If the report doesn't already exist, create a new report
        if not (data_set_name in self.counters):
            self.counters[data_set_name] = 0

        amount = amount if amount else 1

        self.counters[data_set_name] -= amount

    def get_results(self, data_set_name):
        """ Return stored data as a pandas data frame """
        file = self.memory_file.get(data_set_name, None)
        df = None
        if file is not None:
            file.seek(0)
            df = pd.read_csv(file)

        return df

    def get_counter(self, data_set_name):
        """return value of a counter"""

        return self.counters.get(data_set_name, None)

    def get_list_of_reports(self):
        """ Get a list of reports

        Return: list of reports
        """
        report_list = []
        for key, _ in self.memory_file.items():
            report_list.append(key)

        return report_list
