from __future__ import print_function, unicode_literals
import random
import logging
import os
import spacy



os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'

#from textblob import TextBlob
from config import FILTER_WORDS

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# start:example-hello.py
# Sentences we'll respond with if the user greeted us
GREETING_KEYWORDS = ("hola", "hey", "saludos", "que pedo?", "que tranza",)

GREETING_RESPONSES = ["que pex", "hey", "que pasa", "que pedo we"]

def check_for_greeting(sentence):
    """If any of the words in the user's input was a greeting, return a greeting response"""
    for word in sentence:
        if word.text.lower() in GREETING_KEYWORDS:
            return random.choice(GREETING_RESPONSES)

# start:example-none.py
# Sentences we'll respond with if we have no idea what the user just said
NONE_RESPONSES = [
    "NANI????",
    "NANDATO???",
    "Demaciado para mi we",
    "La neta, no me importa xD",
    "No mames",
    "Esa wea ke?",
    "No entendi we",
]
# end

# start:example-self.py
# If the user tries to tell us something about ourselves, use one of these responses
COMMENTS_ABOUT_SELF = [
    "Yo me amo mucho",
    "He sido programado por los mejores",
    "La vida es hermosa, porque yo existo",
]
# end


class UnacceptableUtteranceException(Exception):
    """Raise this (uncaught) exception if the response was going to trigger our blacklist"""
    pass


def starts_with_vowel(word):
    """Check for pronoun compability -- 'a' vs. 'an'"""
    return True if word[0] in 'aeiou' else False


def broback(sentence):
    """Main program loop: select a response for the input sentence and return it"""
    logger.info("Broback: respond to %s", sentence)
    resp = respond(sentence)
    return resp

# start:example-construct-response.py
def construct_response(pronoun,aux, noun, verb, det):
    """No special cases matched, so we're going to try to construct a full sentence that uses as much
    of the user's input as possible"""
    resp = []

    # We always respond in the present tense, and the pronoun will always either be a passthrough
    # from the user, or 'you' or 'I', in which case we might need to change the tense for some
    # irregular verbs.
    if aux:

        aux_word = aux.text
        print("aux word: ", aux_word)
        if aux_word == 'soy':  # This would be an excellent place to use lemmas!
                # The bot will always tell the person they aren't whatever they said they were
            resp.append(random.choice(["nah, no eres", "tal ves seas"]))
    if det is not "":
        resp.append(det.text)
    if noun is not "":
        #pronoun = "an" if starts_with_vowel(noun) else "a"
        resp.append(noun.text)
    


    resp.append(random.choice(("we", "")))

    return " ".join(resp)
# end


# start:example-check-for-self.py
def check_for_comment_about_bot(pronoun, noun, adjective):
    """Check if the user's input was about the bot itself, in which case try to fashion a response
    that feels right based on their input. Returns the new best sentence, or None."""
    resp = None
    if pronoun is not "":
        #print(pronoun.text == "tú" and noun)
        if pronoun.text =='tú' or pronoun.text == "tu" and (noun or adjective):
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
# Template for responses that include a direct noun which is indefinite/uncountable
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
    """Handle some weird edge cases in parsing, like 'i' needing to be capitalized
    to be correctly identified as a pronoun"""
    cleaned = []
    words = sentence.split(' ')
    for w in words:
        if w == 'i':
            w = 'I'
        if w == "i'm":
            w = "I'm"
        cleaned.append(w)

    return ' '.join(cleaned)

# start:example-respond.py
def respond(sentence):
    """Parse the user's inbound sentence and find candidate terms that make up a best-fit response"""
    cleaned = preprocess_text(sentence)
    #parsed = TextBlob(cleaned)

    nlp = spacy.load('es')
    parsed = nlp(sentence)
    # Loop through all the sentences, if more than one. This will help extract the most relevant
    # response text even across multiple sentences (for example if there was no obvious direct noun
    # in one sentence
    pronoun, aux, noun, adjective, verb, det = find_candidate_parts_of_speech(parsed)

    # If we said something about the bot and used some kind of direct noun, construct the
    # sentence around that, discarding the other candidates
    resp = check_for_comment_about_bot(pronoun, noun, adjective)

    # If we just greeted the bot, we'll use a return greeting
    if not resp:
        resp = check_for_greeting(parsed)

    if not resp:
        # If we didn't override the final sentence, try to construct a new one:
        if not pronoun:
            resp = random.choice(NONE_RESPONSES)
        elif pronoun.text == 'tu' and not verb:
            resp = random.choice(COMMENTS_ABOUT_SELF)
        else:
            resp = construct_response(pronoun,aux, noun, verb,det)

    # If we got through all that with nothing, use a random response
    if not resp:
        resp = random.choice(NONE_RESPONSES)

    logger.info("Returning phrase '%s'", resp)
    # Check that we're not going to say anything obviously offensive
    filter_response(resp)

    return resp

def find_candidate_parts_of_speech(parsed):
    """Given a parsed input, find the best pronoun, direct noun, adjective, and verb to match their input.
    Returns a tuple of pronoun, noun, adjective, verb any of which may be None if there was no good match"""


   # print("sent_:", sent_, "\tPOS: ", sent_.pos_, "\tTAG: ", sent_.tag_)

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

# end
    
# start:example-filter.py
def filter_response(resp):
    """Don't allow any words to match our filter list"""
    tokenized = resp.split(' ')
    for word in tokenized:
        if '@' in word or '#' in word or '!' in word:
            raise UnacceptableUtteranceException()
        for s in FILTER_WORDS:
            if word.lower().startswith(s):
                raise UnacceptableUtteranceException()
# end
    
if __name__ == '__main__':
    import sys
    # Usage:
    # python broize.py "I am an engineer"
    if (len(sys.argv) > 0):
        saying = sys.argv[1]
    else:
        saying = "How are you, brobot?"
    print(broback(saying))
