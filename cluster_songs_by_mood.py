import analyzetopic as anato
from gensim import corpora, models, similarities
import os
import pickle
from collections import defaultdict

gdict = anato.getgdict()

# Analyze song lyrics from the "mood" folder.
# (this mood folder was generated by other files and corresponds to
# IBM Watson's mood labels)
# Pickle the result to save time when loading the topic analysis
# data next time.
def pickleTopicsForMood(mood):
	songs_to_topics = {}
	for fname in os.listdir('./songs_to_moods/' + mood):
		path = './txt_period/song_files_with_period/' + fname
		# topics = anato.getStanzaTopics(gdict, path)
		topics = anato.getSongTopics(gdict, path)
		topics = [x for sublist in topics for x in sublist] # flatten list of lists
		songs_to_topics[fname] = topics
		print("analyzed", fname, "got", topics)
	pickle.dump(songs_to_topics, open( "./songs_to_topics/songs_to_topics_" + mood + ".p", "wb"))

# print songs binned by topic.
def retrieveSimilarSongs(mood):
	songs_to_topics = pickle.load(open("./songs_to_topics/songs_to_topics_" + mood + ".p", 'rb'))
	
	# corpus is a list of bags of words per song, a matrix representation that gensim understands.
	corpus = [gdict.doc2bow(song) for song in songs_to_topics.values()]
	titles = [title for title in songs_to_topics.keys()]
	# print(corpus)

	# generate num_topics topics for the entire song corpus
	lda = models.ldamodel.LdaModel(corpus, id2word=gdict, num_topics=50)
	corpus_lda = lda[corpus]

	binned_songs = defaultdict(list)

	# in terms of these generated topics, look at the topics most captured
	# by individual songs.
	for idx, song_bow in enumerate(corpus):
		top_topic = sorted(enumerate(lda[song_bow]), reverse=True, key=lambda x: x[1])[0]
		
		with open('./songs_to_moods/' + mood + '/' + titles[idx]) as metafile:
			meta_list = metafile.read().split('\n')
			meta = {}
			meta['title'] = meta_list[0]
			# use the score to sort the resulting list by score.
			meta['score'] = float(meta_list[2])
			meta['saying'] = meta_list[8]

			binned_songs[top_topic[0]].append(meta)

	# We've grouped songs according to their top-ranked topic.
	# Now, display the topics and their best-matched songs.

	for key, val in binned_songs.items():
		topic_words = [x[0] for x in sorted(lda.show_topic(key), key=lambda x : x[1])]
		print("Topic", topic_words)
		binned_songs[key] = sorted_songs = sorted(val, reverse=True, key=lambda x: x['score'])
		for song in sorted_songs:
			print("\t", song['score'], song['title'], '\n\t\t', song['saying'])

	pickle.dump(binned_songs, open('./topic_groupings/' + mood + '.p', 'wb'))
	return binned_songs

# pickleTopicsForMood('Anger')
retrieveSimilarSongs("Anger")
