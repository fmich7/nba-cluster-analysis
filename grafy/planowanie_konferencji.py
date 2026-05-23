import generator_danych
sesje, konflikty,sale = generator_danych.generuj_dane_konferencji(liczba_sesji=8, szansa_na_konflikt=0.3, mindlugosc=15, maxdlugosc=120, ilosc_sali=3)
sesje.sort(reverse=True,key=lambda x: (x['ilosc_konfliktow'],x['dlugosc'], x['rozmiar']))
sale.sort(reverse=True,key=lambda x: x['rozmiar'])
print (sesje)

