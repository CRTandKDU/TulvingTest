# tulving_test_imm-py.py -- Implementing the "immediate" Tulving protocol
# Started: Tuesday, January 23, 2024
# Revised: Wednesday, January 31, 2024
#          Monday, February 12, 2024

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
TESTWORDS  = "\\tulving\\words_test.pickle"
CUESHEET_1 = "\\tulving\\cues_half_1.pickle"
CUESHEET_2 = "\\tulving\\cues_half_2.pickle"

# Adjust for model context length
BLOCKSIZE = 8

ORDINALS = [ "First",        
             "Second",       
             "Third",        
             "Fourth",       
             "Fifth",        
             "Sixth",        
             "Seventh",      
             "Eighth",       
             "Ninth",        
             "Tenth",       
             "Eleventh",    
             "Twelfth",     
             "Thirteenth",  
             "Fourteenth",  
             "Fifteenth",   
             "Sixteenth",   
             "Seventeenth", 
             "Eighteenth",  
             "Nineteenth",  
             "Twentieth" ]

# Chat templates
TEMPL_RECO   = "1) Memorize the following list, called list S4ODV78T5G, of english words: {}.\n2) Answer YES or NO. Is the following word in the list S4ODV78T5G: {}?"

TEMPL_RECA = "1) Memorize the following list, called list S4ODV78T5G, of english words: {}.\n2) Which word in the S4ODV78T5G list is related to the given cue: answer that word or 'None' if no word in S4ODV78T5G recalls the cue.\nCue = {}, Answer ="


TEMPL_ORD = "1) Memorize the following list, called list S4ODV78T5G, of english words: {}.\n2) What is the {} word of the list?"


TEMPL_RES    = "'{word}',{val:1d},{valfp:1d},'{cue}','{txt}','{cue_type}',{tdur:4.2f}"
TEMPL_HEADER = "'tbrword','result','fp','cue','response','cue_type','duration'"

def prompt_memostr( tbr ):
    str = ""
    for w  in tbr:
        str += w + ", "
    return str[ :len(str)-2 ]

# Protocol
def protocol_ord_match( txt, answer ):
    return 1 if (txt.find( f"'{answer}'") >= 0) or (txt.find( f"\"{answer}\"") >= 0) else 0


# Modified for "immediate"
def protocol_session( mdl, tbr ):
    global ORDINALS
    # INIT Chrono
    tbeg = datetime.now().isoformat( timespec='seconds' )
    # print( f'# BEGIN {tbeg}' )

    # model	 = llm.get_model( "mistral-7b-instruct-v0" )
    model	 = llm.get_model( MODELS[mdl] )
    instr        = prompt_memostr(tbr)
    
    print( TEMPL_HEADER )

    for i in range( len(ORDINALS) ):
        tbeg       = timeit.default_timer()
        response   = model.prompt( TEMPL_ORD.format( instr, ORDINALS[i] ) )
        tdur       = (timeit.default_timer() - tbeg)*1000000
        res_val    = protocol_ord_match( response.text(), tbr[i] )
        res_val_fp = res_val
        print( TEMPL_RES.format( word=tbr[i], val=res_val, valfp=res_val_fp, cue='-', txt=response.text(), cue_type="ordn", tdur=tdur ) )
    # CLOSE Chrono
    tbeg = datetime.now().isoformat( timespec='seconds' )
    # print( f'# END {tbeg}' )



if __name__ == '__main__':
    parser = argparse.ArgumentParser( prog="A LLM Psychoanalyst",
                                      description="Tulving Test on the Mistral-7b LLM." )
    parser.add_argument( '-m', '--model', default='mistral', choices=[ 'mistral', 'orcamini' ] )

    args = parser.parse_args()
    # Read words from files
    with open( CUESHEET_1, 'rb' ) as f:
        cs1 = pickle.load( f )
    with open( CUESHEET_2, 'rb' ) as f:
        cs2 = pickle.load( f )
    with open( TESTWORDS, 'rb' ) as f:
        tbr = pickle.load( f )

    protocol_session( args.model, tbr )
    

