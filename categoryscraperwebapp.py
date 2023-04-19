from flask import Flask, render_template, request
from requests import get
from json import loads
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home/index.html')

@app.route('/', methods=['POST'])
def submit_form():
    try:
        url = request.form['url']
        range_value = int(request.form['range'])

        pageCount = 1
        product_list = []

        if ('q=') in url:
            keywords = url.split('q=')[-1].split("&qt")[0]
            data_url = f'https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/sr?q={keywords}&pi={pageCount}'
        else:
            keyword = url.split("com/")[-1].split("?")[0]
            data_url = f'https://public.trendyol.com/discovery-web-searchgw-service/v2/api/infinite-scroll/{keyword}?pi={pageCount}'

        while True:
            if len(product_list) >= range_value and range_value != 0 or pageCount > 208:
                break
            data = loads(get(data_url).text)
            product_list.extend(data["result"]["products"])

            if len(data["result"]['products']) == 24:
                pageCount += 1
            else:
                break

        product_list = product_list[:range_value] if range_value > 0 else product_list

        product_name = [name["name"] for name in product_list]
        product_link = [link["url"] for link in product_list]
        product_img = [img["images"] for img in product_list]
        product_price = [str(price["price"]["sellingPrice"]) + " TL" for price in product_list]

        product_data = []

        for i in range(len(product_name)):
            product_data.append([product_name[i], "https://trendyol.com"+product_link[i], "https://cdn.dsmcdn.com"+product_img[i][0], product_price[i]])

        df = pd.DataFrame(product_data, columns=(["Urun İsmi", "Urun Linki", "Urun Resmi", "Urun Fiyatı"]))
        df.to_excel("urunler.xlsx", sheet_name="urun", index=False)
        return render_template('result.html', products=product_data)

    except:
        return render_template('home/index.html', error='Islem basarisiz oldu url\'yi kontrol ediniz.')

if __name__ == '__main__':
    app.run(debug=True)
