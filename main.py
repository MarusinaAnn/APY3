import requests
from bs4 import BeautifulSoup
from fake_headers import Headers
import json
from pprint import pprint
import re

HOST = "https://spb.hh.ru"
VARIENTS = f"{HOST}/search/vacancy?text=python&area=1&area=2&"


def get_headers():
    return Headers(browser="firefox", os="win").generate()


def get_text(url):
    return requests.get(url, headers=get_headers()).text


def parse_vacancy(vacancy_tag, salary):
    link_tag = vacancy_tag.find("a", class_="serp-item__title")
    if link_tag is None:
        return
    link = link_tag["href"]

    l = get_text(link)
    soup = BeautifulSoup(l, features="lxml")
    desc = soup.find(class_="vacancy-description").text
    if desc is None:
        return
    
    city = vacancy_tag.find(attrs={"data-qa":"vacancy-serp__vacancy-address"})
    if city is None:
        return

    company_name = vacancy_tag.find('a', attrs={"data-qa":"vacancy-serp__vacancy-employer"})
    if company_name is None:
        return

    name = link_tag.text
    regexp_search = r'.*((D|d)jango).*((F|f)lask).*'
    pr=r'.*(USD).*'
    if re.search(regexp_search, desc):
        resume = {
            "name": link_tag.text,
            "salary": salary,
            "link": link,
            "city": city.text.split(',')[0],
            "company_name": company_name.text.replace("\xa0"," "),
        }
        return resume
    

def parse_page(page):
    html = get_text(f"{VARIENTS}page={page}&hhtmFrom=vacancy_search_list")
    soup = BeautifulSoup(html, features="lxml")
    vacancies = soup.find(class_="vacancy-serp-content").find_all(class_="serp-item")
    salary = soup.find("span", class_="bloko-header-section-3").text.replace("\u2009","").replace("\xa0"," ").replace("\u202f"," ")
    
    for vacancy in vacancies:
        parsed = parse_vacancy(vacancy, salary)
        vacancies_parsed.append(parsed)     
    return vacancies_parsed


if __name__ == "__main__": 
    vacancies_parsed = [] 
    for page in range(1, 41):
        print(page)
        print(parse_page(page))
        
        with open('vacancies.json', 'w', encoding='UTF-8') as v:
            json.dump(parse_page(page), v, ensure_ascii=False, indent=2)