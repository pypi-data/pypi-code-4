#!/usr/bin/env python
# -*- coding: utf8 -*-

from etiquetando import Etiquetador

texto = u"""Uma caneca é uma variedade de recipiente semelhante a um copo, porém com uma alça denominada "asa". Ao contrário da xícara, é geralmente maior e não necessita de pires, pois sua forma não é cunhada. Fonte (Alça de Águia).

A caneca é um recipiente resistente, que é destinado para a armazenar líquidos em temperaturas elevadas, isto é, bebida frequentemente quentes como café, chá, chocolate quente, leite. Também usada para bebidas frias como vinhos, cerveja, champanhe e outros
Aparência

Esse objeto pode possuir formatos diversos. A caneca se difere do copo e da xicara, pois possui tipo de "asa" anelar para facilitar seu manuseio.
Composição

As canecas são feitas geralmente de porcelana, porém algumas são produzidas a partir de um vidro resistente a choques térmicos com a marca Pyrex, e outras de plástico, de metais (como aço e alumínio) alguns esmaltados ou cerâmica. Também há canecas térmicas feitas de material que muda de cor com a temperatura. (Caneca Mágica)

A sua igualdade topológica com um donut é um dos exemplos mais utilizados como introdução à topologia.

Fonte: http://pt.wikipedia.org/wiki/Caneca"""

etiquetador = Etiquetador()
for tag, peso in etiquetador(texto):
    print tag, peso
print

etiquetador = Etiquetador(max_tags=8)
for tag, peso in etiquetador(texto):
    print tag, peso
print

etiquetador = Etiquetador(max_tags=12, weight_range=(1,4))
for tag, peso in etiquetador(texto):
    print tag, peso
print
