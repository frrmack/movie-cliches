from pymongo import MongoClient
from textblob import TextBlob
from collections import Counter, defaultdict
import json
import pickle
import string
import re
import sys

DATABASE_NAME = 'movie_cliches'
COLLECTION_NAME = 'scripts'


def connect_to_db(db=DATABASE_NAME, 
                  coll=COLLECTION_NAME):
    """ Keep this modular in case in the future I want to
    use a remote db, etc."""
    return MongoClient()[db][coll]


def save(obj, filename):
    with open(filename, 'w') as picklefile:
        pickle.dump(obj, picklefile)

def load(filename):
    with open(filename, 'r') as picklefile:
        return pickle.load(picklefile)


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
    sentence_to_movies = defaultdict(Counter)
    tot_length, num_scripts = 0,0
    for i, script in enumerate(scripts):
        print '[%i] Processing %s' % (i, script['title'])
        if not script['text']:
            print '-- No text for %s' % script['title']
            continue
        blob = TextBlob(script['text'])
        sentences = [clean_sentence(s) for s in blob.sentences]
        for sent in sentences:
            sentence_to_movies[sent].update([script['title']])
        print '-- %i sentences in %s' % (len(sentences), script['title'])
        tot_length += len(sentences)
        num_scripts += 1
        counter.update(sentences)
    print '%.1f sentences per script on average' % (1.*tot_length/num_scripts)
    return counter, sentence_to_movies
                                      

def normalize_sentence_counts(counter, prior=4e-6):

    if None in counter: del counter[None]
    if '' in counter: del counter['']
    total = float(sum(counter.values()))
    pseudo_count = max(round(prior*total), 1)
    print 'pseudo_count: %i' % pseudo_count
    for key in counter:
        counter[key] = (counter[key]+pseudo_count)/(total+pseudo_count)
    return counter


def genre_counter(genre, pickle=True):
    db = connect_to_db()
    if genre == 'all':
        scripts = db.find()
    else:
        scripts = db.find({'genres':genre})
    print >> sys.stderr, '%i %s scripts found' % (scripts.count(), genre)
    counter, sentence_to_movies = count_sentences(scripts)
    counter = normalize_sentence_counts(counter)
    if pickle:
        print >> sys.stderr, 'saving %s counter...' % genre,
        save(counter, 'counter_%s.pkl' % genre.lower())
        save(sentence_to_movies, 'sent2mov_%s.pkl' % genre.lower())
        print >> sys.stderr, 'done.'
    return counter, sentence_to_movies

def count_and_save_each_genre():
    db = connect_to_db()
    genres = db.distinct('genres')
    for genre in genres:
        ##############
        if genre in ['all', 'Romance', 'Action']:
            continue
        #############
        genre_counter(genre, pickle=True)


if __name__ == '__main__':


    # count_and_save_each_genre()
    # sys.exit()


    # Count and save
    #all_counter, sent2mov = genre_counter('all')
    # action_counter = genre_counter('Action')
    #romance_counter = genre_counter('Romance')

    # Load counts
    all_counter, sent2mov = load('counter_all.pkl'), load('sent2mov_all.pkl')
    #action_counter = load('counter_action.pkl')
    #romance_counter = load('counter_romance.pkl')
    #comedy_counter = load('counter_comedy.pkl')
    
    print '----------ALL----------'
    data = []
    for sent, count in all_counter.most_common(90):
        if sent == "A beat" : continue  # A stop sentence (script language)
        if sent and len(sent.split()) > 1:
            print count*3000,':', sent
            movie_data = [{"movie": mov, "count": ct} for mov, ct in sent2mov[sent].most_common(12)]
            data.append({"sentence": sent,
                          "freq": "%.2f" % (count*3000),
                          "movies": movie_data })
    with open("all.json", 'w') as jsonfile:
        json.dump(data, jsonfile)
    print 'Data written.'
    sys.exit()        
    


    min_freq_threshold = 3e-5

    print '----------ACTION----------'
    for sent, count in action_counter.most_common(100):
        if sent and len(sent.split()) > 1:
            print count,':', sent
    print '--------'
    ratios = [(count/all_counter[sent], sent) for sent, count in action_counter.iteritems() if len(sent.split()) > 1 and count > min_freq_threshold]
    ratios.sort(reverse=True)
    for ratio, sent in ratios[:100]:
        print '%f: %s' % (ratio, sent)
    print '---------------------------'

    print '----------ROMANCE----------'
    for sent, count in romance_counter.most_common(100):
        if sent and len(sent.split()) > 1:
            print count,':', sent
    print '--------'
    ratios = [(count/all_counter[sent], sent) for sent, count in romance_counter.iteritems() if len(sent.split()) > 1 and count > min_freq_threshold]
    ratios.sort(reverse=True)
    for ratio, sent in ratios[:100]:
        print '%f: %s' % (ratio, sent)
    print '---------------------------'


    print '----------ACTION----------'
    for sent, count in action_counter.most_common(100):
        if sent and len(sent.split()) > 1:
            print count,':', sent
    print '--------'
    ratios = [(count/all_counter[sent], sent) for sent, count in action_counter.iteritems() if len(sent.split()) > 1 and count > min_freq_threshold]
    ratios.sort(reverse=True)
    for ratio, sent in ratios[:100]:
        print '%f: %s' % (ratio, sent)
    print '---------------------------'


            

    


