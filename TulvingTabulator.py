# TulvingTabulator.py -- Tabulating results of Tulving-Watkins tests
import argparse
import csv
import numpy as np
import pandas as pd

class TulvingTabulator:
    DATAFILE_TEMPLATE = 'tw_session_{}.csv'
    LABELS_ROWS       = [ 'A/AR', 'A/RA', 'R/AR', 'R/RA' ]
    LABELS_COLS       = [ 'ar', 'Ra', 'Ar', 'AR' ]
    #
    datadir = ''

    def __init__( self, datafiles_dir ):
        self.datadir = datafiles_dir


    def read_csv( self, sessions ):
        results = np.zeros( (4, 4), dtype=float )
        for ses in sessions:
            with open( self.datadir + TulvingTabulator.DATAFILE_TEMPLATE.format( ses ) ) as f:
                csvreader    = csv.DictReader( f, delimiter=',', quotechar="'" )
                idx, batch   = 0, 0
                aresp, rresp = 0, 0
                for row in csvreader:
                    if idx in [ 8*batch + x for x in [ 0, 3, 4, 7 ] ]:
                        aresp = int( row['RESULT'] )
                    if idx in [ 8*batch + x for x in [ 1, 2, 5, 6 ] ]:
                        rresp = int( row['RESULT'] )
                    #
                    if 1 == (idx % 2):
                        row, col = (idx - 8*batch) // 2, aresp + aresp + rresp
                        # print( f'row: {idx}, batch: {batch}, col:{col}' )
                        results[ row, col ] += 1.
                        aresp, rresp = 0, 0
                    #    
                    idx += 1
                    if 0 == (idx % 8):
                        batch += 1
                
        return results


if __name__ == '__main__':
    pd.set_option("display.precision", 2)
    #
    parser = argparse.ArgumentParser( prog="Tabulate",
                                      description="Tabulate Tulving-Watkins Test results." )
    parser.add_argument('sessions', metavar='N', type=int, nargs='+', help='Session number(s)')
    args       = parser.parse_args()
    #
    ttab = TulvingTabulator( "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\output\\" )
    res = np.array( ttab.read_csv( args.sessions ), dtype=float ) / (4*len(args.sessions))
    twres = pd.DataFrame( res, index=TulvingTabulator.LABELS_ROWS,  columns=TulvingTabulator.LABELS_COLS )
    print( twres )
    print( twres.mean() )
    print( twres.sum( axis=1 ) )
