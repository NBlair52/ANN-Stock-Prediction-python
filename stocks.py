#IMPORTS
from csv import reader, Error
from datetime import date, timedelta
from pybrain import RecurrentNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.structure import LinearLayer, TanhLayer, FullConnection
from pybrain.supervised.trainers import BackpropTrainer
from random import gauss
from urllib import urlretrieve, ContentTooShortError

from stock_week import Stock_Week, Stock_Day

#GLOBALS
STOCK_TICKS = ['GOOG', 'AAPL']                ##Stocks to look up, Might change this later to be a file to read in
PARAMETERS_NAME = ['Start', 'High', 'Low', 'End', 'Ave_volume', 'sMA', 'gMA']
PARAMETERS_NUM = len(PARAMETERS_NAME)
MIDDLE_NUM = PARAMETERS_NUM                           ##Not sure how many to use.  Ballance memory and compuation power?
LAYERS_NUM = 5                                           ##Not sure how many to use.  Ballance memory and compuation power?
BACK_SAMPLES_NUM = 12                                     ##Not sure how many to use.
DELTA_CUTOFF = 0.0001                                     ##Not sure what level.

URL_BASE = 'http://ichart.finance.yahoo.com/table.csv?s=' 
OUTPUT_BASE = 'C:\Python27\ANN-Stock-Prediction'

TODAY = date.today()
ONE_DAY = timedelta(days=1)
ONE_WEEK = 7 * ONE_DAY

#FUNCTIONS
# Functions to manipulate days of the week
def last_friday(today):
    """ Input:  date object
        Output: date object for the previous Friday
    """
    while (today.weekday() != 4):
        today -= ONE_DAY
    return today

def last_monday(today):
    """ Input:  date object
        Output: date object for the previous Monday
    """
    while (today.weekday() != 0):
        today -= ONE_DAY
    return today

def str2date(string):
    """ Input:  string
        Output: date object parsed from that string
    """
    try:
        year, month, day = int(string[0:4]), int(string[5:7]), int(string[8:10])
        return date(year, month, day)
    except ValueError as e:
        return 0

# Functions to get data from online
def make_url(stock):
    """ Input:  String stock ticker
        Output: String of URL to request stock data
    """
    return URL_BASE + stock

def make_filename(stock, directory='Stock_Data'):
    """ Input:  String stock ticker, String dorectory to place stock data
        Output: String of URL to request stock data
    """
    return OUTPUT_BASE + '\\' + directory + '\\' + stock + '.csv'

def get_data(stock):
    """ Input:  String stock ticker
        Function retrieves stock data from online and saves into a .csv
    """
    try:
        urlretrieve(make_url(stock),make_filename(stock))
    except ContentTooShortError as e:
        outfile = open(make_filename(stock), 'w')
        outfile.write(e.content)
        outfile.close

# Functions to extract financial data
def extract_row(stock, day):
    """ Input:  String stock ticker to get data, date object for day to get data
        Output: String line of stock data
    """
    infile = open(make_filename(stock), 'r')
    stock_reader = reader(infile)
    for row in stock_reader:
        if (str2date(row[0]) == day):
            return row
    return '-1'

def package_day(row):
    if (row == '-1'):
        return '-1'
    return Stock_Day(str2date(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]))

def package_week(stock, day):
    """ Input:  String stock ticker to get data, date object for Friday of week to get daya
        Output: String tupple of each day's data
    """
    friday    = package_day(extract_row(stock, day - 0 * ONE_DAY))
    thursday  = package_day(extract_row(stock, day - 1 * ONE_DAY))
    wednesday = package_day(extract_row(stock, day - 2 * ONE_DAY))
    tuesday   = package_day(extract_row(stock, day - 3 * ONE_DAY))
    monday    = package_day(extract_row(stock, day - 4 * ONE_DAY))
    week = Stock_Week(monday, tuesday, wednesday, thursday, friday)
    return week

#def compute_metrics(week):
#    #do some shit on the week, return that shit
#    return gauss(50, 25), gauss(0, 3)

# Functions to setup and load network and dataSet
def setup_network(input_num, middle_num, layers, output_num):
    network = RecurrentNetwork()
    network.addInputModule(LinearLayer(input_num, 'in'))
    name_prev, name_curr = 'in', 'mid1'
    for i in range (1, layers + 1):
        network.addModule(TanhLayer(middle_num, name_curr))
        network.addConnection(FullConnection(network[name_prev], network[name_curr], name='F'+name_prev+'-'+name_curr))
        if (i != 1):
            network.addRecurrentConnection(FullConnection(network[name_curr], network[name_curr], name='R'+name_curr))
        name_prev, name_curr = name_curr, 'mid' + str(i+1)
    network.addOutputModule(LinearLayer(output_num, 'out'))
    network.addConnection(FullConnection(network[name_prev], network['out'], name='F'+name_prev+'-out'))
    network.sortModules()
    #make fast
    return network

def setup_dataSet(stock):
    friday = last_friday(TODAY)
    current_week_metrics = package_week(stock, friday).compute_metrics()

    friday = last_friday(friday - ONE_DAY)
    week_present = package_week(stock, friday)
    while (week_present.num_days == 0):
        friday = last_friday(friday - ONE_DAY)
        week_present = package_week(stock, friday)

    dataSet = SupervisedDataSet(PARAMETERS_NUM, 1)
    for weeks in range (BACK_SAMPLES_NUM):
        friday -= ONE_WEEK
        week_past = package_week(stock, friday)
        if (week_past.num_days !=0):
            dataSet.addSample(week_past.compute_metrics(), week_present.percent_change)
            week_present = week_past

    return current_week_metrics, dataSet

#MAIN
def main():
    for stock in STOCK_TICKS:
        # Get offline
        get_data(stock)

        # Add to data set
        current_week_metrics, dataSet = setup_dataSet(stock)

        # Train network
        network = setup_network(PARAMETERS_NUM, MIDDLE_NUM, LAYERS_NUM, 1)
        trainer = BackpropTrainer(network, dataSet)
        delta, error_prev, error_curr = 1, 1, 1
        while delta > DELTA_CUTOFF:
            error_prev = error_curr
            error_curr = trainer.train()
            delta = abs((error_prev - error_curr) / error_prev)
        #trainer.trainUntilConvergence() this one seems to take too long

        output = network.activate(current_week_metrics)
        print stock + ': ' + str(output)

if __name__ == "__main__":
    main()
