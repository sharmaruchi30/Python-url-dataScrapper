import csv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import json
import psycopg2

def database_dump(p_title , p_imgurl , price , p_detail):
    
    hostname = 'localhost'
    database = 'A_urldata'
    username = 'postgres'
    pwd = '1234'
    port_id = 5432
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(host = hostname , dbname = database , user = username , password = pwd , port = port_id)

        cur = conn.cursor()
        
        create_table = ''' Create Table IF NOT EXISTS products_data (
                        id int,
                        p_title text,
                        img_url text,
                        price text,
                        p_detail text
        )
        '''
        cur.execute(create_table)

        conn.commit()

        cur.execute("Select max(id) from products_data")
        id = cur.fetchone()
        # print(id)
        if (id[0] == None):
            id = 1
        else:
            id = int(id[0])+1
        cur.execute(f"insert into products_data values ({id},'{p_title}','{p_imgurl}','{price}','{p_detail}')")
        # (f"insert into URLSDATA values ({id},'{p_title}','{p_imgurl}','{price}','{p_detail}')")
        conn.commit()

    except Exception as e:
        print(e)

    finally:
        if cur is not None:
            cur.close()

        if conn is not None:
            conn.close()
    # con = sqlite3.connect("A_dataScrape.db")
    # cur = con.cursor()
    # cur.execute("create table IF NOT EXISTS URLSDATA (id int,p_title text, imgurl text , price text , p_details text )")
    # con.commit()
    
    # cur.execute("Select max(id) from URLSDATA")
    # id = cur.fetchone()
    # # print(id)
    # if (id[0] == None):
    #     id = 1
    # else:
    #     id = int(id[0])+1
    # cur.execute(f"insert into URLSDATA values (?,?,?,?,?);",(id, p_title, p_imgurl , price , p_detail))
    # # (f"insert into URLSDATA values ({id},'{p_title}','{p_imgurl}','{price}','{p_detail}')")
    # con.commit()
    # con.close()



class GetUrls:
    def __init__(self):
        ser= Service("D:\\New folder\\chromedriver.exe")
        # ser = webdriver.Chrome(executable_path=executable_path)
        # "D:\\New folder\\chromedriver.exe"
        self.driver = webdriver.Chrome(service=ser)

        ##Enable Browser Logging
        d = DesiredCapabilities.CHROME
        d['loggingPrefs'] = {'browser' :'All'}
        # self.driver = webdriver.Chrome(desired_capabilities=d)

        ## Creating dictionary
        ScrapeVals = {}
        # DEFINING KEYS
        prot = "Product Title"
        iu = "Image URL"
        cost = "Price"
        ProDet = "Product Detail"

        # print(self.driver.page_source)
        count = 0
        with open("Amazon Scraping - Sheet1.csv", "r") as csv_file:
            reader = csv.reader(csv_file)
            scrapenums = 1
            start_time = time.time()
            for i in reader:
                asin = i[2]
                country_code =i[3]
                count += 1
                if (count % 100 == 0):
                    stop_time = time.time()
                    print("100 URL's Complete. Time Stamp in Seconds :", stop_time - start_time)
                    start_time = time.time()
                else:
                    pass
                self.driver.get(f"https://www.amazon.{country_code}/dp/{asin}")
                # r = requests.get(f"https://www.amazon.{country_code}/dp/{asin}")
                log_message = 'success'

                for entry in self.driver.get_log('browser'):

                    if entry['message'] == f'https://www.amazon.{country_code}/dp/{asin} - Failed to load resource: the server responded with a status of 404 ()':
                        log_message = '404'


                if log_message == "404" :
                    print(f"https://www.amazon.{country_code}/dp/{asin}" , " not available")
                else:
                        ### Getting Title

                        title = self.driver.find_element(By.ID, "productTitle")
                        ### IMAGE URL
                        try:
                            imgdiv = self.driver.find_element(By.ID, "imgTagWrapperId")
                            img = imgdiv.find_element(By.TAG_NAME, "img")
                        except:
                            pass

                        try:
                            imgdiv = self.driver.find_element(By.ID, "img-canvas")
                            img = imgdiv.find_element(By.TAG_NAME, "img")
                        except:
                            pass

                        ### Price
                        try:

                            currencysymbol = self.driver.find_element(By.CLASS_NAME, "a-price-symbol")
                            cs = (currencysymbol.text)

                            price = self.driver.find_element(By.CLASS_NAME, "a-price-whole")
                            pp = price.text

                            price_fraction = self.driver.find_element(By.CLASS_NAME, "a-price-fraction")
                            pf = price_fraction.text
                            # print(cs + pp + "." + pf)
                            finalprice = cs + pp + "." + pf
                        except:
                            pass
                        try:
                            currencysymbol = self.driver.find_element(By.ID, "twister-plus-price-data-price")
                            pp = currencysymbol.get_attribute('value')

                            currencysymbol = self.driver.find_element(By.ID, "twister-plus-price-data-price-unit")
                            ppu = currencysymbol.get_attribute('value')
                            finalprice = pp+ppu
                            # price_fraction = self.driver.find_element(By.CLASS_NAME, "a-price-fraction")
                            # pf = price_fraction.text
                            # print(cs +pp + "." + pf)
                        except:
                            pass

                        ## Product Details
                        try:

                            product_details = self.driver.find_element(By.ID, "productDescription")
                            pd = product_details.find_element(By.TAG_NAME, "p")
                            # print(pd.text)
                        except:
                            pass
                        try:
                            pd = self.driver.find_element(By.ID, "bookDescription_feature_div")

                        except:
                            pass

                        ScrapeVals.update({scrapenums:{prot:title.text,iu :img.get_attribute("src") ,cost:finalprice,ProDet :pd.text}})
                        print(title.text)
                        database_dump(title.text ,img.get_attribute("src"),finalprice,pd.text)
                        scrapenums += 1

            print("PRINTING ALL DATA IN PYTHON DICTIONARY :- \n")
            print(ScrapeVals)
            with open("URLSDATA.json", "w") as outfile:
                json.dump(ScrapeVals, outfile , indent=4)






open = GetUrls()

