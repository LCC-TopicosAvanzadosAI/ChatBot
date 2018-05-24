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
    qt = int(cast_to_number(noun[1]))
    nt = noun[0]
    tupla = process.extractOne(nt, list(order.keys()))

    if tupla and tupla[1] > 80:
        nt = tupla[0]

    if nt in order:
        order[nt] += qt
        response = "Añadiendo " + cast_to_number(qt) + "  " + nt + "más tu pedido actual. " 
    else:
        order[nt] = qt
        response = "Añadiendo " + cast_to_number(qt) + "  " + nt + "a tu pedido actual. "

    return response,order

def remove_from_list(sentence, order):
    noun = get_noun(sentence)
    response = ""

    print("NOUN: ", noun)
    qt = int(cast_to_number(noun[1]))
    nt = noun[0]
    tupla = process.extractOne(nt, list(order.keys()))

    if tupla[1] > 80:
    	nt = tupla[0]

    if nt in order:
    	if order[nt] >= qt:
    		order[nt] -= qt

    		if order[nt] == 0:
    			response = "Se ha removido " + str(qt) + " " + nt + " de tu lista."
    			del order[nt]
    		elif order[nt] >= 2:
    			response = "Se han removido " + str(qt) + " " + nt + " de tu lista."
    	else:
    		response = "No se puede remover " + str(qt) + " de " + nt + "cuando solo hay " + str(order[nt])
    else:
    	response = "Usted no ha ordenado " + nt + "."

    return response, order
    
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

def detect_flavor(order):
	for word in order:
		if word.pos_ == "ADJ" and process.extractOne(word.text, ["dulce", "salado", "picante", "amargo", "agrio"]) [1] > 71:
			return word.text
	return "none"

def recomend(order):
	sabor = detect_flavor(order)
	if sabor is not "none":
		response = "Para tu antojo " + sabor + " te recomiendo: " + random.choice(open_json("recomendaciones")[sabor])
		
	else:
		response = "No reconozco ese sabor."
	return response

def show_list(order):
    response = "Lo que hay en tu orden es:\n" 
    for o in order:
        response += str(order[o]) + " " + o + "\n" 

    return response

def cast_to_number(number):
    if type(number) is int:
        return str(number)
    else:
        if number in nums:
            return str(nums[number])
        else:
            return number
#Funcion encargada de responder al usuario
def respond(sentence, diccionario):
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
            resp,diccionario = add_to_list(parsed[idx],diccionario)
            response += resp
        elif orden == "remover":
            resp,diccionario = remove_from_list(parsed[idx], diccionario)
            response += resp
        elif orden == "recomendar":
        	response = recomend(parsed[idx])
        elif orden == "mostrar":
            resp = show_list(diccionario)
            response += resp

    #print(diccionario)

    return response, diccionario

#Testeo
import unittest

#Clase para testeo de casos
class MyTest(unittest.TestCase):
    def test(self):
        resp, order = broback("Hola. Quisiera una hamburguesa, tres pizzas de queso con anchoas, unas salchichas y una coca de dieta por favor", {})
        print("---------------------------------------")
        resp, order = broback("mostrar la orden plis",order)
        #resp, order = broback("cambiar la hamburguesa por una malteada", order)
        #resp, order = broback("Quiero remover tres hamburguesas ", order)
        #resp, order = broback("Quiero una pizza y recomiendame algo amargo", {})
        print(resp, order)
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



