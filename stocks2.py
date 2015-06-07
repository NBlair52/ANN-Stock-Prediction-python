__author__ = 'Nicholas Blair'

########################################################################################################################
# IMPORTS
########################################################################################################################
from csv import reader

from datetime import date

from os import getcwd

from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import ClassificationDataSet
from pybrain.supervised.trainers import BackpropTrainer

from stock_week import Stock_Day

from urllib import urlretrieve, ContentTooShortError

########################################################################################################################
# GLOBALS
########################################################################################################################
STOCK_TICKS = ['GOOG', 'AAPL']
PARAMETERS = ['start', 'high', 'low', 'end', 'volume', 'adj_end']

INPUT_NUM = len(PARAMETERS)
MIDDLE_NUM = 100
OUTPUT_NUM = 1
MIN_SAMPLE_NUM = 200

EPOCHS_MAX = 100
########################################################################################################################
# FUNCTIONS
########################################################################################################################
def main():
    for stock in STOCK_TICKS:
        # Download Data
        get_data(stock)

        # Import Data
        days = extract_data(stock)
        today = days.pop(0)

        # Make DataSet
        data_set = ClassificationDataSet(INPUT_NUM, 1, nb_classes=2)
        for day in days:
            target = 0
            if day.change > 0:
                target = 1
            data_set.addSample(day.return_metrics(), [target])

        # Make Network
        network = buildNetwork(INPUT_NUM, MIDDLE_NUM, MIDDLE_NUM, OUTPUT_NUM)

        # Train Network
        trainer = BackpropTrainer(network)
        trainer.setData(data_set)
        trainer.trainUntilConvergence(maxEpochs=EPOCHS_MAX)

        # Activate Network
        prediction = network.activate(today.return_metrics())
        print prediction
        #print "ANN predicts that you should " + outcome + stock

########################################################################################################################
#  Functions to get data from online
########################################################################################################################
def make_url(stock):
    """
    returns the appropriate URL name to request stock data for given ticker
    :param stock: String stock ticker
    :return: String URL
    """
    return 'http://ichart.finance.yahoo.com/table.csv?s=' + stock

def make_filename(stock, directory='Stock_Data'):
    """
    function returns the appropriate file name for .csv file of stock data given ticker of stock
    :param stock: String ticker of stock
    :param directory: String name of deesired subdirectory (default 'Stock_Data')
    :return String complete file path
    """
    return getcwd() + '\\' + directory + '\\' + stock + '.csv'

def get_data(stock):
    """
    requests daily stock data from yahoo.com and saves the results in a.csv file in 'Stock_Data sub dir
    :param stock: String ticker of stock to request data for
    """
    try:
        urlretrieve(make_url(stock), make_filename(stock))
    except ContentTooShortError as e:
        outfile = open(make_filename(stock), 'w')
        outfile.write(e.content)

########################################################################################################################
# Functions to extract financial data from files
########################################################################################################################
def extract_data(stock):
    """
    Read in the .csv file (from Stock_Data sub dir) stock data into a list of Stock_Day objects
    :param stock: String ticker of stock to read data from
    :return: list Stock_Day objects for the given stock
    """
    infile = open(make_filename(stock), 'r')
    stock_reader = reader(infile)
    days = []
    row_iterator = iter(stock_reader)
    next(row_iterator)
    for row in row_iterator:
        days.append(package_day(row))
    return days

def package_day(row):
    """
    Given a row of .csv data the function returns a Stock_Day object holding that data
    :param row: String row of CSV file containing stock data, order: date, open, high, low, close, volume, adjusted end
    :return: Stock_Day object
    """
    if row == '-1':
        return '-1'
    return Stock_Day(str2date(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]))

def str2date(string):
    """
    Converts a String into appropriate date object
    :param string: String to turn into a date
    :return: date object
    """
    try:
        year, month, day = int(string[0:4]), int(string[5:7]), int(string[8:10])
        return date(year, month, day)
    except ValueError as e:
        return 0
########################################################################################################################

if __name__ == "__main__":
    main()