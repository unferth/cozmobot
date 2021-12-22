#!/usr/bin/env python

import string, random, sys, os, re, imp
import wikipedia
import time
from bs4 import UnicodeDammit
import subprocess
import shelve
cp = imp.find_module('cPickle')
cPickle = imp.load_module('cPickle', cp[0], cp[1], cp[2])

MAXGEN=1000 # Max number of words to generate
NONWORD = '\n' # Use as start- and endmarkers
SAVECOUNT = 30
global answer
answer = ""
global jeopardy
jeopardy = False
global tries
tries = 0
global question
question = ""
global roundCount
roundCount = 0
global uncovered
uncovered = ""
global silent
silent = False

class MarkovChainer:
    def __init__(self, bot):
        self.bot = bot
        self.bot.register_handler("pubmsg", self.handle_pubmsg)
        self.dict = cPickle.load(open("markov.state", 'r'))
        self.savecounter = 0

    def handle_pubmsg(self, connection, event):
        global answer
        global jeopardy
        global tries
        global question
        global roundCount
        global uncovered
        global silent
        silent = False
        spoken = 0
        addressed = 0
        chainable = 1
        whonick = self.bot.nm_to_n(event.source())
        message = event.arguments()[0]
        print '%s: %s' % (whonick, message)
        target = event.target()

        if re.search(string.lower(self.bot._nickname),
                     string.lower(message)):
            addressed = 1

        if message.lower() == "%s, status?" % self.bot._nickname:
            connection.privmsg(target, "I know %s phrases" %
                               str(len(self.dict.keys())))
            return

        if message.lower() == "%s reboot" % self.bot._nickname or message.lower() == "%s restart" % self.bot._nickname:
            sys.exit()

        if addressed == 1:
            silent = False

        if message.lower() == "%s silent" % self.bot._nickname:
            silent = True
        
        message = self.strip_nick(message)
        message = self.strip_shit(message)

        if chainable:
            self.input(message)
            print 'self.input(%s)' % message
        else:
            print 'not chainable'

        if not spoken:
            splitmsg = string.split(message, ' ')
            try:
                text = string.strip(self.output(splitmsg[0], splitmsg[1]))
                print 'self.output(%s %s)' % (splitmsg[0], splitmsg[1])
            except:
                text = string.strip(self.output())
                print 'self.output()'
        else:
            print 'not spoken'

        print 'bot thinks: ' + text

        # stop jeopardy
        if message.lower() == "stop jeopardy":
            jeopardy = False
            roundCount = 0

        # joke
        elif message.lower() == "joke":
            lines = open('jokes.txt').read().splitlines()
            myline = random.choice(lines)
            for joke in myline.split('<>'):
                joke = joke.strip()
                connection.privmsg(target, joke)
                #translation = subprocess.check_output(["python3","/home/user/bots/cozmo/translate.py","%s" % joke])
                #if translation != joke:
                #    connection.privmsg(target, translation)
                time.sleep(15)
        # fortune
        elif message.lower() == "fortune":
            getFortune = subprocess.check_output("fortune")
            for fortune in subprocess.check_output("fortune").split('\n'):
                connection.privmsg(target, fortune)
                time.sleep(1)
                translation = subprocess.check_output(["python3","/home/user/bots/cozmo/translate.py","%s" % fortune])
                if translation != fortune:
                    connection.privmsg(target, translation)
                    time.sleep(1)
        elif message.lower().startswith("what is") or message.startswith("what was") or message.startswith("what are") or message.startswith("who is") or message.startswith("who was") or message.startswith("who are"):
            # or translation.lower().startswith("what is") or translation.startswith("what was") or translation.startswith("what are") or translation.startswith("who is") or translation.startswith("who was") or translation.startswith("who are"):
            numSentence = 2
            if message.endswith('?'):
                numSentence = 4
            try:
                result = wikipedia.summary(message.encode('utf-8'), sentences = numSentence)
                connection.privmsg(target, result.encode('utf-8'))
            except:
                print 'wiki error'
        elif jeopardy == True:
            # correct answer
            if UnicodeDammit(answer.lower().strip()).unicode_markup in UnicodeDammit(message.lower().strip()).unicode_markup:
                # if hint == answer:
                #     tries += 1
                playerScore = 5 - tries
                connection.privmsg(target, "correct! %i points" % playerScore)
                tries = 0
                scores = open('scores.txt').read().splitlines()
                foundNick = False
                newScores = ""
                for score in scores:
                    if whonick in score:
                        foundNick = True
                        playerScore = int(score.split(' ')[1]) + playerScore
                        newScores += '%s %i' % (whonick, playerScore)
                    else:
                        newScores += score
                scoresFile = open('scores.txt', 'w')
                for line in newScores:
                    scoresFile.write(line)
                scoresFile.close()
                connection.privmsg(target, "%s has %i points" % (whonick, playerScore))
                jeopardy = False
            # hint
            elif tries < 3 and message.lower() != "next" and message.lower() != "pass" and message.lower() != "skip":
                tries += 1
                hint = ""
                count = 0
                charLoc = 0
                compare = message
                _uncovered = ""
                while len(compare) < len(answer):
                    compare += "$"
                while len(uncovered) < len(answer):
                    uncovered += "_"
                for character in answer:
                    if count < tries or character == " " or character in string.punctuation or compare[charLoc] == answer[charLoc] or uncovered[charLoc] == answer[charLoc]:
                        hint += character
                        _uncovered += character
                        if count < tries:
                            count += 1
                        if character == " " or character in string.punctuation:
                            count = 0
                    else:
                        hint += "_"
                        _uncovered += "_"
                    charLoc += 1
                uncovered = _uncovered
                textstring = hint + " " + question.replace(answer,"")
                connection.privmsg(target, textstring.encode('utf-8'))
            # wrong answer    
            else:
                tries = 0
                if message.lower() != "next" and message.lower() != "pass" and message.lower() != "skip":
                    connection.privmsg(target, "answer: " + answer.encode('utf-8'))
                else:
                    connection.privmsg(target, "skipping question. answer: " + answer.encode('utf-8'))
                jeopardy = False
                roundCount += 1

            if tries == 0:
                if roundCount > 5:
                    roundCount = 0

        # print markov text and translations
        elif message.lower() != "jeopardy":
            # text = text.replace(message, '')
            textList = text.split(' ')
            msgList = message.split(' ')
            fixedString = ''
            count = 0
            for word in textList:
                if count < len(msgList):
                    if msgList[count].lower() != word.lower():
                        fixedString += word + ' '
                else:
                    fixedString += word + ' '
                count += 1
            #fixedString = (' '.join(textList))
            fixedString = fixedString.strip()
            fixSplit = fixedString.split(' ')
            print text + ' -> ' + fixedString
            outputString = ''
            translation = ''

            try:
                translation = subprocess.check_output(["python3","/home/user/bots/cozmo/translate.py","%s" % message])
                translation = translation.replace('MDR', '')
                translation = translation.replace('Jajaja', '')
                if translation != message and len(translation) > 1:
                    outputString += translation
            except:
                print 'translation error'

            if silent == False: # and len(message.split(' ')) > 1: # and len(fixSplit) > 1:
                if addressed == True and fixedString.lower() == message.lower():
                    connection.privmsg(target, 'nods')
                else:
                    outputString = '%s .. %s' % (outputString, fixedString)
                    # connection.privmsg(target, fixedString)
            #translation = ''
            #translation = subprocess.check_output(["python3","/home/user/bots/cozmo/translate.py","%s" % text])
            #if translation != text and len(translation) > 1:
            #    connection.privmsg(target, translation)
            # translate
            connection.privmsg(target, outputString)
        # start jeopardy
        if message.lower() == "jeopardy" or (roundCount > 0 and jeopardy == False):
            success = False
            while success == False:
                try:
                    jeopardy = True
                    answer = wikipedia.random(pages=1).encode('utf-8')
                    split_answer = answer.split("(", 1)
                    answer = split_answer[0]
                    blanks = ""
                    for word in answer.split():
                        blanks += self.convert_letter(word) + " "
                    # category = wikipedia.WikipediaPage(answer).categories
                    question = wikipedia.summary(answer, sentences=3, auto_suggest=True, redirect=True)
                    blanks = UnicodeDammit(blanks).unicode_markup
                    question = UnicodeDammit(question).unicode_markup.strip()
                    answer = UnicodeDammit(answer).unicode_markup
                    textstring = blanks + question.replace(answer,"")
                    textstring = UnicodeDammit(textstring).unicode_markup
                    while answer in textstring:
                        textstring = textstring.replace(answer,"")
                        textstring = UnicodeDammit(textstring).unicode_markup
                    connection.privmsg(target, textstring.encode('utf-8'))
                    success = True
                except:
                    print 'wiki error looking up ' + answer + '(?)'
        print ''
        
    def convert_letter(self, word):
        return ''.join('_' if c in string.ascii_letters else c for c in word)


    def strip_nick(self, message):
        return string.replace(string.strip(message),
                              self.bot._nickname, '')

    def strip_shit(self, message):
        index = 0 
        for char in string.lower(message):
            if char in [',']:
                index = index + 1
            else:
                break
        return string.strip(message[index:])
        
    def input(self, originalText):
        word1, word2 = NONWORD, NONWORD
        wordList = string.split(originalText)
        for word3 in wordList: # Loop over rest of words
            if not self.dict.has_key( (word1,word2) ):
                self.dict[(word1,word2)] = [] #initialize to empty list
            self.dict[(word1, word2)].append(word3) # Add suffix for word-pair
            word1,word2 = word2, word3 # Shift in new words as dictionary keys
        self.dict[(word1,word2)] = [NONWORD] # Mark end of text
        self.savecounter = self.savecounter + 1        
        if self.savecounter >= SAVECOUNT:
            self.dumpdb()
            self.savecounter = 0
            
    def dumpdb(self):
        try:
            os.rename("markov.state.2", "markov.state.3")
        except:
            pass
        try:
            os.rename("markov.state.1", "markov.state.2")
        except:
            pass
        try:
            os.rename("markov.state", "markov.state.1")
        except:
            pass
        cPickle.dump(self.dict, open("markov.state", "w"))

    def output(self, word1=NONWORD, word2=NONWORD):
        #word1,word2 = NONWORD, NONWORD # Start at beginning
        output = word1 + " " + word2
        for i in range(MAXGEN):
            successorList = self.dict[(word1,word2)]
            word3 = random.choice(successorList)
            if word3 == NONWORD:
                break
            output = output + " "  + word3
            word1, word2 = word2, word3

        return output
