import random

def generuj_dane_konferencji(liczba_sesji, szansa_na_konflikt,mindlugosc,maxdlugosc,ilosc_sali=3):
    """
    Generuje losowe dane wejściowe dla problemu planowania konferencji.
    Zwraca listę sesji oraz listę krotek reprezentujących konflikty.
    """
    sesje = []
    konflikty = []
    sale=[]
    max_rozmiar_sesji=0
    max_rozmiar_sali=0
    for i in range(liczba_sesji):
        sesja = {
            "nazwa": f"S{i+1}",
            "dlugosc": random.randint(int(mindlugosc/15), int(maxdlugosc/15)) * 15,
            "rozmiar": random.randint(1, 3) * 50,
            "ilosc_konfliktow": 0
        }
        if sesja["rozmiar"]>max_rozmiar_sesji:
            max_rozmiar_sesji = sesja["rozmiar"]
        sesje.append(sesja)
    for i in range(ilosc_sali):
        sala={
            "nazwa": f"Sala{i+1}",
            "rozmiar": random.randint(1, 3) * 50,
            "harmonogram": [None] * 32
        }
        if sala["rozmiar"] > max_rozmiar_sali:
            max_rozmiar_sali = sala["rozmiar"]
        sale.append(sala) 

    if max_rozmiar_sali < max_rozmiar_sesji:
        print(f"zmieniam rozmiar sali z {max_rozmiar_sali} na {max_rozmiar_sesji}")
        sale[0]["rozmiar"] = max_rozmiar_sesji
        

    for i in range(liczba_sesji):
        for j in range(i + 1, liczba_sesji):
            if random.random() < szansa_na_konflikt:
                konflikty.append((sesje[i]["nazwa"], sesje[j]["nazwa"]))
                sesje[i]["ilosc_konfliktow"] += 1
                sesje[j]["ilosc_konfliktow"] += 1

    return sesje, konflikty,sale

# a=open("dane_konferencji.txt", "w")
# sesje, konflikty, sale = generuj_dane_konferencji(liczba_sesji=23, szansa_na_konflikt=0.1, mindlugosc=30, maxdlugosc=90, ilosc_sali=3)
# a.write(str(sesje)+"\n")
# a.write(str(konflikty)+"\n")
# a.write(str(sale)+"\n")
# a.close()

# Wypisanie wyniku w postaci zwykłego tekstu
# print("--- DANE WEJŚCIOWE KONFERENCJI ---")
# print(f"Liczba sesji: {len(sesje)}")
# print(f"Lista sesji: {', '.join(x['nazwa'] for x in sesje)}")
# print(f"czas trwania sesji: {', '.join(str(x['dlugosc']) for x in sesje)}")
# print(f"Rozmiar sesji: {', '.join(str(x['rozmiar']) for x in sesje)}")
# print(f"rozmiary sali: {', '.join(str(x['rozmiar']) for x in sale)}")
# print(f"Liczba konfliktów: {len(konflikty)}")
# print(konflikty[0][0])