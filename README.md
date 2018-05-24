# ChatBot 
Es un chatbot hecho por *@Franko1307* y *@JoseGurrola*, estudiantes de la Licenciatura en Ciencias de la Computación en la Universidad de Sonora.
Está hecho en Python 3, utiliza: 
* [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) Para identificar palabras que pueden ser verbos, comidas, pronombres, etc.
* [Spacy](https://spacy.io/) Para identificar verbos, pronombres, adjetivos, conjunciones, adverbios en una frase.
* [Flask](http://flask.pocoo.org/)  Como entorno minimalista para desarrollo web en Python.
* [Heroku](https://www.heroku.com/). Otorga alojamiento gratuito en la web. 

El chatbot es capaz de hacer lo siguiente:
##1. Ordenar comida.
  Ejemplo:
  *Usuario*                               *Chatbot*
  "Quiero una pizza y una hamburguesa"    "Añadiendo 1  pizza a tu pedido actual. Añadiendo 1  hamburguesa a tu pedido actual."
##2. Remover algo de la orden.
  Ejemplo:
  *Usuario*                               *Chatbot*
  "remover pizza de la orden"             "Se ha removido 1 pizza  de tu lista."
##3. Recomendar comidas y bebidas segun el sabor.
   Ejemplo:
  *Usuario*                               *Chatbot*
  "Recomiendame algo salado"              "Para tu antojo salado te recomiendo: crepas."
##4. Mostrar la lista de ordenes.
   Ejemplo:
  *Usuario*                               *Chatbot*
  "enseñame la lista"                     "Lo que hay en tu orden es: 1 hamburguesa ."

