from sklearn.linear_model import SGDClassifier
from gensim.matutils import corpus2dense
from gensim import corpora
from nltk.tokenize import word_tokenize
from preprocessing import preprocess
import numpy as np
import gensim
import joblib
import pickle
import redis
import os
import re

redisModel = redis.Redis(host='redis', port=6379, db=2)

dictionary = corpora.Dictionary.load("tfidf_sentiment.dictionary")
tfidf = gensim.models.TfidfModel.load("tfidf_sentiment.model")
with open("emoticon_dictionary1.pkl","rb") as g:
    emoticon_dictionary = pickle.load(g)
sentiment_dictionary = {"negative":0,"positive":4}


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

def feedback(tweet,correct_sentiment):
    print(tweet, correct_sentiment)
    print(type(tweet),type(correct_sentiment))
    p = redisModel.pipeline()
    p.watch('model')  # watch for changes on these keys
    lr = pickle.loads(p.get("model"))
    correct_sentiment = sentiment_dictionary[correct_sentiment.lower()]
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
    classes= [0,4]
    # try:
    p.multi()
    print(features.shape)
    lr.partial_fit(features,[correct_sentiment],classes=classes)
    p.set("model", pickle.dumps(lr))
    p.execute()
    # except:
    #     p = redisModel.pipeline()
    #     p.watch('model')  # watch for changes on these keys
    #     lr = pickle.loads(redis_server.get("model"))
    #     feedback(tweet,correct_sentiment)



