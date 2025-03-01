# -*- coding: utf-8 -*-
"""online retail analysis with EDA

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1SWCPMNqh7GWSxAjoiqRwStoMufdY7mBP
"""

!pip install openpyxl

import pandas as pd
from matplotlib import pyplot as plt

!unzip /content/online+retail.zip



df1=pd.read_excel('Online Retail.xlsx',dtype={'InvoiceNo':'string','StockCode':'string','Description':'string','InvoiceNo':'string','Country':'string'})

df1.head(10)

#for detailed info
df1.info()

#### data cleaning and missing value###
df1.isnull().sum()
# gives count of null values with column
#description have 1454 records as empty

df1[df1.Description.isnull()]
# gives only null values

#check the description of stockcode=22139 with other records and may be the most occuring result is the description
#IF DESCRIPTION IS NULL THEN LOOK AT OTHER RECORDS WITH SAME STOCK CODE WHICH EVER THE DESCREIPTION OCCURS FREQUENTLY OCCURED THEN CONSIDER IT
df1[df1.StockCode=='22139']

#TO FIND MOST FREQUENTLY OCCURED RECORD USE MODE() AS IT HELPS TO RETRIEVE THE EXACT RECORD
df1[df1.StockCode=='22139'].Description.mode()

#valuecounts gives count of total occurance of that description in the dataset
most_freq=df1[["StockCode","Description"]].value_counts().reset_index()
most_freq

most_freq.columns = ["StockCode", "freqDescription", "count"]
most_freq

most_freq = most_freq.groupby("StockCode").first().reset_index()

df2 = df1.merge(most_freq, on="StockCode", how="left")
df2

df2.isnull().sum()

df2['Description']=df2['freqDescription']
df2

df2.isnull().sum()

#now drop the records if the value is "NA"
df2.dropna(subset=['Description'],inplace=True)
df2.isnull().sum()

df2.shape

#now drop unwanted columns i.e freqdescription,count
df2.drop(columns=['freqDescription','count'],inplace=True)
df2

df2.describe()

df2[df2.Quantity<0]

df2[df2.UnitPrice<0]

#now remove quantity<0 and unitprice<0 from the dataset
#solution
df3=df2[(df2.Quantity>0) & (df2.UnitPrice>0)]
df3.describe()

df3.Quantity.quantile(0.9999)

#feature engineering to add new columns
# in the dataset we have quantity and unitprice so we can solve saleamount
copy=df3.copy()

copy['TotalSales'] = copy['Quantity'] * copy['UnitPrice']
copy

# Extract the month
copy['Month'] = copy['InvoiceDate'].dt.month
copy

"""#visualizattion and EDA
###1.plot monthly sales
"""

monthlysales=copy.groupby('Month')['TotalSales'].sum()
monthlysales.plot(kind='bar',title='Monthly Sales')
plt.xlabel('Month')
plt.ylabel('Total Sales')
plt.show()

monthlysales = copy.groupby('Month')['TotalSales'].sum()
monthlysales.plot(kind='line', title='Monthly Sales') # Changed to line plot
plt.xlabel('Month')
plt.ylabel('Total Sales')
plt.grid(True)
plt.show()

"""#insights
#####total sales rising up from august and having a peek in november.most likely due to holiday season at end of year.

##Top 5 countries by sales
"""

top_5_countries = copy.groupby('Country')['TotalSales'].sum().nlargest(5)
top_5_countries.plot(kind='bar', title='Top 5 Countries by Sales')
plt.xlabel('Country')
plt.ylabel('Total Sales')

plt.show()

top_5_countries = copy.groupby('Country')['TotalSales'].sum().nlargest(5)
top_5_countries

top_5_countries = copy.groupby('Country')['TotalSales'].sum().nlargest(5)

plt.figure(figsize=(10, 6))
plt.bar(top_5_countries.index, top_5_countries.values, color='skyblue')
plt.title('Top 5 Countries by Total Sales', fontsize=16)
plt.xlabel('Country', fontsize=12)
plt.ylabel('Total Sales', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(fontsize=10)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt
total_sales = top_5_countries.sum()
percentages = (top_5_countries / total_sales) * 100
plt.figure(figsize=(10, 6))
bars = plt.barh(percentages.index, percentages.values, color='skyblue')
for bar, percentage in zip(bars, percentages):
    plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{percentage:.1f}%', va='center')

plt.title('Top 5 Countries by Total Sales Percentage', fontsize=16)
plt.xlabel('Percentage of Total Sales', fontsize=12)
plt.ylabel('Country', fontsize=12)
plt.xlim(0, percentages.max() * 1.1)
plt.tight_layout()
plt.show()

top_products = copy.groupby('StockCode')['TotalSales'].sum().nlargest(5)
total_sales = top_products.sum()
percentages = (top_products / total_sales) * 100

plt.figure(figsize=(10, 6))
bars = plt.barh(percentages.index, percentages.values, color='skyblue')

for bar, percentage in zip(bars, percentages):
    plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2, f'{percentage:.1f}%', va='center')

plt.title('Top 5 Products by Total Sales Percentage', fontsize=16)
plt.xlabel('Percentage of Total Sales', fontsize=12)
plt.ylabel('StockCode', fontsize=12)
plt.xlim(0, percentages.max() * 1.1)
plt.tight_layout()
plt.show()



"""4.RFM ANALYSIS"""

current_dt =copy['InvoiceDate'].max()+pd.DateOffset(days=1)
current_dt

rfm=copy.groupby("CustomerID").agg({
    "InvoiceDate": lambda date: (current_dt - date.max()).days,
    "InvoiceNo": "count",
    "TotalSales": "sum"
})
rfm.columns = ['Recency','frequency','monetary']
rfm

copy[copy.CustomerID==12349]
#for the customerid=12349 the recent transaction was 19days ago

copy[copy.CustomerID==12349]["TotalSales"].sum()

rfm['r_quartile'] = pd.qcut(rfm['Recency'], 4, [4,3,2,1])
rfm['f_quartile'] = pd.qcut(rfm['frequency'], 4, [1,2,3,4])
rfm['m_quartile'] = pd.qcut(rfm['monetary'], 4, [1,2,3,4])
rfm['RFM_Score'] = rfm[['r_quartile','f_quartile','m_quartile']].sum(axis=1)
rfm

rfm.sort_values(by='RFM_Score',ascending=False)
# rfm score is high when recent,frequency,monetary of the customer is valuable for the company in terms of sales