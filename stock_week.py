def sigma(bot, top, inc=1):
    total = 0
    while (bot <= top):
        total += bot
        bot += inc
    return total

class Stock_Day():
    """
    The class to hold information about a stock's preformance on each day
    """
    
    def __init__(self, date, start, high, low, end, volume, adj_end):
        self.date = date
        self.start = start
        self.high = high
        self.low = low
        self.end = end
        self.volume = volume
        self.adj_end = adj_end

        self.spread = high - low
        self.change = (start - end) / start
    
#    def __init__(self):

class Stock_Week():
    """
    The class to hold information about a stock's preformance over a week
    """

    def __init__(self, monday, tuesday, wednesday, thursday, friday):
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.days = [monday, tuesday, wednesday, thursday, friday]
        self.starts = []
        self.highs = []
        self.lows = []
        self.ends = []
        self.volumes = []
        self.adj_ends = []
        self.spreads = []
        self.changes = []
        
        for day in self.days:
            if (day != '-1'):
                self.starts.append(day.start)
                self.highs.append(day.high)
                self.lows.append(day.low)
                self.ends.append(day.end)
                self.volumes.append(day.volume)
                self.adj_ends.append(day.adj_end)
                self.spreads.append(day.spread)
                self.changes.append(day.change)
            else :
                self.days.remove(day)

        self.num_days = len(self.days)
        if (self.num_days != 0):
            self.start = self.starts[0]
            self.end = self.ends[len(self.ends) - 1]
            self.high = max(self.highs)
            self.low = min(self.lows)
            self.volume = sum(self.volumes)
            self.spread = self.high - self.low
            self.change = self.end - self.start
            self.percent_change = self.change / self.start

    def ave_volume(self):
        return self.volume / self.num_days

    def simple_moving_average(self):
        return sum(self.ends) / self.num_days

    def geometric_moving_average(self):
        denom = sigma(1, self.num_days)
        average = 0
        i = 1
        for day in self.days:
            weight = i / denom
            average += weight * day.end
            i += 1
        return average

    def compute_metrics(self):
        return self.start, self.high, self.low, self.end, self.ave_volume(), self.simple_moving_average(), self.geometric_moving_average()
