import numpy as np

#exemple de demonstration pour utiliser des microphones pour detecter
#la localisation du ballon avec le bruit lors de l'impact.
# Daniel Perron  Avril 2019.
#
# Code traduit en python avec modification de la resolution de matrice pour permettre un nombre sans limite de microphone
# utilisation de numpy pour la matrice.
##
#
#  La vitesse du son dans l'air depend beaucoup de la temperature il serait donc pratique de faire un lancer pour determiner la
#  vitesse du son  et de corriger C. 
#  C pour la vitesse du son dans l'air (m/s)
#  343 m/s 20C    
#  v = 331m/s + 0.6m/s/C * T   
C = 343.0

#  
#
# ref:
# https://people.ece.cornell.edu/land/courses/ece4760/FinalProjects/s2007/sp369_bb226/sp369_bb226/index.htm

# position des micros (x,y ,z) en metre

micros = []
micros.append([0,0,1])
micros.append([3,0,0])
micros.append([0,3,0])
micros.append([3,3,1])

#le nombre de micro n'est pas limité
#micros.append([1.5,5,0])
#micros.append([0,3,1])

# Calculation d'un ballon dummy pour verifier

ballon = [ 1.2 , 3.0 , 0]

# Ok calculons le temps pour chaque micro

t = []

for mic in micros:
  t.append( pow( pow(ballon[0] - mic[0],2) + pow(ballon[1]-mic[1],2) + pow(ballon[2] - mic[2],2),.5) / C)
  
#forçons le plus proche de l'impact a etre la base de temps;
# ce qui enleve en theorie la distance reel de l'impact
#  normallement nous ne l'avons pas.
# ce n'est pas necessaire mais plus lisible avec des chiffres positifs.

base = min(t)

for i in range(len(t)):
    t[i] = t[i] - base;
  
# ok nous avons notre temps de test 
# maintenant determinons la location

for i in range(len(t)):
  print("micro #{} : {:3.4f} sec".format(i+1,t[i]))
  
def  addVect4(a,b):
    global reponse
    for i in range(4):
        reponse[i] = a[i]+b[i]
 
  
def dfdvar(answer, position, idx):
    global C
    temp = 0.0
    if idx==3:
       return C
    temp = function1(answer,position)
    temp = pow(temp, -0.5) *(answer[idx]-position[idx])
    return temp
      
  
def function1(answer,position):
    temp = 0.0
    for i in range(3):
       temp = temp + pow(answer[i] - position[i],2)
    return temp
  
def negFunction(answer,position,delais):
    temp=0.0
    temp=function1(answer,position)
    temp= pow(temp,0.5) - C *(delais - answer[3])
    return -temp
    
def norm4(vector):
    temp = 0.0
    for i in vector:
      temp= temp + pow(i,2)
    return temp



#Calculation par matrice avec les equations Newton Raphson.   
#dummy reponse
reponse = np.array([ 1.0 , 1.0 , 1.0 , 50.0])

#dummy update
update =  np.array([ 50.0 , 0.0 ,0.0 ,0.0])
inverse4Result = np.empty([len(micros),4])

#create array

array = np.empty([len(micros),4])


#error
negF = len(micros)*[0]
#print("micros",micros)
diff = 0.0
while True:
  diff = norm4(update)
  #print("diff",diff)
  if diff  <= 0.000001:
      break;
  for i in range(len(micros)):
    negF[i] = negFunction(reponse,micros[i],t[i])
  #print("negF",negF)
#fill array
  for i in range(len(micros)):
    for j in range(4):
     array[i][j] = dfdvar(reponse,micros[i],j);
  #print("array",array)

#modification du code original pour pouvoir utiliser plusieur micros au lieu d'etre pris avec 4 micros
#
#  pour 3 dimensions le minimum est de 4 micros et au moins un(deux c'est mieux) avec une position z differente.
#  pour 2 dimensions il est possible d'utiliser seulement 3 micros mais il faut changer le code pour avoir seulement  x et y
#
#   nouvelle formule matrice
#
#      inverse(transpose(M) * M) * transpose(M) * negF


  tr_array = np.transpose(array)
  xr = np.matmul(tr_array,array)
  inverse4Result = np.linalg.inv(xr)
  xr = np.matmul(inverse4Result,tr_array)
  update = np.matmul(xr,negF)
  #print("reponse",reponse)
  #print("update",update)
  addVect4(reponse,update)

print("Location X:{:.2f}m Y:{:.2f}m Z:{:.2f}m ".format(reponse[0],reponse[1],reponse[2]))

