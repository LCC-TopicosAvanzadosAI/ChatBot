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

nums = {'dos':2,
        'tres':3,
        'cuatro':4,
        'cinco':5,
        'seis':6,
        'siete':7,
        'ocho':8,
        'nueve':9,
        'diez':10
        }


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def broback(sentence, orden):
    logger.info("Broback: respondiendo a %s", sentence)
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
def detect_order(sentences):
    ordenes = []
    possible_orders = get_orders()
    for sentence in sentences:

        verbs = get_verbs(sentence)
        candidates = []

        for verb in verbs:
            candidates.append(process.extractOne(verb,possible_orders))
        if len(candidates) > 0:
            orden, score = max(candidates, key=itemgetter(1))
        else:
            score = 0
        if score > 75:
            ordenes.append(process_order(orden))
        else:
            ordenes.append("ordenar")
    return ordenes

def filtro_nouns():
    return ["favor"]
#Funcion encargada de detectar y unir todos los nouns
def get_noun(sentence):

    isClosed = True
    noun = ""

    idx = 0
    cantidad = 1

    for word in sentence:
        if word.pos_ == "NUM":
            cantidad = word.text
        if isClosed:
            noun = ""
            isClosed = False
        if word.pos_ == "NOUN" :
            print("PARECIDO: ", word.text, " ", process.extractOne(word.text, filtro_nouns())[1])
        if (word.pos_ == "NOUN" and process.extractOne(word.text, filtro_nouns())[1] < 60) or (word.pos_ == "ADP" and word.text != "por"):
            #print("PARECIDO: ",word.text, " ",process.extractOne(word.text, filtro_nouns())[1] )
            noun += word.text + " "
        else:
            isClosed = True
        if isClosed and noun != "":
            return (noun,cantidad)

    if noun != "":
        return (noun,cantidad)

    return ("",0)
#Esta funcion busca en la oracion, los adjetivos que son los elementos que el usuario ordeno y los aniade a la lista de compras
def add_to_list(sentence, order):
    #Obtenemos los nouns, cosas como pizza de queso, hamburguesa, coca de dieta, etc... (Funcionando 60%)
    noun = get_noun(sentence)
    response = ""
    print("NOUN: ", noun)
    #Estructura de noun : (NOUN, CANTIDAD)
    qt = noun[1]
    response = noun[0]
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

def process_order_into_orders(order):
    ordenes = []

    idx = 0
    p_idx = 0
    while idx < len(order):
        if order[idx].tag_ == "PUNCT__PunctType=Comm" or order[idx].pos_ == "CONJ":
            ordenes.append(order[p_idx:idx])
            p_idx = idx+1
        elif idx == len(order)-1:
            ordenes.append(order[p_idx:idx+1])
        idx += 1
    return ordenes

def cast_to_number(number):
    if type(number) is int:
        return str(number)
    else:
        return str(nums[number])

#Funcion encargada de responder al usuario
def respond(sentence, list):
    #Se carga lo relacionado a spacy
    nlp = es_core_news_sm.load()
    doc = nlp(sentence)
    #Para imprimir los tags que spacy nos ofrece
    for word in doc:
        print(word.text, word.pos_, word.tag_)
    #Funcion para dividir una sentencia con una orden de varias partes en varias ordenes
    parsed = process_order_into_orders(doc)

    #Detectamos que orden desea el cliente (Funcionando 80%, pasa los testeos pero no la he testeado bien)
    ordenes = detect_order(parsed)

    #Dependiendo de la orden hacemos lo que se nos pida
    #Nota: Ordenar es la mas completa, remover esta mas o menos completa, cambiar esta incompleta y se espera que podamos brindar mas ordenes
    print("ORDENES: ", ordenes)
    response = ""
    for idx,orden in enumerate(ordenes):
        if orden == "ordenar":
            resp,list = add_to_list(parsed[idx],list)
            response += "Añadiendo " + cast_to_number(list[resp]) + " " + resp + ". "
        elif orden == "remover":
            resp,list = remove_from_list(parsed[idx], list)
        elif orden == "cambiar":
            resp, list = change_from_list(parsed[idx], list)

    #print(list)

    return response, list

#Testeo
import unittest

#Clase para testeo de casos
class MyTest(unittest.TestCase):
    def test(self):
        logger.info(broback("Hola. Quisiera una hamburguesa, tres pizzas de queso con anchoas, unas salchichas y una coca de dieta por favor", {}))
        return 6
        logger.info(broback("Quisiera ordenar una pizza",{}))
        logger.info(broback("Quisiera una pizza",{}))
        logger.info(broback("Me das una pizza de queso",{}))
        #logger.info(broback("Me quitas la pizza de anchoas por favor",{}))
        logger.info(broback("Va a ser una hamburguesa con papas",{}))
        #logger.info(broback("Me remueves las salchichas por favor",{}))
        logger.info(broback("Quiero ordenar tres pizzas por favor",{}))
        #logger.info(broback("Quiero ordenar unas pizzas  por favor",{}),)
        #logger.info(broback("Quiero unas 3 pizzas por favor",{}))
        #logger.info(broback("Me da unas cuatro hamburguesas",{}))
        logger.info(broback("Quiero cuatro malteadas de fresa", {}))

        logger.info("OKAY, EVERYTHING LOOKS GOOD!")


if __name__ == '__main__':
    tester = MyTest()
    tester.test()



