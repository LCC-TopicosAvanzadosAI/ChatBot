from __future__ import print_function, unicode_literals
import random
import logging
import os
import spacy
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from operator import itemgetter
from operator import add
import es_core_news_sm
from functools import reduce


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def broback(sentence, orden):
    logger.info("Broback: respond to %s", sentence)
    orden = respond(sentence,orden)
    return orden

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

import json
def open_json(route):
    with open("data/json/"+route+".json") as f:
        data = json.load(f)
    return data

#Funcion encargada de agarrar la orden y transformarla en una orden mas general, es decir cosas como "pedir, solicitar, dar" -> "ordenar"
def process_order(orden):
    json_ordenes = open_json("ordenes")
    for key, value in json_ordenes.items():
        if orden in value:
            return key
    return orden

#funcion que regresa posibles ordenes que el usuario pudiera dar
def get_orders():
    return reduce(add, open_json("ordenes").values())

#Funcion que filtra los verbos en una sentencia y los retorna
def get_verbs(sentence):
    verbs = []
    for word in sentence:
        #print(word, word.tag_)
        if word.pos_ == 'VERB':
            verbs.append(word.text)
    return verbs

#Funcion que nos permite deducir que es lo que el usuario quiere que hagamos, ejemplos: ordenar, remover, cambiar, etc...
def detect_order(sentence):

    verbs = get_verbs(sentence)

    possible_orders = get_orders()

    candidates = []

    for verb in verbs:
        candidates.append(process.extractOne(verb,possible_orders))
    if len(candidates) > 0:
        orden, score = max(candidates, key=itemgetter(1))
    else:
        #ordenar es por default.
        orden = "ordenar"
        score = 0
    print("Orden: ", orden, " candidatos: ", candidates)
    if score > 75:
        return process_order(orden)
    return "ordenar"

#Funcion encargada de detectar y unir todos los nouns
def get_noun(sentence):
    nouns = []

    idx = 0
    isClosed = True
    noun = ""
    for word in sentence:
        if isClosed:
            noun = ""
            isClosed = False
        if word.pos_ == "NOUN" or word.pos_ == "ADP":
            noun += word.text + " "
        else:
            isClosed = True
        if isClosed and noun != "":
            nouns.append((noun,1))

    if noun != "":
        nouns.append((noun,1))

    return nouns
#Esta funcion busca en la oracion, los adjetivos que son los elementos que el usuario ordeno y los aniade a la lista de compras
def add_to_list(sentence, order):
    #Obtenemos los nouns, cosas como pizza de queso, hamburguesa, coca de dieta, etc... (Funcionando 60%)
    nouns = get_noun(sentence)
    response = ""
    #TODO: La variable qt representa la cantidad, esta por default a 1, pero se deberia poder leer esa cantidad en la sentencia dada por el usuario y pedirla en caso de que no se nos solicite, por ejemplo en el caso de : Me da unas pizzas. Debemos pedirle al usuario que reingrese su sentencia con la informacion mas completa
    for noun in nouns:
        #Estructura de noun : (NOUN, CANTIDAD)
        qt = noun[1]
        if noun[0] in order:
            response = "Claro, le he agregado " + noun + " ha su pedido."
            order[noun[0]] += qt
        else:
            order[noun[0]] = qt
    return response,order

def remove_from_list(sentence, order):
    nouns = get_noun(sentence)
    response = ""
    for noun in nouns:
        qt = noun[1]
        if noun[0] in order:
            response = "Claro, le he removido " + noun[0] + " de su pedido"
            order[noun[0]] -= qt
        else:
            response = "No recuerdo que me haya pedido " + noun[0] + " por favor, pruebe de nuevo."
    return response,order


#Funcion encargada de responder al usuario
def respond(sentence, list):
    #Se carga lo relacionado a spacy
    nlp = es_core_news_sm.load()
    parsed = nlp(sentence)

    #Para imprimir los tags que spacy nos ofrece
    for word in parsed:
        print(word.text, word.pos_, word.tag_)

    #Detectamos que orden desea el cliente (Funcionando 80%, pasa los testeos pero no la he testeado bien)
    orden = detect_order(parsed)

    #Dependiendo de la orden hacemos lo que se nos pida
    #Nota: Ordenar es la mas completa, remover esta mas o menos completa, cambiar esta incompleta y se espera que podamos brindar mas ordenes
    if orden == "ordenar":
        list = add_to_list(parsed,list)
    elif orden == "remover":
        remove_from_list(parsed, list)
    elif orden == "cambiar":
        change_from_list(parsed, list)
    else:
        return orden

    return orden

#Testeo
import unittest

#Clase para testeo de casos
class MyTest(unittest.TestCase):
    def test(self):
        self.assertEqual(broback("Quisiera ordenar una pizza",{}), "ordenar")
        self.assertEqual(broback("Quisiera una pizza",{}), "ordenar")
        self.assertEqual(broback("Me das una pizza de queso",{}), "ordenar")
        self.assertEqual(broback("Me quitas la pizza de anchoas por favor",{}), "remover")
        self.assertEqual(broback("Va a ser una hamburguesa con papas",{}), "ordenar")
        self.assertEqual(broback("Me remueves las salchichas por favor",{}), "remover")
        self.assertEqual(broback("Quiero ordenar tres pizzas por favor",{}), "ordenar")
        self.assertEqual(broback("Quiero ordenar unas pizzas  por favor",{}), "ordenar")
        self.assertEqual(broback("Quiero unas 3 pizzas por favor",{}), "ordenar")
        self.assertEqual(broback("Me da unas cuatro hamburguesas",{}), "ordenar")
        logger.info("OKAY, EVERYTHING LOOKS GOOD!")


if __name__ == '__main__':
    tester = MyTest()
    tester.test()



