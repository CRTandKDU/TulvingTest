# tulving_tabulate.py -- Tabulating results of the "direct comparison"
# Revised: Wednesday, February 14, 2024 -- Added ordering tests results
# Revised: Sunday, February 18, 2024 -- The question of cue valence

import argparse
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

CUETYPES        = ["'copy'", "'ncaw'", "'ncrw'", "'none'"]
TESTWORDS       = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\words_test.pickle"
OUTPUT_DIR      = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\output\\"
TEMPL_MERGERECO = "merge_reco_{}_session_{}.csv"
TEMPL_MERGERECA = "merge_reca_{}_session_{}.csv"
TEMPL_MERGEORDR = "merge_ord_{}_mistral_session_{}.csv"
SESSIONS        = None

def tulving_ordering_results():
    """
    Merge results tables from 'ordering' Tulving Test into dataframes.
    One for the delayed test; one for the immmediate test.
    """
    global SESSIONS, OUTPUT_DIR, TEMPL_MERGEORDR
    COLRES  = "'RESULT'"
    del_df  = pd.read_csv( OUTPUT_DIR + TEMPL_MERGEORDR.format( 'del', SESSIONS[0] ),
                           index_col=False, 
                           usecols=lambda x: x.upper() in [COLRES, "'CUE_TYPE'"] )
    imm_df  = pd.read_csv( OUTPUT_DIR + TEMPL_MERGEORDR.format( 'imm', SESSIONS[0] ),
                           index_col=False,
                           usecols=lambda x: x.upper() in [COLRES, "'CUE_TYPE'"] )
    for ses in SESSIONS[ 1: ]:
        dfd = pd.read_csv( OUTPUT_DIR + TEMPL_MERGEORDR.format( 'del', ses ),
                           index_col=False,
                           usecols=lambda x: x.upper() in [COLRES, "'CUE_TYPE'"] )
        dfi = pd.read_csv( OUTPUT_DIR + TEMPL_MERGEORDR.format( 'imm', ses ),
                           index_col=False,
                           usecols=lambda x: x.upper() in [COLRES, "'CUE_TYPE'"] )
        del_df = pd.concat( [del_df, dfd] )
        imm_df = pd.concat( [imm_df, dfi] )
    return del_df, imm_df


def tulving_results( chrono, false_positives=True ):
    global SESSIONS, OUTPUT_DIR, TEMPL_MERGEFN
    COLRES  = "'RESULT'" if false_positives else "'FP'"
    imm     = "imm" if "Immediate" == chrono else "del"
    reco_df = pd.read_csv( OUTPUT_DIR + TEMPL_MERGERECO.format( imm, SESSIONS[0] ),
                           index_col=False,
                           usecols=lambda x: x.upper() in [COLRES, "'CUE_TYPE'"] )
    reca_df = pd.read_csv( OUTPUT_DIR + TEMPL_MERGERECA.format( imm, SESSIONS[0] ),
                           index_col=False,
                           usecols=lambda x: x.upper() in [COLRES, "'CUE_TYPE'"] )
    for ses in SESSIONS[ 1: ]:
        dfo = pd.read_csv( OUTPUT_DIR + TEMPL_MERGERECO.format( imm, ses ),
                           index_col=False,
                           usecols=lambda x: x.upper() in [COLRES, "'CUE_TYPE'"] )
        dfa = pd.read_csv( OUTPUT_DIR + TEMPL_MERGERECA.format( imm, ses ),
                           index_col=False,
                           usecols=lambda x: x.upper() in [COLRES, "'CUE_TYPE'"] )
        reco_df = pd.concat( [reco_df, dfo] )
        reca_df = pd.concat( [reca_df, dfa] )
        
    return reco_df, reca_df


def tulving_occurences( tbr, nsessions, dfs, cuetype ):
    occ_word, occ_true = np.zeros( len(tbr) ), np.zeros( len(tbr) )
    iw = 0
    for w in tbr:
        for i in range( nsessions ):
            df = dfs[i].loc[ lambda df: df["'tbrword'"] == f"'{w}'" ]
            if df.empty :
                pass
            else:
                if df.iat[ 0, 2 ]  in cuetype:
                    occ_word[iw] += 1
                if 1 == df.iat[ 0, 1 ] and df.iat[ 0, 2 ] in cuetype :
                    occ_true[iw] += 1
        iw += 1
    return occ_word, occ_true


def tulving_cuetype_results( chrono, cuetype, false_positives=True ):
    global SESSIONS, OUTPUT_DIR, TEMPL_MERGEFN, TESTWORDS
    COLRES  = "'RESULT'" if false_positives else "'FP'"
    imm     = "imm" if "Immediate" == chrono else "del"
    # Read session results from column implicitly designes by metrics (all/book)
    i = 0
    dfo, dfa = [ None for i in range( len(SESSIONS) ) ], [ None for i in range( len(SESSIONS) ) ]
    for session in SESSIONS:
        dfo[ i ] = pd.read_csv( OUTPUT_DIR + TEMPL_MERGERECO.format( imm, session ),
                                      index_col=False,
                                      usecols=lambda x: x.upper() in ["'TBRWORD'", COLRES, "'CUE_TYPE'"] )
        dfa[ i ] = pd.read_csv( OUTPUT_DIR + TEMPL_MERGERECA.format( imm, session ),
                                      index_col=False,
                                      usecols=lambda x: x.upper() in ["'TBRWORD'", COLRES, "'CUE_TYPE'"] )
        i += 1
        
    # Score each word
    with open( TESTWORDS, 'rb' ) as f:
        tbr = pickle.load( f )
    occ_words_o, occ_true_o = tulving_occurences( tbr, len(SESSIONS), dfo, cuetype )
    occ_words_a, occ_true_a = tulving_occurences( tbr, len(SESSIONS), dfa, cuetype )
    return( pd.DataFrame( index=tbr, data={ 'occ_word': occ_words_o, 'occ_true': occ_true_o } ),
            pd.DataFrame( index=tbr, data={ 'occ_word': occ_words_a, 'occ_true': occ_true_a} ) )
        

def summary( df, fp ):
    COLRES = "'result'" if fp else "'fp'"
    # summary = df.groupby( "'cue_type'" )[COLRES].mean()
    # Cleansing
    mask = df["'cue_type'"].isin(CUETYPES)
    df_clean = df[ mask ]
    # with pd.option_context('display.max_rows', None,
    #                    'display.max_columns', None,
    #                    'display.precision', 3,
    #                    ):

    summary = df_clean.groupby( ["'cue_type'"] ).mean()[COLRES]
    return summary
    

def rand_jitter(arr):
    stdev = .01 * (max(arr) - min(arr))
    return arr + np.random.randn(len(arr)) * stdev


def tulving_scatterplot( df, title ):
    # dfo_sorted = df.sort_values( by=['reco_true'], ascending=False )
    # df[['B','C']] = df[['B','C']].div(df.A, axis=0)

    df[ ['reco_true'] ] = df[ ['reco_true'] ].div( df.reco_word, axis = 0 )
    df[ ['reca_true'] ] = df[ ['reca_true'] ].div( df.reca_word, axis = 0 )

    # df.reco_true = rand_jitter( df.reco_true )
    # df.reca_true = rand_jitter( df.reca_true )
    xyrange = [ -0.05, 1.05 ]
    df.plot.scatter( x='reca_true', y='reco_true', 
                     title=title, marker='+',
                     xlim=xyrange, ylim=xyrange,
                     xlabel='Cue Valence', ylabel='Recognition'
                    )


def main():
    global SESSIONS
    parser = argparse.ArgumentParser( prog="Tabulate",
                                      description="Tabulate Tulving Test results." )
    parser.add_argument( '-i', '--immediate',
                         help="Selects immediate tests",
                         action=argparse.BooleanOptionalAction )
    parser.add_argument( '-o', '--ordering',
                         help="Selects ordering tests",
                         action=argparse.BooleanOptionalAction )
    parser.add_argument( '-b', '--book',
                         help="Selects original book metrics rather than standard",
                         action=argparse.BooleanOptionalAction )
    parser.add_argument('sessions', metavar='N', type=int, nargs='+',
                        help='Session number(s)')
    args       = parser.parse_args()
    
    chrono     = "Immediate" if args.immediate else "Delayed"
    SESSIONS   = args.sessions

    if args.ordering:
        COLRES         = "'result'"
        del_df, imm_df = tulving_ordering_results()
        ndel, nimm     = len( del_df.index ), len( imm_df.index )
        mdel, mimm     = del_df.mean(numeric_only=True)[COLRES], imm_df.mean(numeric_only=True)[COLRES]
        print( f'* Ordering Task\n:PROPERTIES:\n:SessionIds: {SESSIONS}\n:Delayed: {ndel:3d}\n:Immediate: {nimm:3d}\n:END:' )
        print( f'| Immediate |  Delayed |\n| {mimm:2.3f} | {mdel:2.3f} |\n' )

    else:
        reco, reca = tulving_results( chrono, false_positives = not args.book )
        summary_reco, summary_reca = summary( reco, not args.book ), summary( reca, not args.book )
        treco, treca               = reco.count().get("'cue_type'"), reca.count().get("'cue_type'")
        print( f'* {chrono} Task\n:PROPERTIES:\n:SessionIds: {SESSIONS}\n:Recos: {treco:3d}\n:Recas: {treca:3d}\n:END:' )

        # Org-mode print statistical summaries
        if not args.book :
            df = pd.merge( summary_reco, summary_reca, on="'cue_type'" ).rename(
                columns={"'result'_x": "Familiarity", "'result'_y": "Identification"},
                index={"'copy'": "Copy", "'ncaw'": "Associate", "'ncrw'": "Rhyme", "'none'": "Unrelated"} )
        else:
            df = pd.merge( summary_reco, summary_reca, on="'cue_type'" ).rename(
                columns={"'fp'_x": "Familiarity", "'fp'_y": "Identification"},
                index={"'copy'": "Copy", "'ncaw'": "Associate", "'ncrw'": "Rhyme", "'none'": "Unrelated"} )

        df.index.rename( "Cue Type", inplace=True )
        print( df )

        # Org-mode print most recognized/recalled words
        print()
        print( f'* {chrono} Task: Most recognized and recalled' )
        print( '** Copy Cues' )
        dfo, dfa = tulving_cuetype_results( chrono, [ "'copy'" ], false_positives = not args.book )
        df = pd.concat( [dfo.rename( columns={ 'occ_word': 'reco_word', 'occ_true': 'reco_true' } ), dfa.rename( columns={ 'occ_word': 'reca_word', 'occ_true': 'reca_true' } ) ], axis=1 )
        df.to_csv( f'tab_counts_copy_{chrono}.csv' )
        # print( df.sort_values( by=['reco'] ) )
        # Scatterplot
        tulving_scatterplot( df, f'{chrono} Task -- Copy Cues' )
        plt.show()

        plt.close( "all" )
        print( '** Associative Cues' )
        dfo, dfa = tulving_cuetype_results( chrono, [ "'ncaw'", "'ncrw'" ], false_positives = not args.book )
        df = pd.concat( [dfo.rename( columns={ 'occ_word': 'reco_word', 'occ_true': 'reco_true' } ), dfa.rename( columns={ 'occ_word': 'reca_word', 'occ_true': 'reca_true' } ) ], axis=1 )
        df.to_csv( f'tab_counts_noncopy_{chrono}.csv' )
        tulving_scatterplot( df, f'{chrono} Task - Associative Cues' )
        plt.show()
        # df.sort_values( by=['reco_true'], ascending=False ).to_csv( f'tab_counts_copy_{chrono}.csv' )
        # print( df.sort_values( by=['reco'] ) )

                         
if __name__ == '__main__':
    pd.set_option("display.precision", 2)
    main()
