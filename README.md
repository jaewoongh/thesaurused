Thesaurused
===========
A code poetry machine

## What does this do?
Thesaurused takes text file(s) and replaces possible words into synonyms/antonyms.

## Usage
Basic usage:

	$ ./thesaurused.py the_road_not_taken_by_robert_frost.txt

Options:

	$ ./thesaurused.py [-p|--probability <0..1>] [-a|--antonym <0..1>] [-L|--lesk] [-h|--highlight] <filename>

	  -p, --probability   Probability to change available word, between 0 and 1
	  -a, --antonym       Probability to use antonym instead of synonym, between 0 and 1
	  -L, --lesk          Turn off lesk algorithm
	  -h, --highlight       Highlight changed words

Change 80% of possible words, trying using antonym for half of them if possible:

	$ ./thesaurused.py -p 0.8 -a 0.5 sample.txt

Turn off lesk algorithm to give more possibilities of being ridiculous, and highlight result:

	$ ./thesaurused.py -Lh sample.txt

Highlight colors are green for synonym, red for antonym by default.

*Note that since there're simply not much antonyms for words than synonyms, things may not result in expected output.

## Dependencies
[NLTK](http://www.nltk.org/install.html) is absolutely needed.

This project contains copies of [pywsd](https://github.com/alvations/pywsd) and [pattern.en](http://www.clips.ua.ac.be/pages/pattern-en).  
Please refer to those sites for more information about legal and references.

## As a forgetting device

The project is originally done as a "forgetting device" for the class "To Remember and Forget: Memory and Machine" at ITP, Tisch School Of The Arts, NYU, by [Taeyoon Choi](http://taeyoonchoi.com).

The idea is to slowly change a text a bit by bit, but not entirely at once, so that person could see the text without any clear disturbing feeling. Since the structure of the text is still there and only words change to not completely absurd alternatives, it could effectively mislead the reader if done slowly and steadily.