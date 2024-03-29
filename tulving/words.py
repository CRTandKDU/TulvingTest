# words.py -- The Turing Complete LLM project
# Tuesday, January 23, 2024
# Starting from a list of 48 distinct simple English words, generate
# an org file with synonyms, antonyms and rhymes for each word.

# Done once:
# import nltk
# nltk.download( 'wordnet' )
# nltk.download( 'cmudict' )

#Checking synonym for the word "travel"
from nltk.corpus import wordnet
from nltk.corpus import cmudict

entries = cmudict.entries()
print( 'CMU Pronunciation Dictionary:', len(entries) )

def set_of_cues( word ):
    global entries
    pron, rhymes, syns, antos = None, None, [], []
    # Find pronunciation for rhymes
    for w, p in entries:
        if word == w:
            pron = p
            break
    if pron:
        ending = pron[ -2: ]
        rhymes = [ w for w, p in entries if ending == p[ -2: ] ]
    # Antonyms and synonyms
    for syn in wordnet.synsets( word ):
        for lm in syn.lemmas():
            syns.append( lm.name() ) # adding into synonyms
            if lm.antonyms():
                antos.append( lm.antonyms()[0].name() )
    return rhymes, list( set( syns ) ), list( set( antos ) )

TBR_WORDS = [
    'free',
    'sleet',
    'small',
    'produce',
    'grape',
    'cobweb',
    'library',
    'chair',
    'walk',
    'cart',
    'stitch',
    'side',
    'locket',
    'move',
    'egg',
    'sneeze',
    'faucet',
    'volcano',
    'toy',
    'mass',
    'recess',
    'bead',
    'ant',
    'cover',
    'hen',
    'hat',
    'pet',
    'map',
    'control',
    'pain',
    'cushion',
    'monkey',
    'vegetable',
    'day',
    'curtain',
    'kitten',
    'copper',
    'basin',
    'ball',
    'net',
    'card',
    'cake',
    'locket',
    'guitar',
    'value',
    'volcano',
    'list',
    'arm'
]

print( 'To-be-remembered (TBR) words:', len(TBR_WORDS) )

for w in TBR_WORDS:
    rhy, syn, ant = set_of_cues( w )
    print( "* {}".format( w ) )
    print( "** Rhymes of {}".format( w ) )
    print( rhy )
    print( "** Synonyms of {}".format( w ) )
    print( syn )
    print( "** Antonyms of {}".format( w ) )
    print( ant )
    
    

