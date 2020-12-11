from sklearn.linear_model import SGDClassifier
from gensim.matutils import corpus2dense
from gensim import corpora
from nltk.tokenize import word_tokenize
from preprocessing import preprocess
import numpy as np
import re
import gensim
import joblib
import pickle

dictionary = corpora.Dictionary.load("tfidf_sentiment.dictionary")
tfidf = gensim.models.TfidfModel.load("tfidf_sentiment.model")
with open("emoticon_dictionary1.pkl","rb") as g:
    emoticon_dictionary = pickle.load(g)

lr = joblib.load("lr_sentiment1.joblib")
sentiment_dictionary = {0:"Negative",4:"Positive"}

def get_emojis_pattern():
#     emojis_pattern = re.compile(u'([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])')
    emojis_pattern = re.compile(
            u'([\u2600-\u27BF])|([\uD83C][\uDF00-\uDFFF])|([\uD83D][\uDC00-\uDE4F])|([\uD83D][\uDE80-\uDEFF])')
    return emojis_pattern

def find_emoji(text):
        '''Takes a string and find all emojis'''
        emoji_p = re.compile(r":\)|:-\)|:\(|:-\(|;-\)|;D|:$|:-$|:-D|:D|:-O|:O|:-P|:P|;-D|;P|;-P|%-\)|:'\(|:'-\(|D:|:-|:huglove:|\(:|:\/|::sigh times \d::|::sigh::|::gagging::|::faceplants on floor and cries::|::pouts::|::scampers off::|:\]tweet-tweet\[:")
        emojis = re.findall(emoji_p, text)
        emojis2 = re.findall(get_emojis_pattern(), text)
        return emojis+emojis2

def sentiment_calculation(tweet):
    processed_tweet = str(preprocess(tweet))
    tokenized_tweet = word_tokenize(processed_tweet)
    words = [dictionary.doc2bow(tokenized_tweet)]
    num_terms = len(dictionary.keys())
    tf_fe = corpus2dense(tfidf[words], num_terms, 1)
    emoticon = np.zeros((1,len(emoticon_dictionary)))
    emojis = find_emoji(tweet.strip(":"))
    for k in emojis:
        emoticon[0][emoticon_dictionary[k]] = 1
    features = np.concatenate((tf_fe.T,emoticon),axis=1) 
    sentiment = lr.predict(features)
    return(sentiment_dictionary[sentiment[0]])

print(sentiment_calculation("this is my first sentence happy"))
