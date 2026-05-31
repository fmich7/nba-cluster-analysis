import generator_danych
sesje, konflikty,sale = generator_danych.generuj_dane_konferencji(liczba_sesji=20, szansa_na_konflikt=0.3, mindlugosc=60, maxdlugosc=60, ilosc_sali=3)
sesje.sort(reverse=True,key=lambda x: (x['ilosc_konfliktow'],x['dlugosc'], x['rozmiar']))
sale.sort(reverse=True,key=lambda x: x['rozmiar'])
for i in range(len(sesje)):
    wpisane = False
    for j in range(len(sale)):
        print(sesje[i]["nazwa"] ,sale[j]["nazwa"])
        if sale[j]["rozmiar"]>=sesje[i]["rozmiar"]:
            for k in range(32):
                if sale[j]["harmonogram"][k] is None:
                    if k+sesje[i]["dlugosc"]//15<=32:
                        for l1 in range(k,k+sesje[i]["dlugosc"]//15):
                            for konflikt in konflikty:
                                if konflikt[0]["nazwa"]==sesje[i]["nazwa"] and konflikt[1]["nazwa"]==sale[j]["harmonogram"][l1]:
                                    break
                        for l2 in range(k,k+sesje[i]["dlugosc"]//15):
                            sale[j]["harmonogram"][l2] = sesje[i]["nazwa"]
                        wpisane = True
                        break
        if wpisane==True:
            break
    if wpisane==False:
        print("nie można wpisać sesji ",sesje[i]["nazwa"],sesje[i]["ilosc_konfliktow"]," do żadnej sali")    
print(sale[0]["harmonogram"])
print("\n")
print(sale[1]["harmonogram"])
print("\n")
print(sale[2]["harmonogram"])