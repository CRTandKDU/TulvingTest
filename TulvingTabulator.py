# TulvingTabulator.py -- Tabulating results of Tulving-Watkins tests
import argparse
import csv
import numpy as np
import pandas as pd

class TulvingTabulator:
    #
    datadir = ''
    DATAFILE_TEMPLATE = 'tw_session_{}.csv'
    # This should really be read from a model description file shared with 'tulvinglib.py'
    # Encoding/Retrievals
    LABELS_ROWS       = [ 'A/AR', 'A/RA', 'R/AR', 'R/RA' ]
    # Lower case: fail, Upper case: pass
    LABELS_COLS       = [ 'ar', 'aR', 'Ar', 'AR' ]
    # Selecting encodings for data matrices
    ENCODINGS         = {"all": range(32),
                         "A": [ 0, 1, 2, 3,  8,  9, 10, 11, 16, 17, 18, 19, 24, 25, 26, 27 ],
                         "R": [ 4, 5, 6, 7, 12, 13, 14, 15, 20, 21, 22, 23, 28, 29, 39, 31 ]
                         }
    

    def __init__( self, datafiles_dir ):
        self.datadir = datafiles_dir


    def read_data_matrices_csv( self, sessions, encoding="all" ):
        dmXY, dmYX = np.zeros( (2, 2), dtype=float ), np.zeros( (2, 2), dtype=float )
        for ses in sessions:
            with open( self.datadir + TulvingTabulator.DATAFILE_TEMPLATE.format( ses ) ) as f:
                csvreader    = csv.DictReader( f, delimiter=',', quotechar="'" )
                idx = 0
                xresp, yresp = 0, 0
                for row in csvreader:
                    if idx in TulvingTabulator.ENCODINGS[ encoding ]:
                        if (0 == (idx % 8)) or (4 == (idx % 8)):
                            xresp = int( row['RESULT'] )
                        elif (1 == (idx % 8)) or (5 == (idx % 8)):
                            yresp = int( row['RESULT'] )                        
                            dmXY[ 1-xresp, 1-yresp ] += 1
                            xresp, yresp = 0, 0
                        elif (2 == (idx % 8)) or (6 == (idx % 8)):
                            yresp = int( row['RESULT'] )
                        elif (3 == (idx % 8)) or (7 == (idx % 8)):
                            xresp = int( row['RESULT'] )
                            dmYX[ 1-yresp, 1-xresp ] += 1
                            xresp, yresp = 0, 0
                        else:
                            pass
                    idx += 1
        #
        tot = (8 if "all" == encoding else 4) * len( sessions )
        return dmXY/tot, dmYX/tot

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


    def trace_mat( self, dmXY, dmYX ):
        # Equations 1 to 6 from paper
        xy = (dmXY[1,1] + dmYX[1,1])/2.
        rxy, ryx  = (1-xy)/(1-dmXY[1,1]), (1-xy)/(1-dmYX[1,1])
        X  = (dmXY[0,0] + dmXY[0,1])*rxy
        Y  = (dmYX[0,0] + dmYX[0,1])*ryx
        xY = dmXY[1,0]*rxy
        Xy = dmYX[1,0]*ryx
        eq6l, eq6r = (dmXY[0,0] + dmXY[0,1] + dmXY[1,0]), (dmYX[0,0] + dmYX[0,1] + dmYX[1,0])
        # Adjust and complete as in text
        return ([ [X-Xy, Xy, X],
                  [xY,xy, xY+xy],
                  [Y, Xy+xy, dmXY[1,1] - dmYX[1,1]] ],
                [ [Y-xY, Xy, X],
                  [xY,xy, xY+xy],
                  [Y, Xy+xy, dmYX[1,1] - dmXY[1,1]] ])


    # def trace_adjust( self, mat, x, y ):
    #     # Adjust a 2x2 matrix by substracting an equal share of M_{x,y} from all other elenents
    #     delta = mat[x][y]/3.
    #     for i in range(2):
    #         for j in range(2):
    #             mat[i][j] += delta
    #     mat[x][y] = 0.
    #     # Update marginals
    #     mat[0][2] = mat[0][0] + mat[0][1]
    #     mat[1][2] = mat[1][0] + mat[1][1]
    #     mat[2][0] = mat[0][0] + mat[1][0]
    #     mat[2][1] = mat[0][1] + mat[1][1]
    #     return mat
    
    def test( self ):
        testXY = np.array( [[ .36, .07 ],
                            [ .19, .38 ]] )
        testYX = np.array( [[ .32, .21 ],
                            [ .15, .32 ]] )
        tm1, tm2 = self.trace_mat( testXY, testYX )
        #
        pd.set_option("display.precision", 2)
        print( pd.DataFrame(tm1) )
        print( pd.DataFrame(tm2) )
        #       0     1     2
        # 0  0.31  0.14  0.45
        # 1  0.20  0.35  0.55
        # 2  0.51  0.49  0.06
        #       0     1     2
        # 0  0.31  0.14  0.45
        # 1  0.20  0.35  0.55
        # 2  0.51  0.49 -0.06        


if __name__ == '__main__':
    pass
    # pd.set_option("display.precision", 2)
    # #
    # parser = argparse.ArgumentParser( prog="Tabulate",
    #                                   description="Tabulate Tulving-Watkins Test results." )
    # parser.add_argument('sessions', metavar='N', type=int, nargs='+', help='Session number(s)')
    # args       = parser.parse_args()
    # #
    # ttab = TulvingTabulator( "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\output\\" )
    # res = np.array( ttab.read_csv( args.sessions ), dtype=float ) / (4*len(args.sessions))
    # twres = pd.DataFrame( res, index=TulvingTabulator.LABELS_ROWS,  columns=TulvingTabulator.LABELS_COLS )
    # print( twres )
    # print( twres.mean() )
    # print( twres.sum( axis=1 ) )
