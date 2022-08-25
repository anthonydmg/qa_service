#from haystack.utils import launch_es
import wget
import gdown

## REGLAMENTO MATRICULA
doc_matricula = 'https://fc.uni.edu.pe/wp-content/uploads/2022/04/reglamento-de-matricula-29-03-2022.pdf'
wget.download(doc_matricula, 'documents/')

## MATRÍCULA REZAGADA
url = "https://drive.google.com/uc?id=1nCUQUKm1KdOJYS9Dp4N48x3Bm86Xwlmp"
gdown.download(url, output= 'documents/MATRÍCULA_REZAGADA.pdf')

## ALUMNOS EN RIESGO ACADÉMICO
url = "https://drive.google.com/uc?id=15cRuuYEbB5v_4MwuHi7l8FZYCHWjgx4V"
gdown.download(url, output= 'documents/RIESGO_ACADEMICO.pdf')

## RETIRO PARCIAL
url = "https://drive.google.com/uc?id=1HHNaREQY7WWJ2Y_rk1rtTwiDOuptZHh9"
gdown.download(url, output= 'documents/RETIRO_PARCIAL.pdf')

## RETIRO TOTAL
url = "https://drive.google.com/uc?id=1MHa9Mrsu8qsStzqFKgVAVYUoJMHjMKOt"
gdown.download(url, output= 'documents/RETIRO_TOTAL.pdf')


## REINCORPORACIÓN
url = "https://drive.google.com/uc?id=1WCZ54XQL16yRjT_h20fPQmDXS4daDfRi"
gdown.download(url, output= 'documents/REINCORPORACIÓN.pdf')


## RESERVA DE MATRÍCULA
url = "https://drive.google.com/uc?id=15ZZvoi1etESzH54Qd-xZNOV240cJ0UdH"
gdown.download(url, output= 'documents/RESERVA_DE_MATRÍCULA.pdf')

## EVALUACIÓN DE REGULARIZACIÓN
url = "https://drive.google.com/uc?id=1PkJShOgvz60qDpy5Yti8UupqLTf3wNLT"
gdown.download(url, output= 'documents/EVALUACIÓN_DE_REGULARIZACIÓN.pdf')

## EVALUACIÓN TRASLADO INTERNO
url = "https://drive.google.com/uc?id=1_O6RE6ixUwLXyqaw4AnZXjZuQHE8MJeG"
gdown.download(url, output= 'documents/TRASLADO_INTERNO.pdf')