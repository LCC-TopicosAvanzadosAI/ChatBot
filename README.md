# ChatBot 
Es un chatbot hecho por *@Franko1307* y *@JoseGurrola*, estudiantes de la Licenciatura en Ciencias de la Computación en la Universidad de Sonora.
Está hecho en Python 3, utiliza: 
* [fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) Para identificar palabras que pueden ser verbos, comidas, pronombres, etc.
* [Spacy](https://spacy.io/) Para identificar verbos, pronombres, adjetivos, conjunciones, adverbios en una frase.
* [Flask](http://flask.pocoo.org/)  Como entorno minimalista para desarrollo web en Python.
* [Heroku](https://www.heroku.com/). Otorga alojamiento gratuito en la web. 

El chatbot es capaz de hacer lo siguiente:<br>
1. **Ordenar comida.**<br>
  --------------------
  Ejemplo:<br>
  Usuario<br>
    "Quiero una pizza y una hamburguesa"    
  Chatbot<br>
    "Añadiendo 1  pizza a tu pedido actual. Añadiendo 1  hamburguesa a tu pedido actual."<br>
  
2. **Remover algo de la orden.**<br>
  ---------------------------
  Ejemplo:<br>
  Usuario<br>                               
    "remover pizza de la orden"
  Chatbot<br>
    "Se ha removido 1 pizza  de tu lista."<br>
  
3. **Recomendar comidas y bebidas segun el sabor.**<br>
  ---------------------------
  Ejemplo:<br>
  Usuario<br>                               
    "Recomiendame algo salado"
  Chatbot<br>
    "Para tu antojo salado te recomiendo: crepas."<br>
  
4. **Mostrar la lista de ordenes.**<br>
  ---------------------------
  Ejemplo:<br>
  Usuario<br>                               
    "enseñame la lista"
  Chatbot<br>
    "Lo que hay en tu orden es: 1 hamburguesa ."<br>

