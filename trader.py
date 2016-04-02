#!/usr/bin/python3
# -*- coding: utf-8 -*-

from urllib.request import urlopen
#import urllib
import os
import statistics
# Console colors
W = '\033[0m'  # white (normal)
R = '\033[31m'  # red
G = '\033[32m'  # green
O = '\033[33m'  # orange
B = '\033[34m'  # blue
P = '\033[35m'  # purple
C = '\033[36m'  # cyan
GR = '\033[37m'  # gray

Wb = '\033[1m'  # white (normal)
Rb = '\033[1;31m'  # red
Gb = '\033[1;32m'  # green
Ob = '\033[1;33m'  # orange
Bb = '\033[1;34m'  # blue
Pb = '\033[1;35m'  # purple
Cb = '\033[1;36m'  # cyan
GRb = '\033[1;37m'  # gray

DATAPATH = "./dane/"
PERIOD = 248 * 5 #248 dni (rok) razy 10 lat

class Index:

    def __init__(self,config):
        self.config = config

    def __convertDays(self,period):
        Y = 248 #ilość dni notowań w roku
        M = 21 #ilość dni notowań w miesiącu
        y = (period - period%Y)/Y
        m = ((period - y * Y) -(period - y * Y)%M)/M
        d = period - (y * Y + m * M)
        w = ""
        if y > 0: w+=str(int(y))+"r"
        if m > 0: w+=str(int(m))+"m"
        w+=str(int(d))+"d"
        return w

    def setColumns(self,columns):
        self.columns = columns#.copy()

    def getColumn(self,name):
        return self.columns[name]

    def getName(self):
        return self.config["NAZWA"]
    
    def getLastValue(self,name):
        '''Wartość ostatniego notowania'''
        return self.columns[name][len(self.columns[name])-1]
    
    def getMinValue(self,name):
        '''Minimalna wartość w całym PERIOD'''
        return min(self.columns[name][-1*PERIOD:])

    def getMaxValue(self,name):
        '''Maksymalna wartość w całym PERIOD'''
        return max(self.columns[name][-1*PERIOD:])

    def getWhenWasLess(self,name,value):
        '''Jak dawno temu było taniej od ceny value w całym znanym okresie'''
        i=0
        for r in reversed(self.columns[name]):
            if(r < value):
                return self.__convertDays(i)
            i=i+1
        return '0d'

    def getWhenWasMore(self,name,value):#jak dawno było tak drogo lub drożej
        '''Jak dawno temu było drożej od ceny value w całym znanym okresie'''
        i=0
        for r in reversed(self.columns[name]):
            if(r > value):
                return self.__convertDays(i)
            i=i+1
        return '0d'

    def getChange(self,name):
        '''Ostatnia procentowa zmiana ceny'''
        change = self.columns[name][len(self.columns[name])-1] - self.columns[name][len(self.columns[name])-2]
        change = 100 * change/self.columns[name][len(self.columns[name])-2]
        return change

    def getAverage(self,name):
        '''Średnia arytmetyczna'''
        return statistics.mean(self.columns[name][-1*PERIOD:])

    def getMedian(self,name):
        '''Mediana'''
        return statistics.median(self.columns[name][-1*PERIOD:])

    def getStdPeriod(self,name):
        '''Odchylenie standardowe dla PERIOD'''
        return 100*statistics.stdev(self.columns[name][-1*PERIOD:])

    def getStd(self,name):
        '''Odchylenie standardowe dla PERIOD'''
        return statistics.stdev(self.columns[name])

class Presenter:
    def __init__(self,indexes):
        self.indexes = indexes

    def showMain(self):
        print('\033[1;47;30m{:^10}\t{:^10}{:^8}{:^9}{:^9}{:^9}{:^9}{:^9}{:^9}{:^9}'.format('NAME','DATE','CHANGE%','CLOSE','MIN','MAX','MINTIME','MAXTIME','AVERAGE%','MEDIAN%') + W)
        for index in self.indexes:
            line = W
            line += '{:<10}\t{:^10}'.format(index.getName(),index.getLastValue('Data'))
            if index.getChange('Zamkniecie') > 0: line+=G
            elif index.getChange('Zamkniecie') < 0: line+=R
            else: line+=W
            line += '{:>7.2f}%'.format(index.getChange('Zamkniecie'))
            
            line += W + '{:>9.2f}{:>9.2f}{:>9.2f}{:>9}{:>9}{:>8.2f}%{:>8.2f}%{:>9.2f}%'.format(
                                            index.getLastValue('Zamkniecie'),
                                            index.getMinValue('Zamkniecie'),
                                            index.getMaxValue('Zamkniecie'),
                                            index.getWhenWasLess('Zamkniecie',index.getLastValue('Zamkniecie')),
                                            index.getWhenWasMore('Zamkniecie',index.getLastValue('Zamkniecie')),
                                            100*index.getLastValue('Zamkniecie')/index.getAverage('Zamkniecie'),
                                            100*index.getLastValue('Zamkniecie')/index.getMedian('Zamkniecie'),
                                            index.getStdPeriod('Zamkniecie')/index.getAverage('Zamkniecie')#współczynnik zmienności 
                                            #index.getStd('Zamkniecie')
                                           )
            print(line)
        print(W)

class Loader:
    def __init__(self, configs):
        self.configs = configs

    def getIndexes(self, fromNet):
        indexes = []
        if fromNet == None:
            answer = input("Czy pobrać aktualne dane?[t/N]:") 
            if answer.upper() == "T":
                self.fromNet = True
            else:
                self.fromNet = False

        for c in self.configs:
            print(c["NAZWA"])
            if self.fromNet and len(c["URL"]) > 0:
                f = urlopen(c["URL"]).read()
                open(DATAPATH + c["NAZWA"] + ".csv",'wb').write(f)
            f = open(DATAPATH + c["NAZWA"] + ".csv", 'r').read()
            self.columns = {}
            self.colName = {}
            j=0
            i=0
            for row in f.rsplit():
                if j==0:
                    for r in row.split(';'):#Tworzę columns
                        self.columns[r] = []
                        self.colName[i]= r
                        i=i+1
                else:#Wypełniam columns danymi    
                    i=0
                    for r in row.rsplit(';'):
                        if self.colName[i] == 'Data':
                            (self.columns[self.colName[i]]).append(r)
                        else:
                            (self.columns[self.colName[i]]).append(float(r))
                        i=i+1
                j=j+1
            index = Index(c)
            index.setColumns(self.columns)
            indexes.append(index)
        return indexes

#==============================================================================================

if __name__=='__main__':
    configs = [
                #{"NAZWA": "TEST","URL" : ""},http://stooq.pl/q/d/l/?s=kom&i=d&c=1
                #{"NAZWA": "KOMPU","URL" : "http://stooq.pl/q/d/l/?s=kom&i=d&c=1"},
                {"NAZWA":"CHFPLN","URL":"http://stooq.pl/q/d/l/?s=chfpln&i=d&c=1"},
                {"NAZWA":"WIG20","URL":"http://stooq.pl/q/d/l/?s=wig20&i=d&c=1"},
                {"NAZWA":"ZŁOTO","URL":"http://stooq.pl/q/d/l/?s=gc.f&i=d&c=1"},
                {"NAZWA":"SREBRO","URL":"http://stooq.pl/q/d/l/?s=xagusd&i=d&c=1"},
                {"NAZWA":"MIEDŹ","URL":"http://stooq.pl/q/d/l/?s=ca_c.f&i=d&c=1"},
                {"NAZWA":"ROPA","URL":"http://stooq.pl/q/d/l/?s=sc.f&i=d&c=1"},
                {"NAZWA":"GAZ","URL":"http://stooq.pl/q/d/l/?s=ng.f&i=d&c=1"},
                {"NAZWA":"KAWA","URL":"http://stooq.pl/q/d/l/?s=kc.f&i=d&c=1"},
                {"NAZWA":"KAKAO","URL":"http://stooq.pl/q/d/l/?s=cc.f&i=d&c=1"},
                {"NAZWA":"CUKIER","URL":"http://stooq.pl/q/d/l/?s=sb.f&i=d&c=1"}
    ]

    os.system('clear')
    loader = Loader(configs)
    indexes = loader.getIndexes(None)
    os.system('clear')
    presenter = Presenter(indexes)
    presenter.showMain()
