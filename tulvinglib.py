# tulvinglib.py -- A catalog of Tulving Tests
import logging
import tulvingmem as tm

def test_recognition( chrono, fn, model_nn ):
    def test_score( resp, row ):
        if 'C' == row['cue_type']:
            return 1 if resp.upper().find( "YES" ) >= 0 else 0
        else:
            return 1 if resp.upper().find( "NO" ) >= 0 else 0

    tt             = tm.TulvingTest( 'Tulving Recognition {}'.format( tm.TulvingTest.TYPE_LABELS[chrono] ) )
    tt.distractors = [ 'D' ]
    tt.remember    = 'Memorize the following list, called list S4ODV78T5G, of english words: {}.'
    tt.encodings   = '{0}'
    tt.retrievals  = 'Answer YES or NO. Is the following word in the list S4ODV78T5G: {0}?'
    tt.protocol    = {
        'type'         : chrono,
        'batch_number' : 4,
        'batch_size'   : 8,
        'encodings'    : [ ['T'], ['T'], ['T'], ['D'], ['T'], ['T'], ['T'], ['D'] ],
        'retrievals'   : [ ['C'], ['A'], ['R'], ['D'], ['C'], ['A'], ['R'], ['D'] ]
    }
    tt.fill( fn )
    tt.score = test_score
    tt.perform( model_nn )


def test_recall( chrono, fn, model_nn ):
    def test_score( resp, row ):
        if 'C' == row['cue_type']:
            return 1 if resp.upper().find( "YES" ) >= 0 else 0
        else:
            return 1 if resp.upper().find( "NO" ) >= 0 else 0

    tt             = tm.TulvingTest( 'Tulving Reall {}'.format( tm.TulvingTest.TYPE_LABELS[chrono] ) )
    tt.distractors = [ 'D' ]
    tt.remember    = 'Memorize the following list, called list S4ODV78T5G, of english words: {}.'
    tt.encodings   = '{0}'
    tt.retrievals  = 'Which word in the list S4ODV78T5G is associated or rhymes with: {0}?'
    tt.protocol    = {
        'type'         : chrono,
        'batch_number' : 4,
        'batch_size'   : 8,
        'encodings'    : [ ['T'], ['T'], ['T'], ['D'], ['T'], ['T'], ['T'], ['D'] ],
        'retrievals'   : [ ['C'], ['A'], ['R'], ['D'], ['C'], ['A'], ['R'], ['D'] ]
    }
    tt.fill( fn )
    tt.score = test_score
    tt.perform( model_nn )
    
    
def test_tw( chrono, fn, model_nn ):
    def tw_test_score( resp, row ):
        return 1 if resp.upper().find( row['target'][0].upper() ) >= 0 else 0

    tt             = tm.TulvingTest( 'Tulving Watkins {}'.format( tm.TulvingTest.TYPE_LABELS[chrono] ) )
    tt.encodings   = '{0} (context: {1})'
    tt.distractors = []
    tt.remember    = 'Memorize the following list of english words with their context: {}. You will be asked to remember and answer one of these words to later questions.'
    tt.retrievals  = 'Which word in the memorized list is associated or rhymes with {0}?'
    tt.protocol    = {
        'type'         : chrono,
        'batch_number' : 4,
        'batch_size'   : 4,
        'encodings'    : [ ['target', 'acue'], ['target', 'acue'], ['target', 'rcue'], ['target', 'rcue'] ],
        'retrievals'   : [ ['altacue', 'altrcue'], ['altrcue', 'altacue'], ['altacue', 'altrcue'], ['altrcue', 'altacue'] ]
    }
    tt.fill( fn )
    tt.score = tw_test_score
    tt.perform( model_nn )

    
def test_ordering( chrono, fn, model_nn ):
    def test_score( resp, row ):
        return 1 if resp.upper().find( row['target'][0].upper() ) >= 0 else 0

    tt             = tm.TulvingTest( 'Tulving Ordering {}'.format( tm.TulvingTest.TYPE_LABELS[chrono] ) )
    tt.distractors = []
    tt.remember    = 'Memorize the following list, called list S4ODV78T5G, of english words: {}.'
    tt.encodings   = '{0}'
    tt.retrievals  = 'What is the {0} word in the list S4ODV78T5G?'
    tt.protocol    = {
        'type'         : chrono,
        'batch_number' : 1,
        'batch_size'   : 24,
        'encodings'    : [ ['T'], ['T'], ['T'], ['T'], ['T'], ['T'], ['T'], ['T'],
                           ['T'], ['T'], ['T'], ['T'], ['T'], ['T'], ['T'], ['T'],
                           ['T'], ['T'], ['T'], ['T'], ['T'], ['T'], ['T'], ['T']],
        'retrievals'   : [ ['O'], ['O'], ['O'], ['O'], ['O'], ['O'], ['O'], ['O'],
                           ['O'], ['O'], ['O'], ['O'], ['O'], ['O'], ['O'], ['O'],
                           ['O'], ['O'], ['O'], ['O'], ['O'], ['O'], ['O'], ['O'] ]
    }
    tt.fill( fn, randomize=False )
    tt.score = test_score
    tt.perform( model_nn )



if __name__ == '__main__':
    logging.basicConfig(
        filename='tulvingmem.log',
        encoding='utf-8',
        level=logging.INFO
    )
    # test_recall( tm.TulvingTest.TYPE_PROMPT, 'tm_words0023.csv', 'mistral' )
    # test_ordering( tm.TulvingTest.TYPE_PROMPT, 'tm_ordering.csv', 'mistral' )
    test_tw( tm.TulvingTest.TYPE_PROMPT,  'tw_cues.csv', 'mistral' )
