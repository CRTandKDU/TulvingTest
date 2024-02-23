# tulving_test_del_order.py -- Implementing the "delayed" Tulving protocol
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
TESTWORDS  = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\words_test.pickle"
CUESHEET_1 = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\cues_half_1.pickle"
CUESHEET_2 = "C:\\Users\\chauv\\Documents\\NEWNEWAI\\tulving\\cues_half_2.pickle"

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

TEMPL_ORDMEMO = "Step 1. Memorize the following list of english words: {}."
TEMPL_ORDTEST = "What is the {} word of the memorized list in Step 1?"


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

    model	 = llm.get_model( MODELS[mdl] )
    conversation = model.conversation()
    instr        = prompt_memostr(tbr)
    
    tbeg         = timeit.default_timer()
    response     = conversation.prompt( TEMPL_ORDMEMO.format( instr ) )
    tdur         = (timeit.default_timer() - tbeg)*1000000
    # print( f'# MEMO {tdur:4.2f}' )
    
    
    print( TEMPL_HEADER )

    for i in range( len(ORDINALS) ):
        tbeg       = timeit.default_timer()
        response   = conversation.prompt( TEMPL_ORDTEST.format( ORDINALS[i] ) )
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
    

