#!/usr/bin/env python

import sys
from sys import argv
import getopt
import os.path
import random

import nltk
from nltk.corpus import wordnet as wn
from pywsd.lesk import simple_lesk as s_lesk
from pattern.en import pluralize, singularize, comparative, superlative, conjugate, PRESENT, SG, tenses
from nltk.stem.wordnet import WordNetLemmatizer
wnl = WordNetLemmatizer()

# Usage manual
def usage(message):
	if message is not None:
		print message
		print
	print 'Usage: ./thesaurused.py [-p|--probability <0..1>] [-a|--antonym <0..1>] [-L|--lesk] [-h|--hilight] <filename>'
	print
	print '  -p, --probability   Probability to change available word, between 0 and 1'
	print '  -a, --antonym       Probability to use antonym instead of synonym, between 0 and 1'
	print '  -L, --lesk          Turn off lesk algorithm'
	print '  -h, --hilight       Hilight changed words'
	return

# Get command line options and arguments
prob_change = 1.0
prob_antonym = 0.0
no_lesk = False
do_hilight = False
try:
	opts, args = getopt.getopt(argv[1:], 'p:a:Lh', ['probability=', 'antonym=', 'lesk', 'hilight'])
except getopt.GetoptError:
	usage(None)
	sys.exit(2)

# Check if those options are valid
for opt, val in opts:
	if opt == '-p' or opt == '-a':
		try:
			v = float(val)
		except ValueError:
			usage ('Option ' + opt + ' takes number')
			sys.exit(2)

		if v < 0 or v > 1:
			usage('Option ' + opt + ' takes number between 0 and 1')
			sys.exit(2)

		if opt == '-p':
			prob_change = v
		else:
			prob_antonym = v
	elif opt == '-L':
		no_lesk = True
	elif opt == '-h':
		do_hilight = True

# Check if those arguments are existing files
if not len(args) >= 1:
	usage('What file do you want to make thesaurused?')
for filename in args:
	if not os.path.isfile(filename):
		usage()
		sys.exit(2)

# Main
def main():
	for book in args:
		# Read line by line
		with open(book, 'r') as f:
			lines = f.readlines()

		for line in lines:
			# Get words and tag it
			words = nltk.regexp_tokenize(line, "[\w']+")
			poses = nltk.pos_tag(words)
			# print poses

			line_new = str()
			for i, word in enumerate(words):
				word_list = list()
				word_mark = str()
				try:
					# Lemmatize the word
					pos = poses[i][1]
					word_lem = wnl.lemmatize(word, get_wordnet_pos(pos[0]))

					# Make synonym or antonym list
					syns = wn.synsets(word_lem, pos[0].lower())
					if len(syns) > 0 and random.random() < prob_change:
						syns_lesk = s_lesk(line, word_lem)
						if random.random() < prob_antonym:
							word_mark = 'ant'
							if no_lesk:
								word_list = [a.name().replace('_', ' ') for i, syn in enumerate(syns) for m in syn.lemmas() for a in m.antonyms()]
							else:
								word_list = [a.name().replace('_', ' ') for m in syns_lesk.lemmas() for a in m.antonyms()]
						else:
							word_mark = 'syn'
							if no_lesk:
								word_list = [n.replace('_', ' ') for i, syn in enumerate(syns) for n in syn.lemma_names()]
							else:
								word_list = [n.replace('_', ' ') for n in syns_lesk.lemma_names()]
				except KeyError:
					word_list = [word]

				# Try to remove words that are just same as original
				try:
					word_list = list(set(w.lower() for w in word_list))
					word_list.remove(word.lower())
				except ValueError:
					pass

				# Reconstruct line
				if not len(word_list) > 0:
					line_new += word + ' '
				else:
					if do_hilight:
						if word_mark == 'syn':
							line_new += hilight(transform_word(random.choice(word_list), pos, word), True, False) + ' '
						elif word_mark == 'ant':
							line_new += hilight(transform_word(random.choice(word_list), pos, word), False, False) + ' '
						else:
							line_new += transform_word(random.choice(word_list), pos, word) + ' '
					else:
						line_new += transform_word(random.choice(word_list), pos, word) + ' '

			print line_new



# Return wordnet POS from treebank tag
def get_wordnet_pos(tag):
	if tag == 'J':
		return wn.ADJ
	elif tag == 'V':
		return wn.VERB
	elif tag == 'N':
		return wn.NOUN
	elif tag == 'R':
		return wn.ADV
	else:
		return ''

# Transform word into desired POS
def transform_word(word, pos, word_original):
	words = word.split(' ')
	result = list()
	for i, word in enumerate(words):
		if i == 0:
			try:
				if pos == 'JJR' or pos == 'RBR':
					pos_again = nltk.pos_tag([word])[0][1]
					if pos_again == 'JJR' or pos_again == 'RBR':
						result.append(word)
					else:
						result.append(comparative(word))
				elif pos == 'JJS' or pos == 'RBS':
					pos_again = nltk.pos_tag([word])[0][1]
					if pos_again == 'JJS' or pos_again == 'RBS':
						result.append(word)
					else:
						result.append(superlative(word))
				elif pos == 'NNS' or pos == 'NNPS':
					pos_again = nltk.pos_tag([word])[0][1]
					if pos_again == 'NNS' or pos_again == 'NNPS':
						result.append(word)
					else:
						result.append(pluralize(word))
				elif pos == 'VBD':
					result.append(conjugate(word, 'p'))
				elif pos == 'VBG':
					result.append(conjugate(word, 'part'))
				elif pos == 'VBN':
					result.append(conjugate(word, 'ppart'))
				elif pos == 'VBP':
					if (PRESENT, 1, SG) in tenses(word_original):
						result.append(conjugate(word, '1sg'))
					else:
						result.append(conjugate(word, '2sg'))
				elif pos == 'VBZ':
					result.append(conjugate(word, '3sg'))
				else:
					result.append(word)
			except KeyError:
				result.append(word)
		else:
			result.append(word)
	return ' '.join(result)

# Colorizer
def hilight(string, status, bold):
	attr = list()
	if status:
		# green
		attr.append('32')
	else:
		# red
		attr.append('31')
	if bold:
		attr.append('1')
	return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), string)

# Start
main()