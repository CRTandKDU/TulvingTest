import argparse
import numpy as np
import pandas as pd

OUTPUT_DIR      = "\\tulving\\output\\"
TEMPL_MERGERECO = "merge_reco_{}_session_{}.csv"
TEMPL_MERGERECA = "merge_reca_{}_session_{}.csv"
SESSIONS        = [ 5 ]

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


def summary( df, fp ):
    # print( df.count() )
    COLRES = "'result'" if fp else "'fp'"
    return df[ [COLRES, "'cue_type'"] ].groupby( "'cue_type'" ).mean()
    

def main():
    parser = argparse.ArgumentParser( prog="Tabulate",
                                      description="Tabulate Tulving Test results." )
    parser.add_argument( '-i', '--immediate',
                         help="Selects immediate tests",
                         action=argparse.BooleanOptionalAction )
    parser.add_argument( '-b', '--book',
                         help="Selects original book metrics rather than standard",
                         action=argparse.BooleanOptionalAction )
    args = parser.parse_args()
    chrono = "Immediate" if args.immediate else "Delayed"
    reco, reca = tulving_results( chrono, false_positives = not args.book )

    summary_reco, summary_reca = summary( reco, not args.book ), summary( reca, not args.book )
    treco, treca = reco.count().get("'cue_type'"), reca.count().get("'cue_type'")
    print( f'* {chrono} Task ({treco:3d}, {treca:3d})' )
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
         
if __name__ == '__main__':
    main()
