# outliers.py
from operator import itemgetter

from meps.data import DataSet
import meps.think.stats2 as ts2
import meps.think.plot as tplt
from meps.data.cleaning.cleanerrs import cleanerrs, cleanallerrs

import sklearn


def identifyoutliers(dataframe, variablename, lowrange=10, highrange=10):
    """Given a dataframe and a variable name, return a dictionary
    of low and high outliers identified by by DUPERSID.
    "lowrange" and "highrange" specify percent ranges of outliers. (e.g.
    lowrange=5 will return the lowest 5% of data in the low outliers set.)
    """
    # Create Series & remove error codes
    cleandf = cleanerrs(dataframe, variablename).dropna(subset=[variablename])
    ds = cleandf[variablename]
    # Find value of lowrange-th percentile
    lowperc = ds.quantile(lowrange / 100.)
    highperc = ds.quantile((100. - highrange) / 100.)

    # Identify all points in 0-lowrange percentiles.
    lowdf = cleandf[cleandf[variablename] <= lowperc]
    highdf = cleandf[cleandf[variablename] >= highperc]

    # Get list of DUPERSIDs from each dataframe
    lowID = lowdf['DUPERSID'].values.tolist()
    highID = highdf['DUPERSID'].values.tolist()

    # Size of ranges
    lowquan = len(lowID)
    highquan = len(highID)

    return {
        'low': {
            'df': lowdf,
            'ids': lowID,
            'range': [ds.min(), lowperc],
            'size': lowquan,
            'percentile': lowrange
        },
        'high': {
            'df': highdf,
            'ids': highID,
            'range': [highperc, ds.max()],
            'size': highquan,
            'percentile': highrange
        }
    }


def findsimilarities(dataframe, checkvars):
    """Takes a dataframe (from identifyoutliers()) of outliers and a list of
    variables to be checked.
    """
    cleanframe = cleanallerrs(dataframe)
    reslist = []
    for var in checkvars:
        this_series = cleanframe[var]
        this_std = this_series.std()
        # Number of NaNs:
        this_nan = this_series.isnull().sum()

        this_info = {
            'std': this_std,
            'NaNs': this_nan,
        }
        reslist.append(this_info)

    # sort reslist
    outlist = sorted(reslist, key=itemgetter('std'), reverse=True)
    return outlist


def analyzeoutliers(dataframe, variablename, checkvars):
    outliers = identifyoutliers(dataframe, variablename)
    # Make list of low and high outlier dataframes
    lhdf = [outliers['low']['df'], outliers['high']['df']]
    results = []
    for outlierset in lhdf:
        ranked = findsimilarities(outlierset, checkvars)
        results.append(ranked)
    return results


def main():
    # Demonstration. Prints data regarding lowest 5 and highest 10 percent of
    # total healthcare expenditures.
    h155 = DataSet('h155.pkl')
    df = h155.df
    outliers = identifyoutliers(df, 'TOTEXP12', 5, 10)
    print 'low'
    print outliers['low']['size']
    print outliers['low']['range']
    print outliers['low']['percentile']
    print '\nhigh'
    print outliers['high']['size']
    print outliers['high']['range']
    print outliers['high']['percentile']
    checkvars = ['ADDPRS42', 'ADHECR42', 'ADSMOK42', 'AGE12X', 'AIDHLP31',
                 'AIDHLP53', 'AMCHIR12', 'OBCHIR12', 'AMNURS12', 'OBNURS12', 'AMOPTO12', 'OBOPTO12', 'AMASST12', 'OBASST12', 'AMTHER12', 'OBTHER12', 'OBTOTV12', 'OBDRV12', 'OBOTHV12', 'COGLIM31', 'COGLIM53', 'BLIND42', 'BMINDX53', 'DEAF42', 'EMPST31', 'EMPST42', 'EMPST53', 'EVRETIRE', 'FNGRDF31', 'FNGRDF53', 'HEARAD42', 'HSELIM31', 'HSELIM53', 'HYSTER53', 'MARRY12X', 'MILDIF31', 'MILDIF53', 'NOASPR53', 'NOFAT53', 'RCHDIF31', 'RCHDIF53', 'READNW42', 'RECPEP42', 'SEX', 'STNDIF31', 'STNDIF53', 'STOMCH53', 'STPDIF31', 'STPDIF53', 'TTLP12X', 'UNABLE31', 'UNABLE53', 'VISION42', 'WLK3MO31', 'WLK3MO53', 'WLKDIF31', 'WLKDIF53', 'WLKLIM31', 'WLKLIM53', 'WRGLAS42', 'WRKLIM31', 'WRKLIM53']

    results = analyzeoutliers(h155, 'TOTEXP12', checkvars)

if __name__ == '__main__':
    main()
