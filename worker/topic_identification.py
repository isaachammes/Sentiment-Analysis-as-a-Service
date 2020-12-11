from operator import itemgetter
from nltk import word_tokenize
from gensim import corpora
import spacy
import gensim
import pickle
import re
from preprocessing import preprocess

dictionary = corpora.Dictionary.load("tfidf.dictionary")
model =  gensim.models.LdaMulticore.load('topic_model1.model')
with open("topic_dictionary.pkl","rb") as g:
    topic_dictionary = pickle.load(g)
nlp = spacy.load("en_core_web_sm")

def find_retweeted(tweet):
    '''This function will extract the twitter handles of retweed people'''
    return re.findall('(?<=RT\s)(@[A-Za-z]+[A-Za-z0-9-_]+)', tweet)

def find_mentioned(tweet):
    '''This function will extract the twitter handles of people mentioned in the tweet'''
    return re.findall('(?<!RT\s)(@[A-Za-z]+[A-Za-z0-9-_]+)', tweet)  

def find_hashtags(tweet):
    '''This function will extract hashtags'''
    return re.findall('(#[A-Za-z]+[A-Za-z0-9-_]+)', tweet)

def find_ner(tweet):
    doc = nlp(tweet)
    return(doc.ents)

def topic_identification(tweet):
    retweet = find_retweeted(tweet)
    mention = find_mentioned(tweet)
    hashtag = find_hashtags(tweet)
    preprocessed_tweet = str(preprocess(tweet)) #either preprocess or use db to get preprocessed tweet
    entity = list(find_ner(tweet))
    #print(retweet,mention,hashtag,entity)
    new_doc = word_tokenize(preprocessed_tweet)
    new_doc_bow = dictionary.doc2bow(new_doc)
    topics = model.get_document_topics(new_doc_bow)
    if len(topics) > 0:
        topic = max(topics, key=itemgetter(1)) #gives probability of topi, can be shown
        words_topic = topic_dictionary[topic[0]].split()[0]
    else:
        words_topic = ""
    final_list_topics = retweet+mention+hashtag+entity+[words_topic]
    return(final_list_topics)
# make new columns for mentioned usernames and hashtag