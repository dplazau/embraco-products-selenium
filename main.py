from csv import DictWriter
from datetime import datetime
from multiprocessing.connection import wait
from pprint import pprint

import pandas as pd
# import requests
from bs4 import BeautifulSoup
from helium import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# splash container needed https://splash.readthedocs.io/en/stable/install.html
def get_soup(url, driver):
    # response = requests.get('http://localhost:8050/render.html', params={'url': url, 'wait': 5})
    driver.get(url)
    products = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "product-row")))
    return products


def get_product_attributes(products):
    products_list = []
    for product in products:
        product_dict = {}
        product = product.get_attribute("outerHTML")
        product_soup = BeautifulSoup(product, 'html.parser')
        product_specs_list = product_soup.find('a').get_attribute_list(key="aria-label")[0].split(", ")
        for spec in product_specs_list:
            spec = spec.split(": ")
            if len(spec) > 1:
                key = spec[0]
                value = spec[1]
                product_dict[key] = value
        pprint(product_dict)        
        products_list.append(product_dict)
    return products_list
    

def main ():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    url = 'https://products.embraco.com/compressors'
    time_stamp = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    file_type = ".csv"
    file_name = f'COMPRESSORS-{time_stamp}{file_type}'
    page_products = get_soup(url, driver)
    next_btn = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "next")))
    products_list = get_product_attributes(page_products)
    keys = products_list[0].keys()
    try:
        with open (file_name, "w", encoding='utf-8' ) as csv_file:
            csv_writer = DictWriter(csv_file, keys)
            csv_writer.writeheader()
            while next_btn:
                csv_writer.writerows(products_list)
                next_btn.click()        
                products_list = get_product_attributes(page_products)
    except PermissionError as err:
        print(err, 'If you have the file open close it please!')
    except KeyboardInterrupt as err:
        print(err, 'The user has cancelled the scraping...')
    except:
        raise
    finally:
        driver.quit()
        csv_file.close()




if '__main__' == __name__:
    main()
