# tulvingmem.py -- Refactors Tulving test protocols
# Friday, March 1, 2024 New
import argparse
from datetime import datetime
import timeit
import logging
# import pickle
import csv
import numpy as np
#
import llm

class TulvingTest:
    TYPE_CHAT   = 1
    TYPE_PROMPT = 0
    TYPE_LABELS = [ 'immediate', 'delayed' ]
    DISTRACTOR  = 'NONE'
    # Models are at [[C:\Users\chauv\.cache\gpt4all]]
    MODELS = {
        "orcamini" : "orca-mini-3b-gguf2-q4_0",
        "mistral"  : "mistral-7b-instruct-v0"
    }

    RES_HEADER = "'TBRWORD','RESULT','INLIST','CUE','RESPONSE','CUE_TYPE','DURATION'"
    RES_ROW    = "'{word}',{val:1d},{valinlist:1d},'{cue}','{txt}','{cue_type}',{tdur:4.2f}"

    name       = ""
    remember, encodings, retrievals = '', '', ''
    distractors  = []
    protocol   = None
    session    = []
    tbr_list   = []


    def __init__(self, name):
        "A TulvingTest instance."
        self.name = name


    def score( self, resp, row ):
        return 0


    def score_inlist( self, resp, row ):
        return 0
        

    def perform(self, model_nn):
        tbeg = datetime.now().isoformat( timespec='seconds' )
        logging.info( f'{tbeg} > Performance' )
        #
        tbr_str = ', '.join( [ self.encodings.format( *enc ) for enc in self.tbr_list ] )
        model     = llm.get_model( TulvingTest.MODELS[ model_nn ] )
        #
        tbeg = datetime.now().isoformat( timespec='seconds' )
        logging.info( f'{tbeg} > Model {model_nn} loaded' )
        print( TulvingTest.RES_HEADER )
        #
        if TulvingTest.TYPE_CHAT == self.protocol['type']:
            batch_idx = 0
            for batch in self.session:
                tbeg = datetime.now().isoformat( timespec='seconds' )
                logging.info( f'{tbeg} > BEGIN batch {batch_idx}' )
                #
                conversation = model.conversation()
                response     = conversation.prompt( self.remember.format( tbr_str ) )
                for row in batch:
                    tbeg = datetime.now().isoformat( timespec='seconds' )
                    logging.info( f'{tbeg} > BEGIN row {row}' )
                    #
                    tbeg     = timeit.default_timer()
                    response = conversation.prompt( self.retrievals.format( row['probe'] ) )
                    tdur     = (timeit.default_timer() - tbeg)*1000000
                    val = self.score( response.text(), row )
                    valinlist = self.score_inlist( response.text(), row )
                    print( TulvingTest.RES_ROW.format(
                        word      = row['target'],
                        val       = val,
                        valinlist = valinlist,
                        cue       = row['probe'],
                        txt       = response.text(),
                        cue_type  = row['cue_type'],
                        tdur      = tdur
                    ) )
                batch_idx += 1
        #
        elif TulvingTest.TYPE_PROMPT == self.protocol['type']:
            batch_idx = 0
            inst = '{} '.format( self.remember.format( tbr_str ) )
            for batch in self.session:
                for row in batch:
                    tbeg     = timeit.default_timer()
                    response = model.prompt( inst + self.retrievals.format( row['probe'] ) )
                    tdur     = (timeit.default_timer() - tbeg)*1000000
                    val = self.score( response.text(), row )
                    valinlist = self.score_inlist( response.text(), row )
                    print( TulvingTest.RES_ROW.format(
                        word      = row['target'],
                        val       = val,
                        valinlist = valinlist,
                        cue       = row['probe'],
                        txt       = response.text(),
                        cue_type  = row['cue_type'],
                        tdur      = tdur
                    ) )
                batch_idx += 1

        else:
            pass
        tbeg = datetime.now().isoformat( timespec='seconds' )
        logging.info( f'{tbeg} > Performance done' )



    def fill(self, csvfn, randomize=True ):
        assert self.protocol
        assert len( self.protocol['encodings']) == len( self.protocol['retrievals'] )
        assert len( self.protocol['encodings']) == self.protocol['batch_size']
        
        self.session = []
        tbr, ntbr = [], []
        # Read in words CSV file
        with open( csvfn ) as csvfile:
            reader = reader = csv.DictReader(csvfile)
            for row in reader:
                if [] == self.distractors or all( [ 'none' == row[x] for x in self.distractors ] ):
                    tbr += [ row ]
                else:
                    ntbr += [ row ]

        # Randomize
        p        = np.random.permutation( len(tbr) ) if randomize else range( len(tbr) )
        q        = np.random.permutation( len(ntbr) ) if randomize else range( len(ntbr) )
        # Precompile session as a list of batches
        tbr_idx, ntbr_idx = 0, 0
        self.tbr_list = []
        for b in range( self.protocol['batch_number'] ):
            batch = []
            # A batch is a list of probes = { target:<a list of encodings>, probe:<a cue word> }
            # (There may be several probes for one target.)
            for i in range ( self.protocol['batch_size'] ):
                if self.protocol['encodings'][i][0] in self.distractors:
                    batch += [{
                        'target'   : TulvingTest.DISTRACTOR,
                        'probe'    : ntbr[q[ntbr_idx]][ self.protocol['retrievals'][i][0] ],
                        'cue_type' : self.protocol['retrievals'][i][0]
                    }]
                    ntbr_idx += 1
                else:
                    target = [ tbr[p[tbr_idx]][ x ] for x in self.protocol['encodings'][i] ]
                    for r in self.protocol['retrievals'][i]:
                        batch += [ {
                            'target'   : target,
                            'probe'    : tbr[p[tbr_idx]][r],
                            'cue_type' : r
                        } ]
                    #
                    row = [ tbr[tbr_idx][x] for x in self.protocol['encodings'][i] ]
                    self.tbr_list += [ row ]
                    tbr_idx += 1
            self.session += [ batch ]
                

    
    
if __name__ == '__main__':
    logging.basicConfig(
        filename='tulvingmem.log',
        encoding='utf-8',
        level=logging.INFO
    )
    # Usage:
    # test_recognition( TulvingTest.TYPE_CHAT, 'tm_words2447.csv', 'mistral' )
    #
    # test_tw( TulvingTest.TYPE_PROMPT, 'tw_cues.csv', 'mistral' )

