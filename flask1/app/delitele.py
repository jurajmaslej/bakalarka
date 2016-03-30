__author__ = 'Jurko'

def delitele (n):
    max = n/2
    count = 0
    for i in range (1,round(max) + 1):
        if (n % i == 0):
            count += 1
    count += 1 # este priratam ako delitela nka aj nko samotne

    return count

##print(delitele(8)) nevsimaj si toto

def find_numbers():
    count = 0
    for i in range ( 1, 1000):
        if (delitele(i) == 2): # ak je pocet delitelov 2 lebo delitelmi su aj 1 a cislo samotne , volam funckiu delitele
            count += 1
    return count
print(find_numbers())
