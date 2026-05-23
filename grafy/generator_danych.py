import random

def generuj_dane_konferencji(liczba_sesji, szansa_na_konflikt,mindlugosc,maxdlugosc,ilosc_sali=3):
    """
    Generuje losowe dane wejściowe dla problemu planowania konferencji.
    Zwraca listę sesji oraz listę krotek reprezentujących konflikty.
    """
    sesje = []
    konflikty = []
    sale=[]
    for i in range(ilosc_sali):
        sala={
            "nazwa": f"Sala{i+1}",
            "rozmiar": random.randint(1, 3) * 50,
            "harmonogram": [None] * 32
        }
        sale.append(sala)
    for i in range(liczba_sesji):
        sesja = {
            "nazwa": f"S{i+1}",
            "dlugosc": random.randint(int(mindlugosc/15), int(maxdlugosc/15)) * 15,
            "rozmiar": random.randint(1, 3) * 50,
            "ilosc_konfliktow": 0
        }
        sesje.append(sesja)
    for i in range(liczba_sesji):
        for j in range(i + 1, liczba_sesji):
            if random.random() < szansa_na_konflikt:
                konflikty.append((sesje[i], sesje[j]))
                sesje[i]["ilosc_konfliktow"] += 1
                sesje[j]["ilosc_konfliktow"] += 1

    return sesje, konflikty,sale


sesje, konflikty,sale = generuj_dane_konferencji(liczba_sesji=8, szansa_na_konflikt=0.3, mindlugosc=15, maxdlugosc=120, ilosc_sali=3)

# Wypisanie wyniku w postaci zwykłego tekstu
print("--- DANE WEJŚCIOWE KONFERENCJI ---")
print(f"Liczba sesji: {len(sesje)}")
print(f"Lista sesji: {', '.join(x['nazwa'] for x in sesje)}")
print(f"czas trwania sesji: {', '.join(str(x['dlugosc']) for x in sesje)}")
print(f"Rozmiar sali: {', '.join(str(x['rozmiar']) for x in sesje)}")
print(f"rozmiary sali: {', '.join(str(x['rozmiar']) for x in sale)}")
print(f"Liczba konfliktów: {len(konflikty)}")