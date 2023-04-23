# a module for gathering statistics for a symbol

import json
import time

def stat(tr, time_in):
    #time_in = int(time.time_ns() / 1000.0)
    latency = time_in - tr.timestamp
    return [time_in, latency, tr.__dict__()]

class Statistics:
    def __init__(self, symbol):
        self.symbol = symbol
        self.events = []

    def push(self, tr):
        time_in = int(time.time_ns() / 1000.0)
        latency = time_in - tr.timestamp
        self.events.append((time_in, latency, tr))

    def __dict__(self) -> dict:
        return {
            'symbol': self.symbol,
            'events': self.events
        };

    def __repr__(self) -> str:
        return repr(self.__dict__())
    
class StatisticsEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Statistics):
            return obj.__dict__()
        return json.JSONEncoder.default(self, obj)


class StatisticsRepo:
    def __init__(self):
        self.statistics = {}

    def __dict__(self) -> dict:
        return self.statistics

    def __repr__(self) -> str:
        return repr(self.__dict__())

    def statistics_for(self, symbol):
        try:
            return self.statistics[symbol]
        except KeyError:
            self.statistics[symbol] = statistics = Statistics(symbol)
            return statistics

    def push(self, tr):
        if isinstance(tr.symbol, bytes):
            tr.symbol = tr.symbol.decode()

        statistics = self.statistics_for(tr.symbol)
        statistics.push(tr)
    
    def dump(self):
        print(self.statistics)
        return json.dumps(self.statistics, indent = 4)
