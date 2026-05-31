import generator_danych
import plotly.express as px
import pandas as pd
import datetime
def harmonogram(sesje, konflikty, sale,przerwy):
    sesje.sort(reverse=True,key=lambda x: (x['rozmiar'],x['ilosc_konfliktow'], x['dlugosc']))
    sale.sort(reverse=True,key=lambda x: x['rozmiar'])
    sesje_wykres=[]
    for i in range(len(sesje)):
        print(sesje[i]["nazwa"],sesje[i]["ilosc_konfliktow"],sesje[i]["rozmiar"])
        wpisane = False
        for j in range(len(sale)):
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
                            for l3 in range(k+sesje[i]["dlugosc"]//15,k+(sesje[i]["dlugosc"]+przerwy)//15):
                                    if l3<32:
                                        sale[j]["harmonogram"][l3] = "przerwa"
                            sesje_wykres.append(dict(Nazwa=sesje[i]["nazwa"],
                                                    Sala=sale[j]["nazwa"], 
                                                    Start= datetime.datetime(2025, 5, 31, 9, 0)+ datetime.timedelta(minutes=k*15), 
                                                    Koniec= datetime.datetime(2025, 5, 31, 9, 0)+ datetime.timedelta(minutes=(k+sesje[i]["dlugosc"]//15)*15)))
                            wpisane = True
                            break
            if wpisane==True:
                break
        if wpisane==False:
            print("nie można wpisać sesji ",sesje[i]["nazwa"],sesje[i]["ilosc_konfliktow"]," do żadnej sali")    
    df = pd.DataFrame(sesje_wykres)
    wykres=px.timeline(
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
    wykres.show()
    print(sale[0]["harmonogram"],sale[0]["rozmiar"])
    print("\n")
    print(sale[1]["harmonogram"],sale[1]["rozmiar"])
    print("\n")
    print(sale[2]["harmonogram"],sale[2]["rozmiar"])
sesje, konflikty,sale = generator_danych.generuj_dane_konferencji(liczba_sesji=20, szansa_na_konflikt=0.2, mindlugosc=30, maxdlugosc=90, ilosc_sali=3)
harmonogram(sesje, konflikty, sale, przerwy=15)