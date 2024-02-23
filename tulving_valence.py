# tulving_valence.py -- Implementing the cue valence measure of Tulving and Watkins (1975)
# Tuesday, January 23, 2024
# Sunday, February 18, 2024

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
TESTWCUES  = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\tbr_cues.pickle"
TESTWORDS  = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\words_test.pickle"
CUESHEET_1 = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\cues_half_1.pickle"
CUESHEET_2 = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\cues_half_2.pickle"

# Adjust for model context length
BLOCKSIZE = 8
NVALENCES = 1

# Chat templates
# TEMPL_MEMO   = " Memorize the following list, called list S4ODV78T5G, of english words: {}."

# TEMPL_RECO   = " Answer YES or NO. Is the following word in the list S4ODV78T5G: {}?"


# TEMPL_RECA   = " In this recall exercize, you will be prompted with a cue word that recalls a word from S4ODV78T5G; answer that recalled word or 'None' if you recall no cued word. No comment, no explanation, use the same format as in the examples."
# TEMPL_RECA += "\nExamples:\n(cue = '{ex1}', answer = '{an1}')\n(cue = '{ex2}', answer = '{an2}')\n(cue = '{ex3}', answer = '{an3}')\n Please complete: ( cue ='{cue}', answer = "
# TEMPL_RECA_FOLLOWUP = "Please complet: ( cue ='{cue}', answer = "

# TEMPL_RECA = " Which word in the S4ODV78T5G list is reminiscent of the given cue: answer that word or 'None' if no word in S4ODV78T5G recalls the cue."
# TEMPL_RECA += "\nExamples:\n(cue = \"{ex1}\", answer = \"{an1}\")\n(cue = \"{ex2}\", answer = \"{an2}\")\n(cue = \"{ex3}\", answer = \"{an3}\")\n Please complete: ( cue =\"{cue}\", answer = "
# TEMPL_RECA_FOLLOWUP = "Explain your answer: Please complete only with a word in the S4ODV78T5G list (or NONE if no such word is found): ( cue =\"{cue}\", answer = "

TEMPL_ASSOC_VALENCE = "Answer only with a word in the list {tbr}: which word is associated with '{cue}'?" 
TEMPL_RHYME_VALENCE = "Answer only with a word in the list {tbr}: which word rhymes with '{cue}'?"
DICT_PROMPTS = { "ncaw": TEMPL_ASSOC_VALENCE, "ncrw": TEMPL_RHYME_VALENCE }


TEMPL_RES    = "'{word}', {val:4.2f}, {valfp:4.2f}, '{cue}', '{txt}', '{cue_type}', {tdur:4.2f}"
TEMPL_HEADER = "'tbrword', 'result', 'fp', 'cue', 'response', 'cue_type', 'duration'"

def prompt_memo( tbr ):
    global TEMPL_MEMO
    str = ""
    for w  in tbr:
        str += w.upper() + ", "
    return TEMPL_MEMO.format( str[ :len(str)-2 ] )

# Protocol
def protocol_score( target, response_txt, tbr ):
    return 1 if response_txt.find( target ) >= 0 else 0

def protocol_score_book( target, response_txt, tbr ):
    return any( [ response_txt.upper().find( w ) for w in tbr ] )

def protocol_valence( tbr, cue, cue_type ):
    s          = DICT_PROMPTS[ cue_type ].format( tbr = tbr, cue = cue )
    res_val, res_valfp, tdur = 0, 0, 0.0
    # Repeat NVALENCES times
    for n in range( NVALENCES ):
        tbeg       = timeit.default_timer()
        response   = model.prompt( s )
        res_val   += protocol_score( w, response.text(), tbr )
        res_valfp += protocol_score_book( w, response.text(), tbr )
        tdur      += (timeit.default_timer() - tbeg)*1000
    return res_val, res_valfp, tdur

if __name__ == '__main__':
    parser = argparse.ArgumentParser( prog="A LLM Psychoanalyst",
                                      description="Tulving 'cue valence'." )
    parser.add_argument( '-m', '--model', default='mistral', choices=[ 'mistral', 'orcamini' ] )
    parser.add_argument( '-b', '--begin', type=int, required=True )
    args = parser.parse_args()
    # Read words from files
    with open( TESTWORDS, 'rb' ) as f:
        tbr = pickle.load( f )
    with open( TESTWCUES, 'rb' ) as f:
        tbr_cues = pickle.load( f )

    tbr = list( map( lambda s: s.upper(), tbr) )
    tbeg = timeit.default_timer()
    
    model	 = llm.get_model( MODELS[args.model] )
    tdur = (timeit.default_timer() - tbeg)*1000
    # print( f'# VALENCE: Model loaded {tdur:6.2f}' )
    print( TEMPL_HEADER )
    tot_beg = timeit.default_timer()
    for (w, cue_assoc, cue_rhyme) in tbr_cues[args.begin:args.begin+BLOCKSIZE]:
        for cue_type in [ 'ncaw', 'ncrw' ]:
            cue = cue_assoc if 'ncaw' == cue_type else cue_rhyme
            res_val, res_valfp, tdur = protocol_valence( tbr, cue, cue_type )
            print( TEMPL_RES.format( word     = w,
                                     val      = res_val/NVALENCES,
                                     valfp    = res_valfp/NVALENCES,
                                     cue      = cue,
                                     txt      = "",
                                     cue_type = cue_type,
                                     tdur     = tdur/NVALENCES ) )

    tdur = (timeit.default_timer() - tot_beg)*1000
    # print( f'# VALENCE: Done {tdur:6.2f}' )

    
    

