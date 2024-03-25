# tw_tabulate.py -- Tabulating results of Tulving-Watkins tests
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import TulvingTabulator as tt

# Results from the article 

# - Tulving, E., & Watkins, M. J. (1975). Structure Of Memory
#   Traces. Psychological Review, 82(4),
#   261–275. http://dx.doi.org/10.1037/h0076782

TW_RESULTS = pd.DataFrame( np.array( [ [ 271, 96, 159, 242 ],
                                       [ 281, 67, 142, 278 ],
                                       [ 313, 97, 126, 232 ],
                                       [ 310, 94, 126, 238 ]
                                      ], dtype=float ) / 768 ,
                           index=tt.TulvingTabulator.LABELS_ROWS,
                           columns=tt.TulvingTabulator.LABELS_COLS )


def tab_summary( ttab, args ):
    res   = np.array( ttab.read_csv( args.sessions ), dtype=float )  / (4*len(args.sessions))
    twres = pd.DataFrame( res, index=tt.TulvingTabulator.LABELS_ROWS,  columns=tt.TulvingTabulator.LABELS_COLS )
    print( f'** Sessions: {args.sessions}' )
    print( twres )
    print( twres.mean() )
    print( '** Tulving-Watkins published results (1975)' )
    print( TW_RESULTS )
    print( TW_RESULTS.mean() )
    # print( TW_RESULTS.sum( axis=1 ) )
    fig, (axleft, axright, axbar) = plt.subplots( 1, 3, gridspec_kw={ 'width_ratios': [ 8, 8, 1 ] } )
    fig.suptitle( 'Tulving-Watkins Test, LLM and Human' )
    axleft.set_title( 'LLM (mistral-7b-instruct-v0)' )
    sns.heatmap( twres, vmin=0., vmax=1., annot=True, cmap="crest", ax=axleft, cbar=False )
    axright.set_title( 'T., W. results (1975)' )
    sns.heatmap( TW_RESULTS, vmin=0., vmax=1., annot=True, cmap="crest", ax=axright, cbar_ax=axbar )
    plt.show()
    


if __name__ == '__main__':
    pd.set_option("display.precision", 2)
    #
    parser = argparse.ArgumentParser( prog="Tabulate TW",
                                      description="Tabulate Tulving-Watkins Test results." )
    parser.add_argument('sessions', metavar='N', type=int, nargs='+', help='Session number(s)')
    parser.add_argument('-s', '--summary', action='store_true', help='Tabulate summary of performance')
    args  = parser.parse_args()
    ttab  = tt.TulvingTabulator( "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\output\\" )
    #
    if args.summary:
        tab_summary( ttab, args )
    #
    dmXY, dmYX = ttab.read_data_matrices_csv( args.sessions )
    tm1, tm2 = ttab.trace_mat( dmXY, dmYX )
    tm1, tm2 = ttab.trace_adjust( tm1, 0, 0 ), ttab.trace_adjust( tm2, 0, 0 )
    print( pd.DataFrame( tm1 ) )
    print( pd.DataFrame( tm2 ) )

