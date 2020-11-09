
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from functools import reduce
import pandas as pd
import time

# coge los torneos de la web
def get_tournaments(conductor):
    links = conductor.find_element_by_link_text('Quick Access').find_element_by_xpath('..').find_elements_by_css_selector('a.nav-link')
    tournaments = {}
    for child in links:
        tournaments[child.get_attribute('text')] = child.get_attribute("href")
    return tournaments

# coge las partes de un torneo
def get_tournament_parts(conductor):
    links = conductor.find_element_by_css_selector('#gameMenuToggler').find_elements_by_css_selector('a.nav-link')
    parts = {}
    for child in links:
        parts[child.get_attribute('text').upper()] = child.get_attribute('text')
    return parts

# coge los partidos de una parte de un torneo
def get_partidos(cabeceras):
    partidos=cabeceras.find_element_by_xpath('..').find_element_by_css_selector('tbody').find_elements_by_css_selector("tr")
    matches = []
    for match in partidos:
        matches.append([match.find_elements_by_css_selector('td')[0].text, match.find_elements_by_css_selector('td')[5].text, match.find_elements_by_css_selector('td')[4].text])
    return matches

# accde al historial de partida y cambia la ventana
def match_history(conductor):
    # guarda la ventana actual para devolverla y que se pueda volver en otra funcion
    window_before = conductor.window_handles[0]
    referencia = conductor.find_element_by_css_selector("a[title='Riot Match History']").get_attribute("href")
    conductor.find_element_by_css_selector("a[title='Riot Match History']").click()
    window_after = conductor.window_handles[1]
    # se cambia de ventana
    conductor.switch_to.window(window_after)
    if 'gameHash' not in conductor.current_url:
        new_url = referencia.replace('en/#match-details//matchhistory.na.leagueoflegends.com/en','en')

        conductor.get(new_url)
        time.sleep(3)
        conductor.refresh()
    if 'ESPORT' not in conductor.current_url:
        new_url = conductor.current_url.replace('STMNT','ESPORTSTMNT')

        conductor.get(new_url)
        time.sleep(3)
        conductor.refresh()
    return(window_before)

# función para hacer log in en leagueoflegends.com, el usuario y contraseña no son correctos, hay que crearse una cuenta
def sign_in(conductor):
    WebDriverWait(conductor, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR , "button[title='Sign In']")))
    conductor.find_element_by_css_selector("input[name='username']").send_keys('$username')
    conductor.find_element_by_css_selector("input[name='password']").send_keys('$password')
    conductor.find_element_by_css_selector("input[type='checkbox']").click()

    conductor.find_element_by_css_selector("button[title='Sign In']").click()

# cierra la ventana actual y cambia a la ventana que se le pasa
def close_match_history(conductor,before):
    conductor.close()
    conductor.switch_to.window(before)
