# tulvingmem.py -- Refactors Tulving test protocols
# Friday, March 1, 2024 New
import argparse
from datetime import datetime
import timeit
import pickle
import csv
import numpy as np
#
import llm

class TulvingTest:
    TYPE_CHAT   = 1
    TYPE_PROMPT = 0
    DISTRACTOR  = 'NONE'
    
    MODELS = {
        "orcamini": "orca-mini-3b-gguf2-q4_0",
        "mistral":  "mistral-7b-instruct-v0"
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
        tbr_str = ', '.join( [ self.encodings.format( *enc ) for enc in self.tbr_list ] )
        model     = llm.get_model( TulvingTest.MODELS[ model_nn ] )
        print( TulvingTest.RES_HEADER )

        if TulvingTest.TYPE_CHAT == self.protocol['type']:
            batch_idx = 0
            for batch in self.session:
                conversation = model.conversation()
                response     = conversation.prompt( self.remember.format( tbr_str ) )
                for row in batch:
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
                
        elif TulvingTest.TYPE_PROMPT == self.protocol['type']:
            batch_idx = 0
            inst = '[INST]{}[/INST] '.format( self.remember.format( tbr_str ) )
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

    def fill(self, csvfn ):
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
        p        = np.random.permutation( len(tbr) )
        q        = np.random.permutation( len(ntbr) )
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
                

def test():
    def test_score( resp, row ):
        if 'C' == row['cue_type']:
            return 1 if resp.upper().find( "YES" ) >= 0 else 0
        else:
            return 1 if resp.upper().find( "NO" ) >= 0 else 0
    
    tt             = TulvingTest( 'Tulving Delayed' )
    tt.distractors = [ 'D' ]
    tt.remember    = 'Memorize the following list, called list S4ODV78T5G, of english words: {}.'
    tt.encodings   = '{0}'
    tt.retrievals  = 'Answer YES or NO. Is the following word in the list S4ODV78T5G: {0}?'
    tt.protocol    = {
        'type'         : TulvingTest.TYPE_PROMPT,
        'batch_number' : 4,
        'batch_size'   : 8,
        'encodings'    : [ ['T'], ['T'], ['T'], ['D'], ['T'], ['T'], ['T'], ['D'] ],
        'retrievals'   : [ ['C'], ['A'], ['R'], ['D'], ['C'], ['A'], ['R'], ['D'] ]
    }
    tt.fill( 'tm_words2447.csv' )
    tt.score = test_score
    tt.perform( 'mistral' )

    # tt             = TulvingTest( 'Tulving Watkins' )
    # tt.encodings   = '{0} (context: {1})'
    # tt.distractors = []
    # tt.protocol    = {
    #     'type'         : TulvingTest.TYPE_CHAT,
    #     'batch_number' : 4,
    #     'batch_size'   : 4,
    #     'encodings'    : [ ['target', 'acue'], ['target', 'acue'], ['target', 'rcue'], ['target', 'rcue'] ],
    #     'retrievals'   : [ ['altacue', 'altrcue'], ['altrcue', 'altacue'], ['altacue', 'altrcue'], ['altrcue', 'altacue'] ]
    # }
    # tt.fill( 'tw_cues.csv' )
    # tt.perform( 'mistral' )
    
    
if __name__ == '__main__':
    test()
        

