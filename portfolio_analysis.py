#!/usr/bin/env python3
# shebang for linux

#!/usr/local/bin/python3
# shebang for mac osx

"""
portfolio analysis
program designed to answer the question 'did my portfolio beat the market?'
assesses a given stock portfolio over a given time periord and compares it
to a given index tracker using information from yahoo finance via ypython
ypython documented here: aroussi.com/post/python-yahoo-finance
cash holdings are not accounted for

INPUTS:
    - comparison indexs
    - analysis start date YYYYMMDD
    - analysis end date YYYYMMDD
    - list of:
        - stocker tickers
        - purchae date YYYYMMDD
        - sale date YYYYMMDD
        - purchase price in £ GBP
        - purchase quantity

OUTPUTS:
    - table of % gain of tickers and index and total portfolio for analysis periord
    - £ gain of tickers and index and total portfolio for analysis periord
    - daily line graph of % for all tickers and index and total portfolio for analysis periord
    - total barchart of £ gains/losses for all tickers and index and total portfolio for analysis periord
"""

# import std lib
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
# import 3rd party lib
import yfinance as yf
# import usr lib
# global var

#start debugging
import pdb
#pdb.set_trace();
DEBUG = 0;

def main():
    """
    FUNCTION DESCRIPTION
    OTHER COMMENTS
    INPUTS
    OUTPUTS
    EXAMPLES
    >>> main();
    hello world
    """

    if len(sys.argv) != 2:
        raise ValueError("Expected one file as comandline argument");

    try:
        #get valid analysis periord
        astart = str(input("enter analysis start date YYYYMMDD: "));
        if len(astart) != 8:
            raise ValueError("Date format expected is YYYYMMDD");
        astart_yr = int(astart[:4]);
        astart_mo = int(astart[4:6]);
        astart_da = int(astart[6:8]);
        aend = str(input("enter analysis end date YYYYMMDD: "));
        if len(aend) != 8:
            raise ValueError("Date format expected is YYYYMMDD");
        aend_yr = int(aend[:4]);
        aend_mo = int(aend[4:6]);
        aend_da = int(aend[6:8]);

        earliest_yr = 1910;
        cur_yr = datetime.date.today().year;
        #if start of analysis is before data start or after todays date
        #if end of analysis is after todays date
        if astart_yr < earliest_yr or astart_yr > cur_yr or aend_yr < earliest_yr or aend_yr > cur_yr:
            raise ValueError("Date expected year YYYY between 1940 and %d" % yr);
        elif astart_mo < 1 or astart_mo > 12 or aend_mo < 1 or aend_mo > 12:
            raise ValueError("Date expected month MM between 1 and 12");
        #if incorrect day number for month
        if astart_mo == 9 or astart_mo == 4 or astart_mo == 6 or astart_mo == 11 or \
        aend_mo == 9 or aend_mo == 4 or aend_mo == 6 or aend_mo == 11:
            if astart_da < 1 or astart_da > 30 or aend_da < 1 or aend_da > 30:
                raise ValueError("Invalid day of month entered");
        else:
            if astart_da < 1 or astart_da > 31 or aend_da < 1 or aend_da > 31:
                raise ValueError("Invalid day of month entered");

        #get tickers including indexes from csv
        folio = pd.read_csv(sys.argv[1]);
        print("\n{0} tickers loaded from {1}\n".format(len(folio["ticker"]), sys.argv[1]));

        #validate csv INPUT
        for bd in folio["buy_date"]:
            buy_mo = int(str(bd)[4:6]);
            buy_da = int(str(bd)[6:8]);
            if buy_mo > 12 or buy_mo < 1:
                raise ValueError("Invalid month in CSV");
            if buy_mo == 9 or buy_mo == 4 or buy_mo == 6 or buy_mo == 11:
                if buy_da < 1 or buy_da > 30:
                    raise ValueError("Invalid day of month in CSV");
            else:
                if buy_mo < 1 or buy_da > 31:
                    raise ValueError("Invalid day of month in CSV");
        for i, sd in enumerate(folio["sell_date"]):
            if pd.isnull(sd):
                folio.loc[i, "sell_date"] = aend;
            else:
                sell_mo = int(str(sd)[4:6]);
                sell_da = int(str(sd)[6:8]);
                if sell_mo > 12 or sell_mo < 1:
                    raise ValueError("Invalid month in CSV");
                if sell_mo == 9 or sell_mo == 4 or sell_mo == 6 or sell_mo == 11:
                    if sell_da < 1 or sell_da > 30:
                        raise ValueError("Invalid day of month in CSV");
                else:
                    if sell_da < 1 or sell_da > 31:
                        raise ValueError("Invalid day of month in CSV");

        #get comparison index
        index = input("1) FTSE 100; 2) S&P 500; 3) NASDAQ Composit\nselect a comparison index: ");
        if index == "1":
            index = "^FTSE";
        elif index == "2":
            index = "^GSPC";
        elif index == "3":
            index = "^IXIC";
        else:
            raise ValueError("Comparison index must be a number 1 - 3");

        #run caculations
        i = -1;
        iflag = [];
        for row in folio.itertuples():
            i = i + 1;
            #check ticker and analysis ranges overlap
            buy_yr = int(str(folio.loc[i, "buy_date"])[:4]);
            buy_mo = int(str(folio.loc[i, "buy_date"])[4:6]);
            buy_da = int(str(folio.loc[i, "buy_date"])[6:8]);
            sell_yr = int(str(folio.loc[i, "sell_date"])[:4]);
            sell_mo = int(str(folio.loc[i, "sell_date"])[4:6]);
            sell_da = int(str(folio.loc[i, "sell_date"])[6:8]);
            #if bourght after end of analysis, discard
            if buy_yr > aend_yr or \
            buy_yr == aend_yr and buy_mo > aend_mo or \
            buy_yr == aend_yr and buy_mo == aend_mo and buy_da > aend_da:
                iflag.append(i);
            #if sold before start of analysis, discard
            elif sell_yr < astart_yr or \
            sell_yr == astart_yr and sell_mo < astart_mo or \
            sell_yr == astart_yr and sell_mo == astart_mo and buy_da < astart_da:
                iflag.append(i);
            #if sold after end of analysis use end of analysis date
            elif sell_yr > aend_yr or \
            sell_yr == aend_yr and sell_mo > aend_yr or \
            sell_yr == aend_yr and sell_mo == aend_mo and sell_yr > aend_yr:
                folio.loc[i, "sell_date"] = str(aend_yr) + str(aend_mo) + str(aend_da);
                folio.loc[i, "sell_date"] = int(folio.loc[i, "sell_date"]);

        #do removals now as unsafe while iterating
        for i in iflag:
            folio.drop(i, axis='index', inplace=True);

        if len(folio) < 1:
            raise ValueError("CSV file has no valid lines");

        #get % and £ gains/losses
        folio.insert(len(folio.columns), "+-%", "NA");
        folio.insert(len(folio.columns), "+-GBP", "NA");
        i = -1;
        for row in folio.itertuples():
            i = i + 1;
            sell_yr = str(folio.loc[i, "sell_date"])[:4];
            sell_mo = str(folio.loc[i, "sell_date"])[4:6];
            sell_da = str(folio.loc[i, "sell_date"])[6:8];
            sell_str = sell_yr + "-" + sell_mo + "-" + sell_da;
            #subtract at least 3 days to avoid weekends and ensure stock data is avalable
            if int(sell_da) >= 3:
                start_da = int(sell_da) - 3;
                start_mo = int(sell_mo);
                start_yr = int(sell_yr);
            elif int(sell_mo) > 1:
                start_da = 25;
                start_mo = int(sell_mo) - 1;
                start_yr = int(sell_yr);
            else:
                start_da = 25;
                start_mo = 12;
                start_yr = int(sell_yr) - 1;
            start_str = str(start_yr) + "-" + str(start_mo) + "-" + str(start_da);
            #get data from yahoo finance
            dat = yf.Ticker(row[1]);
            hist = dat.history(start=start_str, end=sell_str, interval="1d", actions='false');
            #caculate gains/losses
            if folio.loc[i, "purchase_price_GBP"] < hist.iloc[0,3]:
                folio.loc[i, "+-GBP"] = hist.iloc[0,3] - folio.loc[i, "purchase_price_GBP"];
            else:
                folio.loc[i, "+-GBP"] = (folio.loc[i, "purchase_price_GBP"] - hist.iloc[0,3]) * -1;
            folio.loc[i, "+-%"] = hist.iloc[0,3] / folio.loc[i, "purchase_price_GBP"];

        #sum
        sumGBP = 0;
        sumPER = 0;
        for i in range(len(folio)):
            sumGBP += folio.loc[i, "+-GBP"];
            sumPER += folio.loc[i, "+-%"];
        #add total portfolio row
        folio = folio.append({"ticker": "TOTAL", "+-%": sumPER, "+-GBP": sumGBP}, ignore_index=True);

        #get index % and £ gains
        astart_str = str(astart_yr) + "-" + str(astart_mo) + "-" + str(astart_da);
        aend_str = str(aend_yr) + "-" + str(aend_mo) + "-" + str(aend_da);
        dat = yf.Ticker(index);
        hist = dat.history(start=astart_str, end=aend_str, interval="1d", actions='false');

        if hist.iloc[0,3] < hist.iloc[len(hist)-1,3]:
            indexGBP = hist.iloc[len(hist)-1,3] - hist.iloc[0,3];
        else:
            indexGBP = hist.iloc[0,3] - hist.iloc[len(hist)-1,3];
        indexPER = hist.iloc[len(hist)-1,3] / hist.iloc[0,3];

        #OUTPUT
        print("\n********************************************\n");
        if sumGBP > indexGBP:
            print("Portfolio beat the market by £{:.0f} GBP, making a total of £{:.0f} GBP over the analysis periord".format((sumGBP - indexGBP), indexGBP));
            print("Percentage growth was {:.0f}% verses {:.0f}% for the index over the same periord".format(sumPER, indexPER));
        else:
            print("Portfolio did not beat the market, making a total of £{:.0f} GBP over the analysis periord, £{:.0f} GBP less than the market".format(sumGBP, indexGBP - sumGBP));
            print("In percentage terms the portoflio changed by {:.0f}% verses {:.0f}% for the index over the same periord".format(sumPER, indexPER));
        #   - csv
        #   - daily line graph of %
        #   - total barchart of £ gains/losses

    except ValueError as err:
        print("Something went wrong: %s" % err, file=sys.stderr);
        sys.exit(1);

    return;

# script autorun
if __name__ == "__main__":

    #run program
    try:
        main();
    except UserWarning as err:
        print("%s" % err, file=sys.stderr);
        sys.exit(1);

    if DEBUG == 1:
        # unit test
        import doctest;
        doctest.testmod();
