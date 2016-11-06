import nltk
import gensim
import os
import codecs
import string
from nltk.corpus import wordnet as wn

TRAIN_VOCAB = 0

## Build the initial Gensim dictionary and store it

# clean text by removing stopwords
# obtain synset for each word, and hypernyms for each synonym.
# return a flat list of hypernyms (not separated by the words
# in text that they represent).
def clean_text(text):

	# Code to clean up the words

	stopword_filename = "./stopwords.txt" # external file that contains stopwords
	# much better than what's available in python itself.
	with open(stopword_filename) as f:
		stopwords = set(f.read().split())
	for punct in string.punctuation:
		stopwords.add(punct)
	exclude = set(string.punctuation)

	# filter out the stopwords
	cleaned_text_list = list(filter(lambda x: x not in stopwords, \
		[''.join(ch for ch in s if ch not in exclude) for s in text.split()]))


	# Expanding vocabulary: Hypernym approach.
	line_hypernyms = []
	for word in cleaned_text_list:
		word_ss = wn.synsets(word)
		for hypernyms in [ss.hypernyms() for ss in word_ss]:
			for hypernym in hypernyms:
				line_hypernyms.append(hypernym.name().split('.')[0])
	# print(line_hypernyms)
	return line_hypernyms



# Gather all the lines, in all the songs, to create a gensim dictionary.
# The training happens in line-sized units.
def generate_song_lines():
	songs_lines = []
	basepath = './'
	for fname in os.listdir(basepath + './txt_period/'):
	    path = os.path.join(basepath, fname)
	    # Enter if not directory (is file)
	    if not os.path.isdir(path):
	        # Assert if it's a .txt file
	        filewhole = path.split('.')
	        filename = filewhole[1][1:]
	        ext = filewhole[-1]
	        # Execute if .txt file
	        if ext == 'txt':
	            # Create out .json files to write to
	            with codecs.open('./txt_period/' + path, 'r', encoding='utf8') as fin:
	                for line in fin:
	                	cleaned = clean_text(line[:-1])
	                	if cleaned:
	                		songs_lines.append(cleaned)
	return songs_lines

# line: an array of words
# gdict: a gensim Dictionary object (your vocabulary)
# numtopics: the number of topics that you want outputted. Currently, this doesn't
# necessarily mean that a higher number makes your topics more distinct and descriptive.
# Our dataset is possibly too small for that.
def make_and_show_lda_model(line, gdict, numtopics):
	# represent the corpus in sparse matrix format, bag-of-words
	corpus = [gdict.doc2bow(line)]

	# now we make an LDA object.
	# in case we have a larger text collection (such as the Brown corpus),
	# make sure to set "passes" to a reasonably high number in order not to have all topics
	# come out equal.
	lda_obj = gensim.models.ldamodel.LdaModel( \
		corpus, id2word=gdict, num_topics=numtopics, passes = 30)

	# how does our line look: how important is each topic there?
	print("Showing how important each topic is for each document")
	total_topic_words = []
	lda_corpus = lda_obj[corpus]
	for docindex, doc in enumerate(lda_corpus):
		for topic, weight in doc:
			topic_words = [x[0] for x in sorted(lda_obj.show_topic(topic), key=lambda x : x[1])]
			# print( "Topic", topic,", which has keywords: ", topic_words, \
			# 	"\nWith weight of", round(weight, 2))
			total_topic_words.append(topic_words)
	return total_topic_words


if TRAIN_VOCAB:
	gdict = gensim.corpora.Dictionary(generate_song_lines())
	gdict.save('./songs_lines.dict')
else: # vocabulary has been trained; just load it and use it.
	gdict = gensim.corpora.Dictionary.load('./songs_lines.dict')

def trainAndPrintTopics(gdict, filepath):
	# Code that outputs each stanza of the song specified in the text
	# file followed by a series of topic-describing hypernyms.
	with open(filepath) as inf:
		stanza = ""
		for line in inf:
			if not line or line == '\n':
				if stanza:
					print("\n\n", stanza)
					make_and_show_lda_model(clean_text(stanza), gdict, 1)
				stanza = ""
			else:
				stanza += line + " "

def getStanzaTopics(gdict, filepath):
	# similar to previous function but it returns a list of topics, one per
	# stanza, instead.
	topics = []
	with open(filepath) as inf:
		stanza = ""
		for line in inf:
			if not line or line == '\n':
				if stanza:
					for topic in make_and_show_lda_model(clean_text(stanza), gdict, 1):
						topics.append(topic)
				stanza = ""
			else:
				stanza += line + " "
	return topics


# trainAndPrintTopics(gdict, "./txt_period/song_files_with_period/mercy_mendes.txt")