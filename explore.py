from pymongo import MongoClient
from textblob import TextBlob
from collections import Counter
import pickle
import string
import re

DATABASE_NAME = 'movie_cliches'
COLLECTION_NAME = 'scripts'


def connect_to_db(db=DATABASE_NAME, 
                  coll=COLLECTION_NAME):
    """ Keep this modular in case in the future I want to
    use a remote db, etc."""
    return MongoClient()[db][coll]


def is_number(sent):
    try:
        float(''.join(sent.split()))
    except:
        return False
    else:
        return True

def clean_sentence(sent):
    """ Takes a TextBlob Sentence instance that
    has specific methods and cleans it"""
    # Remove upper words like EXTERNAL or character names
    for word in sent.words:
        if len(word) > 1 and word.isupper():
            sent = sent.replace(word, '')
    # remove punctuation
    exclude = set(string.punctuation)
    sent = ''.join(ch for ch in sent if ch not in exclude)
    # convert all whitespace to space
    sent = ' '.join(sent.split())
    # Remove sentences that are numbers only
    if is_number(sent):
        sent = None
    return sent
             

def count_sentences(scripts):
    counter = Counter()
    for i, script in enumerate(scripts):
        print '[%i] Processing %s' % (i, script['title'])
        if not script['text']:
            print '-- No text for %s' % script['title']
            continue
        blob = TextBlob(script['text'])
        counter.update([clean_sentence(s) for s in blob.sentences])
    return counter
                                      

def normalize_sentence_counts(counter, prior=1e-5):

    print 'pseudo_count: %i' % pseudo_count
    if None in counter: del counter[None]
    if '' in counter: del counter['']
    total = float(sum(counter.values()))
    pseudo_count = max(round(prior*total), 1)
    for key in counter:
        counter[key] = (counter[key]+pseudo_count)/(total+pseudo_count)
    return counter


def genre_counter(genre):
    db = connect_to_db()
    if genre == 'all':
        scripts = db.find()
    else:
        scripts = db.find({'genres':genre})
    print '%i %s scripts found' % (scripts.count(), genre)
    counter = count_sentences(scripts)
    counter = normalize_sentence_counts(counter)
    return counter


if __name__ == '__main__':

    all_counter = genre_counter('all')
    with open('counter_all.pkl', 'w') as counterfile:
        pickle.dump(all_counter, counterfile)

    action_counter = genre_counter('Action')
    with open('counter_action.pkl', 'w') as counterfile:
        pickle.dump(action_counter, counterfile)
        
    romance_counter = genre_counter('Romance')
    with open('counter_romance.pkl', 'w') as counterfile:
        pickle.dump(romance_counter, counterfile)
    
    print '----------ALL----------'
    for sent, count in all_counter.most_common(100):
        if sent and len(sent.split()) > 1:
            print count,':', sent

    print '----------ACTION----------'
    for sent, count in action_counter.most_common(100):
        if sent and len(sent.split()) > 1:
            print count,':', sent
    print '--------'
    ratios = [(count/all_counter[sent], sent) for sent, count in action_counter]
    ratios.sort(reversed=True)
    for ratio, sent in ratios[:100]:
        print '%f: %s' % (ratio, sent)
    print '---------------------------'

    print '----------ROMANCE----------'
    for sent, count in romance_counter.most_common(100):
        if sent and len(sent.split()) > 1:
            print count,':', sent
    print '--------'
    ratios = [(count/all_counter[sent], sent) for sent, count in romance_counter]
    ratios.sort(reversed=True)
    for ratio, sent in ratios[:100]:
        print '%f: %s' % (ratio, sent)
    print '---------------------------'



            
    

    


