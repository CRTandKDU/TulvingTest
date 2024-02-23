# tulving_test.py -- Implementing the "immediate" Tulving protocol
# Started: Tuesday, January 23, 2024
# Revised: Wednesday, January 31, 2024

import argparse
from datetime import datetime
import timeit
import pickle
import numpy as np
#
import llm

MODELS = { "orcamini": "orca-mini-3b-gguf2-q4_0",
           "mistral":  "mistral-7b-instruct-v0"
          }

# Source words
TESTWORDS  = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\words_test.pickle"
CUESHEET_1 = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\cues_half_1.pickle"
CUESHEET_2 = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\cues_half_2.pickle"

# Adjust for model context length
BLOCKSIZE = 8

# Chat templates
TEMPL_RECO   = "1) Memorize the following list, called list S4ODV78T5G, of english words: {}.\n2) Answer YES or NO. Is the following word in the list S4ODV78T5G: {}?"

TEMPL_RECA = "1) Memorize the following list, called list S4ODV78T5G, of english words: {}.\n2) Which word in the S4ODV78T5G list is related to the given cue: answer that word or 'None' if no word in S4ODV78T5G recalls the cue.\nCue = {}, Answer ="

TEMPL_RES    = "'{word}', {val:1d}, {valfp:1d}, '{cue}', '{txt}', '{cue_type}', {tdur:4.2f}"
TEMPL_HEADER = "'tbrword', 'result', 'fp', 'cue', 'response', 'cue_type', 'duration'"

def prompt_memostr( tbr ):
    str = ""
    for w  in tbr:
        str += w + ", "
    return str[ :len(str)-2 ]

# Protocol
def protocol_reca_match( txt, answer, false_positives = True, tbr=None ):
    if txt:
        if false_positives:
            return 1 if (txt.find( f"'{answer}'") >= 0) or (txt.find( f' {answer}' ) >= 0) or (txt.find( f'"{answer}"') >= 0) else 0
        else:
            return any( [ 1 if txt.find( w ) >=0 else 0 for w in tbr ] )
    return 0


def protocol_reco_match( txt, answer, cue, false_positives = True, tbr=None ):
    if txt:
        res_y, res_n = txt.find( "Yes" ), txt.find( "No" )
        if false_positives:
            return 1 if ( res_y > 0 and res_n < 0) and (answer == cue ) or ( res_y < 0 and res_n > 0 and answer != cue ) else 0
        else:
            return 1 if ( res_y > 0 and res_n < 0) else 0
    return 0

# Modified for "immediate"
def protocol_session( mdl, test, tbr, cs1, cs2, beg ):
    # INIT Chrono
    tbeg = datetime.now().isoformat( timespec='seconds' )
    print( f'# BEGIN {tbeg}' )

    # model	 = llm.get_model( "mistral-7b-instruct-v0" )
    model	 = llm.get_model( MODELS[mdl] )
    instr        = prompt_memostr(tbr)
    
    print( TEMPL_HEADER )

    if 'reco' == test:
        # RECOGNITION
        for w, cue, cue_type in cs1[ beg:beg+BLOCKSIZE ]:
            tbeg     = timeit.default_timer()
            response = model.prompt( TEMPL_RECO.format( instr, cue ) )
            tdur     = (timeit.default_timer() - tbeg)*1000000
            res_val  = protocol_reco_match( response.text(), w, cue )
            res_valfp= protocol_reco_match( response.text(), w, cue,
                                            false_positives=False,
                                            tbr = tbr)
            print( TEMPL_RES.format( word=w, val=res_val, valfp=res_valfp, cue=cue, txt=response.text(), cue_type=cue_type, tdur=tdur ) )
    elif 'reca' == test:
        # RECALL
        prompt_id  = 0
        for w, cue, cue_type in cs1[ beg:beg+BLOCKSIZE ]:
            prompt_id += 1
            prompt_txt = TEMPL_RECA.format( instr, cue )
            # print( prompt_txt )
            tbeg     = timeit.default_timer()
            response = model.prompt( prompt_txt )
            tdur     = (timeit.default_timer() - tbeg)*1000000
            answer   = w if w else 'None'
            res_val  = protocol_reca_match( response.text().lower(), answer.lower() )
            res_valfp= protocol_reca_match( response.text(), answer, false_positives=False, tbr = tbr)
            print( TEMPL_RES.format( word=w, val=res_val, valfp=res_valfp, cue=cue, txt=response.text(), cue_type=cue_type, tdur=tdur ) )
    else:
        pass

    # CLOSE Chrono
    tbeg = datetime.now().isoformat( timespec='seconds' )
    print( f'# END {tbeg}' )


# def protocol_session( test, cs1, cs2 ):
#     snow = datetime.now().isoformat( timespec='seconds' )
#     print( f'# BEGIN {snow}' )
    
#     model	 = llm.get_model( "mistral-7b-instruct-v0" )
#     conversation = model.conversation()

#     # STEP 1: MEMO.
#     tbeg = timeit.default_timer()
#     response     = conversation.prompt( prompt_memo() )
#     tdur = (timeit.default_timer() - tbeg)*1000000
#     # print( response.text(), f'{tdur:4.2f}' )
#     print( TEMPL_HEADER )

#     if 'reco' == test:
#         # STEP 2: RECO. TEST
#         for w, cue in cs1:
#             tbeg = timeit.default_timer()
#             response = conversation.prompt( TEMPL_RECO.format( cue ) )
#             tdur = (timeit.default_timer() - tbeg)*1000000
#             res_y, res_n, res_txt = response.text().find( "Yes" ), response.text().find( "No" ), response.text()
#             res_val = 1 if ( res_y > 0 and res_n < 0 and w == cue ) or ( res_y < 0 and res_n > 0 and w != cue )  else 0
#             print( TEMPL_RES.format( word=w, val=res_val, cue=cue, txt=res_txt, tdur=tdur ) )

#     if 'reca' == test:
#         row = 0
#         # STEP 2: RECA. TEST
#         for w, cue in cs1:
#             # print( TEMPL_RECA.format(
#             #     ex1= cs2[0][1], an1=cs2[0][0],
#             #     ex2= cs2[1][1], an2=cs2[1][0], 
#             #     ex3= cs2[2][1], an3=cs2[2][0], 
#             #     cue=cue ) )

#             sprompt = TEMPL_RECA.format(ex1= cs2[0][1], an1=cs2[0][0], ex2= cs2[1][1], an2=cs2[1][0], ex3= cs2[2][1], an3=cs2[2][0], cue=cue ) if 0 == row else TEMPL_RECA_FOLLOWUP.format( cue=cue )
#             row += 1
            
#             tbeg = timeit.default_timer()
#             response = conversation.prompt( sprompt )
#             tdur = (timeit.default_timer() - tbeg)*1000000
#             res_y, res_n, res_txt = response.text().find( "Yes" ), response.text().find( "No" ), response.text()
#             # Approximation of score (what if cue evokes a different word in list?)
#             answer = w if w else 'None'
#             res_val = protocol_reca_match( response.text().lower(), answer )
#             print( TEMPL_RES.format( word=w, val=res_val, cue=cue, txt=res_txt, tdur=tdur ) )
            
#     snow = datetime.now().isoformat( timespec='seconds' )
#     print( f'# END {snow}' )
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser( prog="A LLM Psychoanalyst",
                                      description="Tulving Test on the Mistral-7b LLM." )
    parser.add_argument( '-t', '--test', default='reco', choices=[ 'reco', 'reca' ] )
    parser.add_argument( '-m', '--model', default='mistral', choices=[ 'mistral', 'orcamini' ] )
    parser.add_argument( '-b', '--begin', type=int, required=True )
    args = parser.parse_args()
    # Read words from files
    with open( CUESHEET_1, 'rb' ) as f:
        cs1 = pickle.load( f )
    with open( CUESHEET_2, 'rb' ) as f:
        cs2 = pickle.load( f )
    with open( TESTWORDS, 'rb' ) as f:
        tbr = pickle.load( f )
    protocol_session( args.model, args.test, tbr, cs1, cs2, args.begin )
    

