from __future__ import print_function, unicode_literals
import random
import logging
import os
import spacy

os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'

from config import FILTER_WORDS

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

GREETING_KEYWORDS = ("hola", "hey", "saludos", "que pedo?", "que tranza",)

GREETING_RESPONSES = ["que pex", "hey", "que pasa", "que pedo we"]



def check_for_greeting(sentence):
    for word in sentence:
        if word.text.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)


NONE_RESPONSES = [
    "NANI????",
    "NANDATO???",
    "Demasiado para mi we",
    "La neta, no me importa xD",
    "No mames",
    "Esa wea ke?",
    "No entendi we",
]
# end

COMMENTS_ABOUT_SELF = [
    "Yo me amo mucho",
    "He sido programado por los mejores",
    "La vida es hermosa, porque yo existo",
]
# end


class UnacceptableUtteranceException(Exception):
    pass

def broback(sentence):
    logger.info("Broback: respond to %s", sentence)
    resp = respond(sentence)
    return resp

def construct_response(pronoun,aux, noun, verb, det):
    resp = []

    if aux:

        aux_word = aux.text
        print("aux word: ", aux_word)
        if aux_word == 'soy':  
            resp.append(random.choice(["nah, no eres", "tal ves seas"]))
    if det is not "":
        resp.append(det.text)
    if noun is not "":
        resp.append(noun.text)
    
    resp.append(random.choice(("we", "")))

    return " ".join(resp)
# end


def check_for_comment_about_bot(pronoun, noun, adjective):
    resp = None
    if pronoun is not "":
        if pronoun.text =='tu' or pronoun.text == "tu" and (noun or adjective):
            if noun is not "":

                if random.choice((True, False)):
                    resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': sing_to_plural(noun)})
                else:
                    resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
            else:
                resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp

def sing_to_plural(noun):
    var = noun.text.split(',')
    if var[-1] not in ['a', 'e', 'i', 'o', 'u']: 
        var.append('es')
    else:
        var.append('s')
    return ''.join(var) 

SELF_VERBS_WITH_NOUN_CAPS_PLURAL = [
    "la neta estoy bien pesado en {noun}",
]

SELF_VERBS_WITH_NOUN_LOWER = [
    "si, pero se mucho de {noun}",
    "Mis compas siempre me preguntan de {noun}",
]

SELF_VERBS_WITH_ADJECTIVE = [
    "a quien le dices {adjective} we", 
    "tal vez sea {adjective} we",
    "soy tan {adjective} como tu we",
    "ya lo se, me paso de lanza",
]
# end

def preprocess_text(sentence):
    cleaned = []
    words = sentence.split(' ')
    for w in words:
        if w == 'i':
            w = 'I'
        if w == "i'm":
            w = "I'm"
        cleaned.append(w)

    return ' '.join(cleaned)

def respond(sentence):
    cleaned = preprocess_text(sentence)

    nlp = spacy.load('es')
    parsed = nlp(sentence)

    pronoun, aux, noun, adjective, verb, det = find_candidate_parts_of_speech(parsed)

    resp = check_for_comment_about_bot(pronoun, noun, adjective)

    if not resp:
        resp = check_for_greeting(parsed)

    if not resp:
        if not pronoun:
            resp = random.choice(NONE_RESPONSES)
        elif pronoun.text == 'tu' and not verb:
            resp = random.choice(COMMENTS_ABOUT_SELF)
        else:
            resp = construct_response(pronoun,aux, noun, verb,det)

    if not resp:
        resp = random.choice(NONE_RESPONSES)

    logger.info("Returning phrase '%s'", resp)

    filter_response(resp)

    return resp

def find_candidate_parts_of_speech(parsed):

    pronoun, aux, noun, adjective, verb, det =[], [], [], [], [], []

    for word in parsed:
        print(word.pos_,word.tag_)
        if word.pos_ == 'PRON':
            pronoun.append(word)
        elif word.pos_ is "AUX":
            aux.append(word)    
        elif word.pos_ == 'NOUN':
            noun.append(word)
        elif word.pos_ == 'ADJ':
            adjective.append(word)
        elif word.pos_ == 'VERB':
            verb.append(word)
        elif word.pos_ == 'DET':
            det.append(word)

    pronoun.append('')
    aux.append('')
    noun.append('')
    adjective.append('')
    verb.append('')
    det.append('')

    print(pronoun, aux, noun, adjective, verb, det)
    logger.info("Pronoun=%s, noun=%s, adjective=%s, verb=%s", pronoun[0], noun[0], adjective[0], verb[0])
    return pronoun[0],aux[0], noun[0], adjective[0], verb[0], det[0]

def filter_response(resp):
    """Don't allow any words to match our filter list"""
    tokenized = resp.split(' ')
    for word in tokenized:
        if '@' in word or '#' in word or '!' in word:
            raise UnacceptableUtteranceException()
        for s in FILTER_WORDS:
            if word.lower().startswith(s):
                raise UnacceptableUtteranceException()
    
if __name__ == '__main__':
    """import sys
    if (len(sys.argv) > 0):
        saying = sys.argv[1]
    else:
        saying = "How are you, brobot?"
    print(broback(saying))"""
    while True:
    	sentence = input()
    	print(broback(sentence))
