import argparse
import pickle
import numpy as np
import pandas as pd

TESTWORDS       = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\words_test.pickle"
OUTPUT_DIR      = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\output\\"
TEMPL_MERGERECO = "merge_reco_{}_session_{}.csv"
TEMPL_MERGERECA = "merge_reca_{}_session_{}.csv"
SESSIONS        = None

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
    occurrences = np.zeros( len(tbr) )
    iw = 0
    for w in tbr:
        for i in range( nsessions ):
            df = dfs[i].loc[ lambda df: df["'tbrword'"] == f"'{w}'" ]
            if df.empty :
                pass
            else:
                if( 1 == df.iat[ 0, 1 ] and df.iat[ 0, 2 ] ) in cuetype :
                    occurrences[iw] += 1
        iw += 1
    return occurrences


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
    occurrences_o = tulving_occurences( tbr, len(SESSIONS), dfo, cuetype )
    occurrences_a = tulving_occurences( tbr, len(SESSIONS), dfa, cuetype )
    return( pd.DataFrame( data={ 'words': tbr, 'occurrences': occurrences_o } ),
            pd.DataFrame( data={ 'words': tbr, 'occurrences': occurrences_a } ) )
        

def summary( df, fp ):
    COLRES = "'result'" if fp else "'fp'"
    # print( df )
    summary= df.groupby( "'cue_type'" )[COLRES].mean()
    return summary
    

def main():
    global SESSIONS
    parser = argparse.ArgumentParser( prog="Tabulate",
                                      description="Tabulate Tulving Test results." )
    parser.add_argument( '-i', '--immediate',
                         help="Selects immediate tests",
                         action=argparse.BooleanOptionalAction )
    parser.add_argument( '-b', '--book',
                         help="Selects original book metrics rather than standard",
                         action=argparse.BooleanOptionalAction )
    parser.add_argument('sessions', metavar='N', type=int, nargs='+',
                        help='Session number(s)')
    args       = parser.parse_args()
    chrono     = "Immediate" if args.immediate else "Delayed"
    SESSIONS   = args.sessions
    reco, reca = tulving_results( chrono, false_positives = not args.book )
    summary_reco, summary_reca = summary( reco, not args.book ), summary( reca, not args.book )
    treco, treca               = reco.count().get("'cue_type'"), reca.count().get("'cue_type'")
    print( f'* {chrono} Task\n:PROPERTIES:\nSessionIds: {SESSIONS}\n:Recos: {treco:3d}\n:Recas: {treca:3d}\n:END:' )

    # Pretty print statistical summaries
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

    # Pretty print most recognized/recalled words
    print()
    print( f'* {chrono} Task: Most recognized and recalled' )
    print( '** Copy Cues' )
    dfo, dfa = tulving_cuetype_results( chrono, [ "'copy'" ], false_positives = not args.book )
    df = pd.concat( [dfo.rename( columns={ 'occurrences': 'reco' } ), dfa['occurrences'].rename( 'reca' )], axis=1 )
    print( df )
    print( '** Associative Cues' )
    dfo, dfa = tulving_cuetype_results( chrono, [ "'ncaw'" ], false_positives = not args.book )
    df = pd.concat( [dfo.rename( columns={ 'occurrences': 'reco' } ), dfa['occurrences'].rename( 'reca' )], axis=1 )
    print( df )
                         
if __name__ == '__main__':
    main()
