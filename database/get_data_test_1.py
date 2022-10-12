import requests
import bs4
from bs4 import BeautifulSoup
import os
import time
from selenium.webdriver.common.by import By
from selenium import webdriver


url = ''
response = requests.get(url)
#Весь код страницы 
soup = BeautifulSoup(response.text, 'lxml')

def get_pagination_limit():
    #Получить ссылку последней страницы (пока бесполезно, но мб пригодится)
    pages_block = soup.find ("ul", class_="paginator-module__pages___1azUM")
    pages_container = pages_block.select("li")
    last_button = pages_container[-2]
    last_button_2 = last_button.select_one("a", class_="base-module__base___7FUQ1 base-module__base-text____L6Jb base-module__button___3TuZj base-module__size-m___2sS92 paginator-button-module__paginator-button___20KL4")
    last_href = last_button_2.get("href")
    #Получить номер последней страницы
    num_last_page = int(pages_block.text.split(".")[-1])
    return num_last_page

#Можно добавить еще в параметры станции метро и тд
def get_page(page: int):
    if page and page>1:
        params={"pageNumber":page}
        response = requests.get(url, params=params)
    else:
        response = requests.get(url)
    return response

def get_blocks(data_page):
    soup = BeautifulSoup(data_page.text, 'lxml')
    soup_flats = soup.find ("ul", class_="OffersSearchList__list")
    container = soup_flats.select ("li", class_="OffersSearchList__item")
    for item in container:
        parse_block(item)
        #print (item)

def parse_block(item):
    flag=False
    try:
        #инфа о квартире
        brief_info_about_flat_text = item.find("div", class_ = "fonts-module__promo-subheader-alone___4BOzH fonts-module__bold___2Zct2").text
        info_about_flat = item.find ("p", class_= "color-primitives-module__black-400___203En fonts-module__secondary-alone___3wVR-")
        #цена
        price = item.find ("div", class_="LayoutSnippet__price")
        price_for_meter = item.find("div", class_="OfferSnippet__price-detail")
        #метро и время до него
        metro = item.find ("span", class_="colors-named-module__primary___3m87l fonts-module__primary___2PNSt SubwayStation__title")
        time_to_the_station_metro= item.find("div", class_="color-primitives-module__black-400___203En fonts-module__primary___2PNSt")
        #ссылка
        url_block = item.select_one('div',class_='LayoutSnippet__title')
        url_block_2 = url_block.select_one('a',class_='LinkSnippet LinkSnippet_hover')
        href = url_block_2.get('href')
        #адрес 
        address_block = item.find ("div", class_="ClClickableAddress__links")
        address = ", ".join(address_block.text.split("•")[0].split(","))
        distance_to_center = address_block.text.split("•")[1].strip()
        flag=True
    except:
        None
    if flag:
        print ("\n\n\n\n_______________")
        print (f"\nНОВАЯ КВАРТИРА \n{brief_info_about_flat_text}")
        print (f"\nО КВАРТИРЕ \n{info_about_flat.text}")
        print (f"\nПолная стоимость \n{price.text}")
        print (f"\nCтоимость кв. метра \n{price_for_meter.text}")
        print (f"\nМЕТРО \n{metro.text} пешком {metro.text}")
        print (f"\nССЫЛКА \n{href}")
        print (f"\nДо центра: \n{distance_to_center}")
        print (f"\nАдрес: \n{address}")
        print ("\nИНФА ОБ ОБЪЯВЛЕНИИ: \n")
        parse_page(href)
        import_images(href)
        print ("_______________")

def parse_page (url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    block_description_all = soup.find_all ("div", class_="grid-module__container___39oIv grid-module__gap___2HbMS")
    
    block_description_apart = block_description_all[0]
    blocks_apart = block_description_apart.find_all("div", class_="grid-module__cell___3uBi0")

    block_description_house = block_description_all[1]
    blocks_house = block_description_house.find_all("div", class_="grid-module__cell___3uBi0")
    
    description_of_apartment={}
    description_of_house={}
    
    for block in blocks_apart:
        key = (block.find ("div", class_="colors-named-module__secondary___2WPH_ fonts-module__secondary-alone___3wVR-"))
        value = (block.find (class_="fonts-module__primary___2PNSt DescriptionCell__value"))
        description_of_apartment[key.text]=value.text.replace(u'\xa0', u' ')

    for block in blocks_house:
        key = (block.find ("div", class_="colors-named-module__secondary___2WPH_ fonts-module__secondary-alone___3wVR-"))
        value = (block.find (class_="fonts-module__primary___2PNSt DescriptionCell__value"))
        description_of_house[key.text]=value.text.replace(u'\xa0', u' ')
 
    print (f"\nОписание квартиры: {description_of_apartment}")
    print (f"Описание дома: {description_of_house}")
    try:
        offerCard_content_block = soup.find ("div", class_="OfferCard__content")
        views = (offerCard_content_block.find("div", class_="color-primitives-module__black-400___203En OfferStatView")).text
        print (f"Просмотры: {views}")
        date = (offerCard_content_block.find("div", class_="colors-named-module__secondary___2WPH_ OfferCard__lastUpdate")).text
        print (f"Дата публикации: {date}")
    except:
        None

def import_images(url):
    global num_folder, browser

    browser.get(url)
    button_block = browser.find_elements(By.CLASS_NAME, 'GalleryOfferCard__btn')
    try:
        button = button_block[-1]
        button.click()
        container_images = browser.find_elements(By.CLASS_NAME,"GalleryDesktopPicture__image")
        for item in container_images:
            image_link = item.get_attribute('src')
            print(image_link)
            save_images(image_link)    
        num_folder=num_folder+1
    except:
        print ("Ошибка в импорте картинок")


def change_url(url):
    url_2=url.split("/")
    url_2[4]="s1000x1000"
    urt_resize="/".join(url_2)
    return urt_resize


def save_images(url):
    global num_folder
    os.makedirs(str(folder_name)+"/"+str(num_folder), exist_ok=True)
    image = requests.get(change_url(url))
    path=folder_name+"/"+str(num_folder)+"/"+(url.split("/"))[8]
    with open(path+".jpg", "wb") as f:
        f.write(image.content)


def parse_all ():
    global browser
    limit = get_pagination_limit()
    #пока что сделаю лимит 1 страница
    #больше одной страницы не советую делать пока что)))
    limit = 1
    for num in range (1, limit+1):
        num_response = get_page(num)
        browser = webdriver.Chrome()
        get_blocks (num_response)
        browser.quit()
      

folder_name="images"
os.makedirs(folder_name, exist_ok=True)
num_folder=1

parse_all()
