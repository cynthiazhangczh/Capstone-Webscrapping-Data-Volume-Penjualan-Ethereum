from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.coingecko.com/en/coins/ethereum/historical_data/usd?start_date=2020-01-01&end_date=2021-06-30#panel')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table',attrs={'class': 'table table-striped text-sm text-lg-normal'})
test = table.find_all('tr',attrs={'class': ''})

row_length = len(test)

temp = [] #initiating a list 

for i in range(1, row_length):
#insert the scrapping process here
    
    #get date
    date = test[i].th.text
    #get market cap
    market_cap = test[i].find_all('td', attrs={'class':'text-center'})[0].text
    market_cap = market_cap.strip('\n')
    
    #get volume
    volume = test[i].find_all('td', attrs={'class':'text-center'})[1].text
    volume = volume.strip('\n')
    
    #get open price
    open_price = test[i].find_all('td', attrs={'class':'text-center'})[2].text
    open_price = open_price.strip('\n')
    
    #get close price
    close_price = test[i].find_all('td', attrs={'class':'text-center'})[3].text
    close_price = close_price.strip('\n')
    temp.append((date,market_cap,volume,open_price,close_price))
    
temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns=('date','market_cap','volume','open_price', 'close_price'))
df = df[['date','volume']]

#insert data wrangling here
df['date'] = pd.to_datetime(df['date'])
df['volume'] = df['volume'].str.replace("$","",regex=False)
df['volume'] = df['volume'].str.replace(",","")
df['volume'] = df['volume'].astype('int64')
df = df.set_index('date')
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{round(df["volume"].mean(),1)}' #be careful with the " and ' 

	# generate plot
	ax = df.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)