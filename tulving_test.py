# tulving_test.py -- Implementing the "delayed" Tulving protocol
# Tuesday, January 23, 2024

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
TEMPL_MEMO   = " Memorize the following list, called list S4ODV78T5G, of english words: {}."

TEMPL_RECO   = " Answer YES or NO. Is the following word in the list S4ODV78T5G: {}?"


# TEMPL_RECA   = " In this recall exercize, you will be prompted with a cue word that recalls a word from S4ODV78T5G; answer that recalled word or 'None' if you recall no cued word. No comment, no explanation, use the same format as in the examples."
# TEMPL_RECA += "\nExamples:\n(cue = '{ex1}', answer = '{an1}')\n(cue = '{ex2}', answer = '{an2}')\n(cue = '{ex3}', answer = '{an3}')\n Please complete: ( cue ='{cue}', answer = "
# TEMPL_RECA_FOLLOWUP = "Please complet: ( cue ='{cue}', answer = "

TEMPL_RECA = " Which word in the S4ODV78T5G list is reminiscent of the given cue: answer that word or 'None' if no word in S4ODV78T5G recalls the cue."
TEMPL_RECA += "\nExamples:\n(cue = \"{ex1}\", answer = \"{an1}\")\n(cue = \"{ex2}\", answer = \"{an2}\")\n(cue = \"{ex3}\", answer = \"{an3}\")\n Please complete: ( cue =\"{cue}\", answer = "
TEMPL_RECA_FOLLOWUP = "Explain your answer: Please complete only with a word in the S4ODV78T5G list (or NONE if no such word is found): ( cue =\"{cue}\", answer = "

TEMPL_RES    = "'{word}', {val:1d}, {valfp:1d}, '{cue}', '{txt}', '{cue_type}', {tdur:4.2f}"
TEMPL_HEADER = "'tbrword', 'result', 'fp', 'cue', 'response', 'cue_type', 'duration'"

def prompt_memo( tbr ):
    global TEMPL_MEMO
    str = ""
    for w  in tbr:
        str += w + ", "
    return TEMPL_MEMO.format( str[ :len(str)-2 ] )

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


def protocol_session( mdl, test, tbr, cs1, cs2, beg ):
    # INIT Chrono
    tbeg = datetime.now().isoformat( timespec='seconds' )
    print( f'# BEGIN {tbeg}' )

    # model	 = llm.get_model( "mistral-7b-instruct-v0" )
    model	 = llm.get_model( MODELS[mdl] )
    conversation = model.conversation()
    # STEP 1: MEMO.
    tbeg         = timeit.default_timer()
    response     = conversation.prompt( prompt_memo( tbr ) )
    tdur         = (timeit.default_timer() - tbeg)*1000000
    print( f'# MEMO {tdur}' )
    print( TEMPL_HEADER )

    if 'reco' == test:
        for w, cue, cue_type in cs1[ beg:beg+BLOCKSIZE ]:
            tbeg     = timeit.default_timer()
            response = conversation.prompt( TEMPL_RECO.format( cue ) )
            tdur     = (timeit.default_timer() - tbeg)*1000000
            res_val  = protocol_reco_match( response.text(), w, cue )
            res_valfp= protocol_reco_match( response.text(), w, cue,
                                            false_positives=False,
                                            tbr = tbr)
            print( TEMPL_RES.format( word=w, val=res_val, valfp=res_valfp, cue=cue, txt=response.text(), cue_type=cue_type, tdur=tdur ) )
    elif 'reca' == test:
        prompt_id = 0
        for w, cue, cue_type in cs1[ beg:beg+BLOCKSIZE ]:
            # First prompt has instructions
            prompt_txt = TEMPL_RECA.format(ex1= cs2[0][1], an1=cs2[0][0], ex2= cs2[1][1], an2=cs2[1][0], ex3= cs2[2][1], an3=cs2[2][0], cue=cue ) if 0 == prompt_id else TEMPL_RECA_FOLLOWUP.format( cue=cue )
            prompt_id += 1
            # print( prompt_txt )
            tbeg     = timeit.default_timer()
            response = conversation.prompt( prompt_txt )
            tdur     = (timeit.default_timer() - tbeg)*1000000
            answer   = w if w else 'None'
            res_val  = protocol_reca_match( response.text().lower(), answer.lower() )
            res_valfp= protocol_reco_match( response.text(), w, cue,
                                            false_positives=False,
                                            tbr = tbr)
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
    

