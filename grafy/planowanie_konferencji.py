from tkinter import ttk
from tkinter import filedialog
import generator_danych
import plotly.express as px
import pandas as pd
import datetime
import tkinter as tk
from PIL import Image, ImageTk
import os
import logging
import sys
import traceback

# Configure logging to stdout for easy console debugging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# Deklaracja zmiennych globalnych
etykieta_z_wykresem = None
etykieta_niewpisane = None
status_label = None
flaga = 0
selected_file_path = ""

def set_status_message(message: str = "", error: bool = True):
    global status_label
    if status_label is None:
        return
    status_label.configure(text=message, fg="red" if error else "green")


def harmonogram(sesje, konflikty, sale, przerwy):
    sesje.sort(reverse=True, key=lambda x: (x['rozmiar'], x['ilosc_konfliktow'], x['dlugosc']))
    sale.sort(reverse=True, key=lambda x: x['rozmiar'])
    sesje_wykres = []
    niewpisane_sesje = []
    
    for i in range(len(sesje)):
        print(sesje[i]["nazwa"], sesje[i]["ilosc_konfliktow"], sesje[i]["rozmiar"])
        wpisane = False
        for j in range(len(sale)):
            if sale[j]["rozmiar"] >= sesje[i]["rozmiar"]:
                for k in range(32):
                    if sale[j]["harmonogram"][k] is None:
                        if k + sesje[i]["dlugosc"] // 15 <= 32:
                            conflict_found = False
                            for l1 in range(k, k + sesje[i]["dlugosc"] // 15):
                                scheduled_name = sale[j]["harmonogram"][l1]
                                if scheduled_name is None:
                                    continue
                                for konflikt in konflikty:
                                    if (konflikt[0] == sesje[i]["nazwa"] and konflikt[1] == scheduled_name) or \
                                       (konflikt[1] == sesje[i]["nazwa"] and konflikt[0] == scheduled_name):
                                        conflict_found = True
                                        break
                                if conflict_found:
                                    break
                            if conflict_found:
                                continue
                            for l2 in range(k, k + sesje[i]["dlugosc"] // 15):
                                sale[j]["harmonogram"][l2] = sesje[i]["nazwa"]
                            for l3 in range(k + sesje[i]["dlugosc"] // 15, k + (sesje[i]["dlugosc"] + przerwy) // 15):
                                if l3 < 32:
                                    sale[j]["harmonogram"][l3] = "przerwa"
                            sesje_wykres.append(dict(
                                Nazwa=sesje[i]["nazwa"],
                                Sala=sale[j]["nazwa"], 
                                Start=datetime.datetime(2025, 5, 31, 9, 0) + datetime.timedelta(minutes=k * 15), 
                                Koniec=datetime.datetime(2025, 5, 31, 9, 0) + datetime.timedelta(minutes=(k + sesje[i]["dlugosc"] // 15) * 15)
                            ))
                            wpisane = True
                            break
            if wpisane == True:
                break
        if wpisane == False:
            niewpisane_sesje.append(sesje[i]["nazwa"])
            
    df = pd.DataFrame(sesje_wykres)
    wykres = px.timeline(
        df,
        x_start="Start",
        x_end="Koniec",
        y="Sala",
        color="Nazwa",
        text="Nazwa",
        title="Harmonogram konferencji"
    )
    wykres.update_yaxes(autorange="reversed")
    wykres.update_xaxes(
        tickformat="%H:%M",
        dtick=1800000
    )
    wykres.update_traces(textposition='inside', insidetextanchor='middle')
    # Zapis wykresu do pliku
    wykres.write_image("tymczasowy_harmonogram.png", width=1200, height=600)
    
    return niewpisane_sesje


def wybierz_plik():
    global selected_file_path
    selected_file_path = filedialog.askopenfilename(
        title="Wybierz plik danych",
        filetypes=[("Plik tekstowy", "*.txt"), ("Wszystkie pliki", "*")]
    )
    if selected_file_path:
        entry8.configure(state='normal')
        entry8.delete(0, tk.END)
        entry8.insert(0, selected_file_path)
        entry8.configure(state='readonly')


def pokaz_harmonogram(niewpisane_sesje):
    global etykieta_z_wykresem, etykieta_niewpisane
    
    # Ukrywamy formularz
    label2.pack_forget()
    form_frame.pack_forget()
    button.pack_forget()
    label8.pack_forget()
    plik_frame.pack_forget()
    
    # Wczytujemy świeżo wygenerowany obraz
    try:
        obraz = Image.open("tymczasowy_harmonogram.png")
        zdjecie = ImageTk.PhotoImage(obraz)
    except Exception:
        return

    # Aktualizacja lub stworzenie etykiety z wykresem
    if etykieta_z_wykresem is None:
        etykieta_z_wykresem = tk.Label(root, image=zdjecie)
    etykieta_z_wykresem.configure(image=zdjecie)
    etykieta_z_wykresem.image = zdjecie
    etykieta_z_wykresem.pack(pady=20)
    
    # Obsługa komunikatu o niewpisanych sesjach
    if len(niewpisane_sesje) > 0:
        tekst_odrzuconych = "Nie udało się przypisać do żadnej sali:\n" + "\n".join(niewpisane_sesje)
        kolor_tekstu = "red"

    if etykieta_niewpisane is None:
        etykieta_niewpisane = tk.Label(root, text=tekst_odrzuconych, font=("Arial", 12, "bold"), fg=kolor_tekstu, bg="#f4f4f4")
    else:
        etykieta_niewpisane.configure(text=tekst_odrzuconych, fg=kolor_tekstu)
    etykieta_niewpisane.pack(pady=5)


def sterownik_przycisku(a, b, c, d, e): 
    global flaga, sesje, konflikty, sale
    try:
        if flaga == 0:
            sesje, konflikty, sale = generator_danych.generuj_dane_konferencji(a, b, c, d, e)
        niewpisane_sesje = harmonogram(sesje, konflikty, sale, przerwy=15)
        pokaz_harmonogram(niewpisane_sesje)
    except Exception:
        logging.exception("Błąd podczas generowania harmonogramu")

def pobranie_danych():
    global flaga, sesje, konflikty, sale, selected_file_path
    set_status_message("")
    if selected_file_path:
        if os.path.isfile(selected_file_path):
            try:
                with open(selected_file_path, 'r') as plik:
                    linie = plik.readlines()
                    sesje = eval(linie[0].strip())
                    konflikty = eval(linie[1].strip())
                    sale = eval(linie[2].strip())
                    flaga = 1
            except Exception as ex:
                logging.exception("Błąd podczas wczytywania pliku danych")
                set_status_message("Błąd odczytu pliku danych. Sprawdź konsolę.")
                return
        else:
            logging.error("Podana ścieżka pliku nie istnieje: %s", selected_file_path)
            set_status_message("Plik nie istnieje lub został usunięty.")
            return

        try:
            sterownik_przycisku(0, 0, 0, 0, 0)
            set_status_message("", False)
        except Exception:
            logging.exception("Błąd podczas uruchamiania harmonogramu z pliku")
            set_status_message("Wystąpił błąd podczas uruchamiania harmonogramu z pliku.")
        return

    try:
        a = int(entry3.get())
        b = float(entry4.get())
        c = int(entry5.get())
        d = int(entry6.get())
        e = int(entry7.get())
        if not (0 <= b <= 1):
            set_status_message("Szansa na konflikt musi być liczbą z przedziału 0-1.")
            return
        sterownik_przycisku(a, b, c, d, e)
        set_status_message("", False)
    except ValueError as ex:
        logging.exception("Błąd konwersji parametrów wejściowych")
        set_status_message("Proszę wprowadzić poprawne wartości numeryczne.")

# Konfiguracja okna głównego Tkinter
root = tk.Tk()
root.title("Generator Harmonogramu Konferencji")
root.geometry("1280x1000")
root.configure(bg="#f4f4f4")

style = ttk.Style()
if 'clam' in style.theme_names():
    style.theme_use('clam')

style.configure("TButton", font=("Arial", 14, "bold"), padding=10)

# Budowa widoku wprowadzania danych
label = tk.Label(root, text="Generator Harmonogramu Konferencji", font=("Arial", 20, "bold"), bg="#f4f4f4")
label.pack(side="top", pady=(30, 10))

label2 = tk.Label(root, text="Podaj parametry konferencji:", font=("Arial", 16), bg="#f4f4f4")
label2.pack(side="top", pady=(0, 20))

form_frame = tk.Frame(root, bg="#f4f4f4")
form_frame.pack(side="top")

font_label = ("Arial", 12)
font_entry = ("Arial", 12)

label3 = tk.Label(form_frame, text="Liczba sesji:", font=font_label, bg="#f4f4f4")
label3.grid(row=0, column=0, sticky="e", padx=10, pady=10)
entry3 = ttk.Entry(form_frame, font=font_entry, width=20)
entry3.grid(row=0, column=1, sticky="w", padx=10, pady=10)

label4 = tk.Label(form_frame, text="Szansa na konflikt (0-1):", font=font_label, bg="#f4f4f4")
label4.grid(row=1, column=0, sticky="e", padx=10, pady=10)
entry4 = ttk.Entry(form_frame, font=font_entry, width=20)
entry4.grid(row=1, column=1, sticky="w", padx=10, pady=10)

label5 = tk.Label(form_frame, text="Minimalna długość (min):", font=font_label, bg="#f4f4f4")
label5.grid(row=2, column=0, sticky="e", padx=10, pady=10)
entry5 = ttk.Entry(form_frame, font=font_entry, width=20)
entry5.grid(row=2, column=1, sticky="w", padx=10, pady=10)

label6 = tk.Label(form_frame, text="Maksymalna długość (min):", font=font_label, bg="#f4f4f4")
label6.grid(row=3, column=0, sticky="e", padx=10, pady=10)
entry6 = ttk.Entry(form_frame, font=font_entry, width=20)
entry6.grid(row=3, column=1, sticky="w", padx=10, pady=10)

label7 = tk.Label(form_frame, text="Liczba sali:", font=font_label, bg="#f4f4f4")
label7.grid(row=4, column=0, sticky="e", padx=10, pady=10)
entry7 = ttk.Entry(form_frame, font=font_entry, width=20)
entry7.grid(row=4, column=1, sticky="w", padx=10, pady=10)

button = ttk.Button(root, text="Generuj Harmonogram", command=pobranie_danych)
button.pack(side="top", pady=40)

label8 = tk.Label(root, text="Wybierz plik danych:", font=font_label, bg="#f4f4f4")
label8.pack(side="top", pady=(0, 5))

plik_frame = tk.Frame(root, bg="#f4f4f4")
plik_frame.pack(side="top", pady=(0, 20))

entry8 = ttk.Entry(plik_frame, font=font_entry, width=40, state='readonly')
entry8.grid(row=0, column=0, sticky="w")

file_button = ttk.Button(plik_frame, text="Wybierz plik...", command=wybierz_plik)
file_button.grid(row=0, column=1, sticky="w", padx=10)

status_label = tk.Label(root, text="", font=("Arial", 12), fg="red", bg="#f4f4f4")
status_label.pack(side="top", pady=(0, 10))
# Uruchomienie aplikacji
root.mainloop()