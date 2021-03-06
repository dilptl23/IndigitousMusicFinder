import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
import pickle

app = Flask(__name__)

@app.route('/')
def home():
	binned_songs = pickle.load(open('../topic_groupings/Joy.p', 'rb'))
	song_list = []
	# for key, val in binned_songs.items():
	# 	for song in val:
	# 		with open('../txt/' + song['title'] + '.txt') as lyric_file:
	# 			song_list.append(lyric_file.read())
	for key, val in binned_songs.items():
		for song in sorted(val, reverse=False, key=lambda x: x['score']):
			song_list.append((song['saying'], url_for('static', filename=song['title'] + '.png')))
		break
	return render_template('display_lyrics.html', songs=song_list)

