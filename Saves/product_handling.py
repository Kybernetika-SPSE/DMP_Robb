import requests
from datetime import date,datetime
import mysql.connector as database

conn = database.connect(host="localhost",
                        user="root",
                        passwd="AhOj159/*@",
                        database="food_schem",
                        )

cursor = conn.cursor()
if cursor:
    print("Connected to MySQL Server")

barcode = 20093358
exp_date = [date(2025, 1, 29), date(2025, 1, 28)]
product_array = [barcode, exp_date]

def upload_product_to_database(product_array):
    # JSON soubor z url stranky
    sql_brcd = str(product_array[0])
    sql = """SELECT expiration_date FROM client_food_table WHERE barcode = %s """
    cursor.execute(sql,(sql_brcd,))
    result = cursor.fetchall()

    if len(result)>0:
        #uz tam je produkt takze staci k nemu jen ulozit dalsi data expirace

        #upravení stringu, ktery byl ziskan z databaze tak aby se dal upravit na date()
        expiration_date = ''
        for date in result:
            print(f"date: {date}")
            date_sepparated_array = date[0].split(",")

            #odstraneni mezer a
            for date in date_sepparated_array:
                date = date.replace(" ","")

                if date == ",":
                    pass
                else:
                    expiration_date += date + ", "

        # upraveni stringu kvuli zbytkovym znakum na konci
        expiration_date = expiration_date[:-3]
        old_dates = expiration_date.split(",")
        old_dates.pop(len(old_dates) - 1)

        # print(f"expiration_date {expiration_date}")
        # print(f"old_dates {old_dates}")
        # pridani nových expiracnich dat

        expiration_date = []
        for date in old_dates:
            date = date.replace(" ","")
            expiration_date.append(datetime.strptime(date, "%Y-%m-%d").date())

        for date in product_array[1]:
            expiration_date.append(date)

        expiration_date = sorted(expiration_date)
        print(f"expiration_date {expiration_date}")
        final_expiration_date = ''
        for date in expiration_date:
            formatted_expiration_date = date.strftime('%Y-%m-%d')
            final_expiration_date += formatted_expiration_date + ', '
        print(f"final_expiration_date: {final_expiration_date}")

        #pridani vsech expiracnich dat do database k prislusnemu produktu
        sql = """UPDATE client_food_table SET expiration_date = %s WHERE barcode = %s """
        val = (final_expiration_date,sql_brcd)
        cursor.execute(sql, val)
        conn.commit()

    else:
        url = f"https://world.openfoodfacts.org/api/v2/product/{product_array[0]}.json"
        response = requests.get(url)
        api_json_file = response.json()
        product_api_data = api_json_file.get('product', 'Unknown')

        # pro hledani v databazi
        keywords = product_api_data.get('_keywords', 'Unknown')

        # info o produktech
        product_name = product_api_data.get('product_name', 'Unknown')
        product_brand = product_api_data.get('brands', 'Unknown')
        quantity = product_api_data.get('quantity', 'Unknown')
        small_image_url = product_api_data.get('image_front_thumb_url', 'Unknown')

        # filtrovani/kategorie
        category_tags = product_api_data.get('categories_tags', 'Unknown')

        category_tags_str = ', '.join([tag.split(":")[1] for tag in category_tags])
        keywords_str = ', '.join(keywords)

        #prevedeni data na string pro odeslani do MYSQL databaze
        expiration_date = ''
        for date in sorted(product_array[1]):
            # udrzeni normovaneho formatu data
            formatted_expiration_date = date.strftime('%Y-%m-%d')
            # pridani do str
            expiration_date += formatted_expiration_date + ', '

        # MYSQL query
        sql = """INSERT INTO client_food_table (name, brand, quantity, small_image_url, category_tags, keywords, expiration_date, barcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        val = (product_name, product_brand, quantity, small_image_url, category_tags_str, keywords_str, expiration_date, sql_brcd)
        cursor.execute(sql, val)
        conn.commit()

#spusteni funkce
upload_product_to_database(product_array)