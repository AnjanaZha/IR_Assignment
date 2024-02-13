from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import time
from requests.auth import HTTPBasicAuth
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os
import schedule
from time import sleep

URL ='https://pureportal.coventry.ac.uk/en/organisations/ihw-centre-for-health-and-life-sciences-chls'

APP_ROOT = os.path.abspath(__file__)

def chromedriver_assign(path, size):
    options = webdriver.ChromeOptions()

    #setup screen size for the crawler
    if(size == 'normal'):
        options.add_argument("--window-size=1366,741")
    elif(size == 'max'):
        options.add_argument("--window-size=195,1053")
    else:
        options.add_argument("--start-maximized")
    
    # options.add_argument("--headless") #operates in headless mode
    options.add_argument("--no-sandbox")  # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage")  # Overcome limited resources problem in Docker
    prefs = {"download.default_directory": path, 
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True}
    options.add_experimental_option("prefs",prefs)

    return options


def retrieve_data():
    start_time = time()

    #for filling CSV file
    actual_title = []
    actual_url = []
    actual_authors = []
    actual_original_language = []
    actual_publication_status = []

    path = os.path.dirname(APP_ROOT)

    options = chromedriver_assign(path, size='normal')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(URL)
    driver.implicitly_wait(10)

    window_size = driver.get_window_size()
    print("Window size:", window_size)

    #accept cookies
    accept_cookies_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="onetrust-accept-btn-handler"]')))
    accept_cookies_btn.click()

    research_output_btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main-navigation"]/ul/li[4]/a')))
    research_output_btn.click()

    #wait for the page to load
    sleep(2)

    #get the searchword
    search_word = input('Enter Please Enter the Search Word: ')

    #searching for the search word
    search_bar = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="global-search-input"]')))
    search_bar.send_keys(search_word)
    search_bar.send_keys(Keys.RETURN)

    #wait for the page to load
    sleep(5)

    links = []

    #search result div
    searh_results_div = WebDriverWait(driver, 5).until(lambda d: d.find_element(
        By.XPATH, '//*[@id="main-content"]/div/div[2]')
    )

    #search_results links
    link_h3_a_tag =  WebDriverWait(driver, 5).until(lambda d: d.find_elements(
        By.XPATH, '//*[@id="main-content"]/div/div[2]/ul/li/div[1]/div/h3/a')
    )

    #getting all the links
    for a_tag in link_h3_a_tag:
        href = a_tag.get_attribute("href")
        links.append(href)


    #removing duplicate links
    actual_links = list(dict.fromkeys(links))

    for research_paper_url in actual_links:

        title = None
        url = None
        authors = None
        original_language = None
        publication_status = None

        try:
            print(research_paper_url)
            driver.get(research_paper_url)

            sleep(5)
            
            url = research_paper_url

            try:
                title = WebDriverWait(driver, 5).until(lambda d: d.find_element(
                    By.XPATH, '//*[@id="page-content"]/div[1]/section/div[1]/div/div[1]/div[1]/h1/span').text
            )
            except:
                title = None

            try:
                authors = WebDriverWait(driver, 5).until(lambda d: d.find_element(
                    By.XPATH, '//p[@class="relations persons"]').text
            )
            except:
                authors = None

            #scroll to view
            element = WebDriverWait(driver, 5).until(lambda d: d.find_element(
                    By.XPATH, '//*[@id="main-content"]/section[1]/div/div/div[1]')
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", element)

            try:
                original_language = WebDriverWait(driver, 5).until(lambda d: d.find_element(
                    By.XPATH, '//tr[@class="language"]/td').text
            )
            except:
                original_language = None

            try:
                publication_status = WebDriverWait(driver, 5).until(lambda d: d.find_element(
                    By.XPATH, '//span[@class="date"]').text
            )
            except:
                publication_status = None


            #appending to the list
            actual_title.append(title)
            actual_url.append(url)
            actual_authors.append(authors)
            actual_original_language.append(original_language)
            actual_publication_status.append(publication_status)

        except:
            continue


    #making into csv file
    data = {
        'Title': actual_title,
        'Url':actual_url,
        'Authors':actual_authors,
        'Original Language':actual_original_language,
        'Publication Status':actual_publication_status,
    }

    df = pd.DataFrame(data)

    df.to_csv(f'Output_{search_word}.csv',index = False)



if __name__ == "__main__":
    retrieve_data()
