#ONUR YAMAN - HAVELSAN STAJ PROJE
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import seaborn as sns


desired_width=1000

pd.set_option('display.width', desired_width)

np.set_printoptions(linewidth=desired_width)

pd.set_option('display.max_columns',10)
###########################################################################################################
#df=pd.read_csv(r"C:\Users\onury\Desktop\covid_19_data.csv")
#print(df.head())
#for col in df.columns: # column nameleri görmek için
    #print(col)
#dfturkey=df[df['Country/Region']=='Turkey']
#print(dfturkey.head())
#dfturkey1=dfturkey['Confirmed'].unique()
#print(dfturkey1)
#print(type(dfturkey1))
#print(dfturkey1.size)
#x=np.linspace(0,124,124)
#y=dfturkey1
################################################################################################################


from evds import evdsAPI
evds = evdsAPI('Lfg3X7Ci8L')
#print(evds.main_categories)
#print(evds.get_sub_categories('FİNANSAL İSTATİSTİKLER'))
c=evds.get_sub_categories('FİNANSAL İSTATİSTİKLER')
d=evds.get_series('bie_kkhartut')
#print(d.head())
e=evds.get_data(['TP.KKHARTUT.KT1'],startdate="10-03-2020", enddate="17-07-2020")
print(e.head())
#print(e.shape[0])
x=np.linspace(0,78,79)
#print(x)
e1=e['TP_KKHARTUT_KT1'] #kredi kartı datası
print(e.dtypes)

####################################################################################################
cvd=pd.read_csv('https://covid.ourworldindata.org/data/ecdc/full_data.csv') #COVİDDATAÇEKME
cvd=cvd[cvd['location']=='Turkey']

cvd=cvd.reset_index(drop=True)
cvd['date'] = pd.to_datetime(cvd['date'])

#print(e.tail())
#COVID VE HARCAMA DATASIYLA DATAFRAME OLUŞTURMA
mask = (cvd['date'] >= '2020-03-13') & (cvd['date'] <= '2020-07-17')
cvd = cvd.loc[mask]

cvd.dropna(subset=['weekly_cases'],axis=0)
print(cvd.head())
i=6
week=[]
while i<125:
    a=cvd.loc[i,'weekly_cases']
    week.append(a)
    #print(a)

    i=i+7
b=cvd.loc[125,'weekly_cases']
week.append(b)
week.insert(0,0)
#print(week)
e['weekly']=week
e=e.drop(columns='YEARWEEK')
e.columns=['Tarih','Total','Haftalık']
print(e.head())



# BASIC ANALYSIS OF DATA
print("İstatistiksel Özet:")
print(e.describe()) #STATISTICAL SUMMARY
print("Korelasyon Değeri:")
print(e["Total"].corr(e["Haftalık"].shift(-1), method = 'pearson',min_periods=1))

#correlation between haftalık vaka and total harcama, 1 hafta offset verilmiş şekilde.
corr=e['Haftalık'].corr(e['Total'])





fig,ax=plt.subplots()
ax.plot(e['Tarih'],e['Total'],color='green' ,marker="o",label='Harcama')
ax.set_xlabel("Tarih")
ax.set_ylabel("TotalHarcama (x10 milyar tl)")
plt.xticks(rotation=45)

ax2=ax.twinx()
ax2.plot(e['Tarih'], e['Haftalık'],color="blue",marker="o",label='Haftalık Vaka')
ax2.set_ylabel("Haftalık Vaka Sayısı",color="blue",fontsize=14)
ax.legend()
ax2.legend()
ax.set_title('Haftalık Türkiye Geneli Banka- Kredi Kartı Harcama vs Haftalık COVID-19 VAKA SAYILARI ')
plt.show()
fig.savefig('stajgrafik.jpg',
            format='jpeg',
            dpi=100,
            bbox_inches='tight')




data=e.pivot_table(index='Tarih',columns='Haftalık',values='Total')
sns.heatmap(data)
plt.show()
#e['Tarih']=pd.to_datetime(e['Tarih'],format='%d-%m-%Y')
#sns.lmplot(x='Tarih',y='Total',data=e)

ax=sns.regplot(data = e.reset_index(), x = 'index', y = 'Haftalık',color='b',marker='o')
ax.set(xlabel='Hafta',ylabel='Haftalık Vaka Sayısı')
ax.set(ylim=(0,40000))
ax.set(xlim=(0,19))
ax.set_title('Vaka Sayıları Regresyon Modeli')
plt.show()
ax3=sns.regplot(data = e.reset_index(), x = 'index', y = 'Total',color='g')
ax3.set(xlabel='Hafta',ylabel='Haftalık Harcama*10 Milyar TL')
ax3.set_title('Harcama Miktarı Regresyon Modeli')
plt.show()

######################################## EXPORTING AND IMPORTING TO DATABASE




from pandas import DataFrame
import sqlite3
conn = sqlite3.connect('evdsveri.db')
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS STAJ4 (Tarih DATE ,Total number,Haftalık number)')
conn.commit()
e.to_sql('STAJ4', conn, if_exists='replace', index = False)
c.execute('''  
SELECT * FROM STAJ4
          ''')



print("Maksimum harcama miktarı :")
c.execute('''
     SELECT Tarih,max(Total),Haftalık FROM STAJ4
''')
a=DataFrame(c.fetchall(),columns=['Tarih','Total','Haftalık'])
print(a)

print("Maksimum haftalık vaka sayısı:")
c.execute('''
     SELECT Tarih,Total,max(Haftalık) FROM STAJ4
''')
b=DataFrame(c.fetchall(),columns=['Tarih','Total','Haftalık'])
print(b)
conn.close()
