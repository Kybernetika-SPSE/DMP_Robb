import requests
from datetime import date,datetime
import mysql.connector as database
from kivy.clock import Clock
import json

with open("dtb_config.json","r") as config_file:
    config = json.load(config_file)
conn = database.connect(**config)

cursor = conn.cursor()

#if cursor:
#    print("Connected to MySQL Server")

#testvaci hodnoty
#barcode = 20093358
#exp_date = [date(2025, 2, 5), date(2025, 2, 6)]
#product_array = [barcode, exp_date]

def execute_mysql_querry(mysql_query):
    conn.reconnect()
    cursor.execute(mysql_query)
    result = cursor.fetchall()
    conn.commit()
    return result

def update_mysql_dtb(mysql_query, values):
    conn.reconnect()
    cursor.execute(mysql_query,values)
    conn.commit()

def get_prod_mysql_dtb(mysql_query, values):
    conn.reconnect()
    cursor.execute(mysql_query, values)
    result = cursor.fetchall()
    return result

def upload_product_to_database(product_array, refresh_function):
    #pullovani JSON soubor z url stranky
    sql_brcd = str(product_array[0])
    #sql = """SELECT expiration_date FROM client_food_table WHERE barcode = %s """
    #cursor.execute(sql,(sql_brcd,))
    #result = cursor.fetchall()

    result = get_prod_mysql_dtb("SELECT expiration_date FROM client_food_table WHERE barcode = %s ",(sql_brcd,))

    final_expiration_date = ""
    if len(result)>0:
        #produkt jiz v databazi je a tak staci jen k jeho zaznamu pridat nove nahrane data expirace
        #upravení stringu, ktery byl ziskan z databaze tak aby se dal upravit na date()

        expiration_date = ""
        for date in result:
            date_sepparated_array = date[0].split(",")
            #odstraneni mezer a prebytecnych znaku
            for date in date_sepparated_array:
                date = date.replace(" ","")
                if date == ",":
                    pass
                else:
                    expiration_date += date + ", "

        #upraveni stringu kvuli zbytkovym znakum na konci
        expiration_date = expiration_date[:-3]
        old_dates = expiration_date.split(",")
        old_dates.pop(len(old_dates) - 1)

        #pridani nových expiracnich dat
        expiration_date = []

        #odstraneni prebytecnich znaku a mezer
        for date in old_dates:
            date = date.replace(" ","")
            #prevedeni dat na date format a pridani do pole exp. dat (priprava pro pridani exp. dat z databaze)
            expiration_date.append(datetime.strptime(date, "%Y-%m-%d").date())

        #pridani exp. dat z databaze
        for date in product_array[1]:
            expiration_date.append(date)

        #serazeni exp. dat vzestupne
        expiration_date = sorted(expiration_date)

        #prevedeni vsech dat na string
        for date in expiration_date:
            formatted_expiration_date = date.strftime('%Y-%m-%d')
            final_expiration_date += formatted_expiration_date + ', '

        #pridani vsech expiracnich dat do database k prislusnemu produktu
        update_mysql_dtb("UPDATE client_food_table SET expiration_date = %s WHERE barcode = %s ",(final_expiration_date, sql_brcd))
        #sql = """UPDATE client_food_table SET expiration_date = %s WHERE barcode = %s """
        #val = (final_expiration_date,sql_brcd)
        #cursor.execute(sql, val)
        #conn.commit()

        #uzavreni pripojeni databaze kvuli spravne aktualizaci databaze
        conn.close()
        #obnoveni aplikace
        Clock.schedule_once(refresh_function,0.1)

    else:
        #produkt jeste nema zaznam v databazi
        url = f"https://world.openfoodfacts.org/api/v2/product/{product_array[0]}.json"
        response = requests.get(url)
        api_json_file = response.json()
        product_api_data = api_json_file.get('product', 'Unknown')

        #pro hledani v databazi
        keywords = product_api_data.get('_keywords', 'Unknown')

        #info o produktech
        product_name = product_api_data.get('product_name', 'Unknown')
        product_brand = product_api_data.get('brands', 'Unknown')
        quantity = product_api_data.get('quantity', 'Unknown')
        small_image_url = product_api_data.get('image_front_thumb_url', 'Unknown')

        #filtrovani/kategorie
        category_tags = product_api_data.get('categories_tags', 'Unknown')

        #if product_name != 'Unknown' or category_tags != 'Unknown' or keywords != 'Unknown':
        category_tags_str = ', '.join([tag.split(":")[1] for tag in category_tags])
        keywords_str = ', '.join(keywords)

        expiration_date = ''
        for date in sorted(product_array[1]):
            #prevedeni jednotlivych dat do stringu
            formatted_expiration_date = date.strftime('%Y-%m-%d')
            #pridani do str
            expiration_date += formatted_expiration_date + ', '

        #vlozeni noveho zaznamu do databaze
        update_mysql_dtb("INSERT INTO client_food_table (name, brand, quantity, small_image_url, category_tags, keywords, expiration_date, barcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",(product_name, product_brand, quantity, small_image_url, category_tags_str, keywords_str, expiration_date, sql_brcd))

        #sql = """INSERT INTO client_food_table (name, brand, quantity, small_image_url, category_tags, keywords, expiration_date, barcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        #val = (product_name, product_brand, quantity, small_image_url, category_tags_str, keywords_str, expiration_date, sql_brcd)
        #cursor.execute(sql, val)
        #conn.commit()

        # uzavreni pripojeni databaze kvuli spravne aktualizaci databaze
        conn.close()
        #obnoveni aplikace
        Clock.schedule_once(refresh_function,0.1)

#spusteni funkce
#upload_product_to_database(product_array)