from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from functools import reduce
import pandas as pd
import re

# función para scrapear los datos de sumario de un mapa
def get_stats_summary(driver):

    historial=driver.find_element_by_xpath("//a[contains(text(), 'Match history')]").get_attribute("href")
    tiempo = driver.find_element_by_xpath("//div[contains(text(), 'Game Time')]").find_element_by_css_selector("h1").text
    parche = driver.find_element_by_xpath("//div[contains(text(), 'Game Time')]").find_element_by_xpath("..").find_elements_by_css_selector("div")[2].text

    # coge ambos equipos y apunta el ganador
    equipo_azul = driver.find_element_by_css_selector("div.blue-line-header")
    nombre_azul = equipo_azul.text.split(" - ")[0]
    if 'WIN' in equipo_azul.text.split(" - ")[1]:
        gana_azul = 1
    else:
        gana_azul = 0
    equipo_rojo = driver.find_element_by_css_selector("div.red-line-header")
    nombre_rojo = equipo_rojo.text.split(" - ")[0]
    if 'WIN' in equipo_rojo.text.split(" - ")[1]:
        gana_rojo = 1
    else:
        gana_rojo = 0

    # coge el numero de asesinatos de cada equipo y quien se hace la primera primera_sangre
    asesinatos_azul=equipo_azul.find_element_by_xpath("../..").find_element_by_css_selector("img[alt=Kills]")
    num_asesinatos_azul=asesinatos_azul.find_element_by_xpath("..").text
    # en caso de que haya algun problema identificando la primera sangre, se asigna como None
    primera_sangre = None
    primera_sangre_lista=asesinatos_azul.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='First Blood']")
    if len(primera_sangre_lista) != 0:
        primera_sangre = nombre_azul


    asesinatos_rojo=equipo_rojo.find_element_by_xpath("../..").find_element_by_css_selector("img[alt=Kills]")
    num_asesinatos_rojo=asesinatos_rojo.find_element_by_xpath("..").text
    primera_sangre_lista=asesinatos_rojo.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='First Blood']")
    if len(primera_sangre_lista) != 0:
        primera_sangre = nombre_rojo

    # coge el numero de torres de cada equipo y quien se hace la primera primera_torre
    torres_azul=equipo_azul.find_element_by_xpath("../..").find_element_by_css_selector("img[alt=Towers]")
    num_torres_azul=torres_azul.find_element_by_xpath("..").text
    # en caso de que haya algun problema identificando la primera sangre, se asigna como None
    primera_torre = None
    primera_torre_lista=torres_azul.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='First Tower']")
    if len(primera_torre_lista) != 0:
        primera_torre = nombre_azul


    torres_rojo=equipo_rojo.find_element_by_xpath("../..").find_element_by_css_selector("img[alt=Towers]")
    num_torres_rojo=torres_rojo.find_element_by_xpath("..").text
    primera_torre_lista=torres_rojo.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='First Tower']")
    if len(primera_torre_lista) != 0:
        primera_torre = nombre_rojo

    # se obtiene el número de dragones de cada equipo y su tipo si está indicado
    dragones_azul=equipo_azul.find_element_by_xpath("../..").find_element_by_css_selector("img[alt=Dragons]")
    num_dragones_azul=dragones_azul.find_element_by_xpath("..").text
    dragones_viento_azul=dragones_azul.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='Cloud Drake']")
    num_dragones_viento_azul = len(dragones_viento_azul)
    dragones_infierno_azul=dragones_azul.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='Infernal Drake']")
    num_dragones_infierno_azul = len(dragones_infierno_azul)
    dragones_oceano_azul=dragones_azul.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='Ocean Drake']")
    num_dragones_oceano_azul = len(dragones_oceano_azul)
    dragones_montaña_azul=dragones_azul.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='Mountain Drake']")
    num_dragones_montaña_azul = len(dragones_montaña_azul)

    dragones_rojo=equipo_rojo.find_element_by_xpath("../..").find_element_by_css_selector("img[alt=Dragons]")
    num_dragones_rojo=dragones_rojo.find_element_by_xpath("..").text
    dragones_viento_rojo=dragones_rojo.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='Cloud Drake']")
    num_dragones_viento_rojo = len(dragones_viento_rojo)
    dragones_infierno_rojo=dragones_rojo.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='Infernal Drake']")
    num_dragones_infierno_rojo = len(dragones_infierno_rojo)
    dragones_oceano_rojo=dragones_rojo.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='Ocean Drake']")
    num_dragones_oceano_rojo = len(dragones_oceano_rojo)
    dragones_montaña_rojo=dragones_rojo.find_element_by_xpath("../..").find_elements_by_css_selector("img[alt='Mountain Drake']")
    num_dragones_montaña_rojo = len(dragones_montaña_rojo)

    # se obtiene el número de nashor de cada equipo
    nashors_azul=equipo_azul.find_element_by_xpath("../..").find_element_by_css_selector("img[alt=Nashor]")
    num_nashors_azul=nashors_azul.find_element_by_xpath("..").text
    nashors_rojo=equipo_rojo.find_element_by_xpath("../..").find_element_by_css_selector("img[alt=Nashor]")
    num_nashors_rojo=nashors_rojo.find_element_by_xpath("..").text

    # se obtiene el oro de cada equipo
    oro_azul=equipo_azul.find_element_by_xpath("../..").find_element_by_css_selector("img[alt='Team Gold']")
    num_oro_azul=oro_azul.find_element_by_xpath("..").text
    oro_rojo=equipo_rojo.find_element_by_xpath("../..").find_element_by_css_selector("img[alt='Team Gold']")
    num_oro_rojo=oro_rojo.find_element_by_xpath("..").text

    # se obtienen los baneos de cada equipo, el último puede faltar porque un equipo elija banear solo 4 campeones
    baneos_azul=equipo_azul.find_element_by_xpath("../..").find_element_by_xpath(".//div[contains(text(),'Bans')]").find_element_by_xpath("..").find_elements_by_css_selector("a")
    ban1_azul=baneos_azul[0].get_attribute("title").split(" ")[0]
    ban2_azul=baneos_azul[1].get_attribute("title").split(" ")[0]
    ban3_azul=baneos_azul[2].get_attribute("title").split(" ")[0]
    ban4_azul=baneos_azul[3].get_attribute("title").split(" ")[0]
    try:
        ban5_azul=baneos_azul[4].get_attribute("title").split(" ")[0]
    except:
        ban5_azul="no ban"

    baneos_rojo=equipo_rojo.find_element_by_xpath("../..").find_element_by_xpath(".//div[contains(text(),'Bans')]").find_element_by_xpath("..").find_elements_by_css_selector("a")
    ban1_rojo=baneos_rojo[0].get_attribute("title").split(" ")[0]
    ban2_rojo=baneos_rojo[1].get_attribute("title").split(" ")[0]
    ban3_rojo=baneos_rojo[2].get_attribute("title").split(" ")[0]
    ban4_rojo=baneos_rojo[3].get_attribute("title").split(" ")[0]
    try:
        ban5_rojo=baneos_rojo[4].get_attribute("title").split(" ")[0]
    except:
        ban5_rojo="no ban"

    # campeones escogidos por cada equipo
    campeones_azul=equipo_azul.find_element_by_xpath("../..").find_element_by_xpath(".//div[contains(text(),'Picks')]").find_element_by_xpath("..").find_elements_by_css_selector("a")
    pick1_azul=campeones_azul[0].get_attribute("title").replace(" stats", "")
    pick2_azul=campeones_azul[1].get_attribute("title").replace(" stats", "")
    pick3_azul=campeones_azul[2].get_attribute("title").replace(" stats", "")
    pick4_azul=campeones_azul[3].get_attribute("title").replace(" stats", "")
    pick5_azul=campeones_azul[4].get_attribute("title").replace(" stats", "")

    campeones_rojo=equipo_rojo.find_element_by_xpath("../..").find_element_by_xpath(".//div[contains(text(),'Picks')]").find_element_by_xpath("..").find_elements_by_css_selector("a")
    pick1_rojo=campeones_rojo[0].get_attribute("title").replace(" stats", "")
    pick2_rojo=campeones_rojo[1].get_attribute("title").replace(" stats", "")
    pick3_rojo=campeones_rojo[2].get_attribute("title").replace(" stats", "")
    pick4_rojo=campeones_rojo[3].get_attribute("title").replace(" stats", "")
    pick5_rojo=campeones_rojo[4].get_attribute("title").replace(" stats", "")

    # se guardan los jugadores de cada equipo
    jugadores_azul = driver.find_elements_by_css_selector("table.playersInfosLine")[0]
    jugadores_rojo = driver.find_elements_by_css_selector("table.playersInfosLine")[1]

    players_azul=jugadores_azul.find_elements_by_css_selector(".link-blanc")
    top_azul=players_azul[0].text
    jng_azul=players_azul[1].text
    mid_azul=players_azul[2].text
    adc_azul=players_azul[3].text
    sup_azul=players_azul[4].text

    players_rojo=jugadores_rojo.find_elements_by_css_selector(".link-blanc")
    top_rojo=players_rojo[0].text
    jng_rojo=players_rojo[1].text
    mid_rojo=players_rojo[2].text
    adc_rojo=players_rojo[3].text
    sup_rojo=players_rojo[4].text

    # se obtiene el kda de cada jugador
    kdas_azul = jugadores_azul.find_elements_by_css_selector("td[style='text-align:center']")
    kda_top_azul=kdas_azul[0].text
    kda_jng_azul=kdas_azul[1].text
    kda_mid_azul=kdas_azul[2].text
    kda_adc_azul=kdas_azul[3].text
    kda_sup_azul=kdas_azul[4].text
    # se generan als variables kills, deaths and assists para cada jugador
    kills_top_azul=kda_top_azul.split("/")[0]
    deaths_top_azul=kda_top_azul.split("/")[1]
    assists_top_azul=kda_top_azul.split("/")[2]
    kills_jng_azul=kda_jng_azul.split("/")[0]
    deaths_jng_azul=kda_jng_azul.split("/")[1]
    assists_jng_azul=kda_jng_azul.split("/")[2]
    kills_mid_azul=kda_mid_azul.split("/")[0]
    deaths_mid_azul=kda_mid_azul.split("/")[1]
    assists_mid_azul=kda_mid_azul.split("/")[2]
    kills_adc_azul=kda_adc_azul.split("/")[0]
    deaths_adc_azul=kda_adc_azul.split("/")[1]
    assists_adc_azul=kda_adc_azul.split("/")[2]
    kills_sup_azul=kda_sup_azul.split("/")[0]
    deaths_sup_azul=kda_sup_azul.split("/")[1]
    assists_sup_azul=kda_sup_azul.split("/")[2]

    kdas_rojo = jugadores_rojo.find_elements_by_css_selector("td[style='text-align:center']")
    kda_top_rojo=kdas_rojo[0].text
    kda_jng_rojo=kdas_rojo[1].text
    kda_mid_rojo=kdas_rojo[2].text
    kda_adc_rojo=kdas_rojo[3].text
    kda_sup_rojo=kdas_rojo[4].text
    kills_top_rojo=kda_top_rojo.split("/")[0]
    deaths_top_rojo=kda_top_rojo.split("/")[1]
    assists_top_rojo=kda_top_rojo.split("/")[2]
    kills_jng_rojo=kda_jng_rojo.split("/")[0]
    deaths_jng_rojo=kda_jng_rojo.split("/")[1]
    assists_jng_rojo=kda_jng_rojo.split("/")[2]
    kills_mid_rojo=kda_mid_rojo.split("/")[0]
    deaths_mid_rojo=kda_mid_rojo.split("/")[1]
    assists_mid_rojo=kda_mid_rojo.split("/")[2]
    kills_adc_rojo=kda_adc_rojo.split("/")[0]
    deaths_adc_rojo=kda_adc_rojo.split("/")[1]
    assists_adc_rojo=kda_adc_rojo.split("/")[2]
    kills_sup_rojo=kda_sup_rojo.split("/")[0]
    deaths_sup_rojo=kda_sup_rojo.split("/")[1]
    assists_sup_rojo=kda_sup_rojo.split("/")[2]

    # se obtienen los minions para cada jugador
    css_azul = jugadores_azul.find_elements_by_css_selector("td[style='text-align:center;']")
    css_top_azul=css_azul[0].text
    css_jng_azul=css_azul[1].text
    css_mid_azul=css_azul[2].text
    css_adc_azul=css_azul[3].text
    css_sup_azul=css_azul[4].text

    css_rojo = jugadores_rojo.find_elements_by_css_selector("td[style='text-align:center;']")
    css_top_rojo=css_rojo[0].text
    css_jng_rojo=css_rojo[1].text
    css_mid_rojo=css_rojo[2].text
    css_adc_rojo=css_rojo[3].text
    css_sup_rojo=css_rojo[4].text

    # se obtienen los summoners para cada jugador, pueden faltar y por tanto están con un try/except
    try:
        summoners_azul=jugadores_rojo.find_elements_by_css_selector("img[alt='Summoner spell']")
        summoner_1_top_azul=summoners_azul[0].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_top_azul=summoners_azul[1].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_1_jng_azul=summoners_azul[2].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_jng_azul=summoners_azul[3].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_1_mid_azul=summoners_azul[4].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_mid_azul=summoners_azul[5].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_1_adc_azul=summoners_azul[6].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_adc_azul=summoners_azul[7].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_1_sup_azul=summoners_azul[8].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_sup_azul=summoners_azul[9].get_attribute("src").split("/Summoner")[1].split(".")[0]

        summoners_rojo=jugadores_rojo.find_elements_by_css_selector("img[alt='Summoner spell']")
        summoner_1_top_rojo=summoners_rojo[0].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_top_rojo=summoners_rojo[1].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_1_jng_rojo=summoners_rojo[2].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_jng_rojo=summoners_rojo[3].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_1_mid_rojo=summoners_rojo[4].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_mid_rojo=summoners_rojo[5].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_1_adc_rojo=summoners_rojo[6].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_adc_rojo=summoners_rojo[7].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_1_sup_rojo=summoners_rojo[8].get_attribute("src").split("/Summoner")[1].split(".")[0]
        summoner_2_sup_rojo=summoners_rojo[9].get_attribute("src").split("/Summoner")[1].split(".")[0]
    except:
        summoner_1_top_azul = summoner_2_top_azul = None
        summoner_1_jng_azul = summoner_2_jng_azul = None
        summoner_1_mid_azul = summoner_2_mid_azul = None
        summoner_1_adc_azul = summoner_2_adc_azul = None
        summoner_1_sup_azul = summoner_2_sup_azul = None
        summoner_1_top_rojo = summoner_2_top_rojo = None
        summoner_1_jng_rojo = summoner_2_jng_rojo = None
        summoner_1_mid_rojo = summoner_2_mid_rojo = None
        summoner_1_adc_rojo = summoner_2_adc_rojo = None
        summoner_1_sup_rojo = summoner_2_sup_rojo = None

    # se guarda la información de visión accediendo a los scripts que contienen estos datos
    script_vision=driver.find_element_by_xpath("//th[contains(text(),'Vision')]").find_element_by_xpath("../..").find_element_by_css_selector("script")
    labels=re.sub('\s+',' ',script_vision.get_attribute('innerHTML').replace("\n", "").replace("\t","").replace("","")).split("{")[2:4]
    wards_rojo=re.search("\[(\d+).(\d+)", labels[0])
    wards_rojo=wards_rojo.group(0).replace("[","").split(",")
    wards_destroyed_rojo = wards_rojo[0]
    wards_placed_rojo = wards_rojo[1]

    wards_azul=re.search("\[(\d+).(\d+)", labels[1])
    wards_azul=wards_azul.group(0).replace("[","").split(",")
    wards_destroyed_azul = wards_azul[0]
    wards_placed_azul = wards_azul[1]

    # se guarda la información de jungla accediendo a los scripts que contienen estos datos
    script_vision=driver.find_element_by_xpath("//th[contains(text(),'Jungle share')]").find_element_by_xpath("../..").find_element_by_css_selector("script")
    labels=re.sub('\s+',' ',script_vision.get_attribute('innerHTML').replace("\n", "").replace("\t","").replace("","")).split("{")[2:4]
    jng_share_azul=re.search("\[(\d+)(.(\d+))?,(\d+)(.(\d+))?", labels[0])
    jng_share_azul=jng_share_azul.group(0).replace("[","").split(",")
    jng_share_15_azul = jng_share_azul[0]
    jng_share_azul = jng_share_azul[1]

    jng_share_rojo=re.search("\[(\d+)(.(\d+))?,(\d+)(.(\d+))?", labels[1])
    jng_share_rojo=jng_share_rojo.group(0).replace("[","").split(",")
    jng_share_15_rojo = jng_share_rojo[0]
    jng_share_rojo = jng_share_rojo[1]

    # se genera un dataframe para los resultados
    nombres = ["tiempo", "parche", "nombre_azul", "nombre_rojo", "gana_azul", "gana_rojo", "num_asesinatos_azul", "num_asesinatos_rojo", "primera_sangre", "num_torres_azul", "num_torres_rojo", "primera_torre", "num_dragones_azul"," num_dragones_viento_azul","num_dragones_infierno_azul", "num_dragones_oceano_azul", "num_dragones_montaña_azul", "num_dragones_rojo", "num_dragones_viento_rojo","num_dragones_infierno_rojo", "num_dragones_oceano_rojo", "num_dragones_montaña_rojo","num_nashors_azul", "num_nashors_rojo", "num_oro_azul", "num_oro_rojo","ban1_azul","ban2_azul","ban3_azul","ban4_azul","ban5_azul","ban1_rojo","ban2_rojo","ban3_rojo","ban4_rojo","ban5_rojo","pick1_azul","pick2_azul","pick3_azul","pick4_azul","pick5_azul","pick1_rojo","pick2_rojo","pick3_rojo","pick4_rojo","pick5_rojo", "top_azul", "jng_azul", "mid_azul", "adc_azul", "sup_azul", "top_rojo", "jng_rojo", "mid_rojo", "adc_rojo", "sup_rojo", "kills_top_azul", "deaths_top_azul", "assists_top_azul", "kills_jng_azul", "deaths_jng_azul"," assists_jng_azul", "kills_mid_azul", "deaths_mid_azul", "assists_mid_azul", "kills_adc_azul", "deaths_adc_azul", "assists_adc_azul", "kills_sup_azul", "deaths_sup_azul", "assists_sup_azul" ,"kills_top_rojo", "deaths_top_rojo", "assists_top_rojo", "kills_jng_rojo", "deaths_jng_rojo", "assists_jng_rojo", "kills_mid_rojo", "deaths_mid_rojo", "assists_mid_rojo", "kills_adc_rojo", "deaths_adc_rojo", "assists_adc_rojo", "kills_sup_rojo", "deaths_sup_rojo", "assists_sup_rojo", "summoner_1_top_azul", "summoner_2_top_azul", "summoner_1_jng_azul", "summoner_2_jng_azul", "summoner_1_mid_azul", "summoner_2_mid_azul", "summoner_1_adc_azul", "summoner_2_adc_azul", "summoner_1_sup_azul", "summoner_2_sup_azul", "summoner_1_top_rojo", "summoner_2_top_rojo", "summoner_1_jng_rojo", "summoner_2_jng_rojo", "summoner_1_mid_rojo", "summoner_2_mid_rojo", "summoner_1_adc_rojo", "summoner_2_adc_rojo", "summoner_1_sup_rojo", "summoner_2_sup_rojo", "css_top_azul", "css_jng_azul", "css_mid_azul", "css_adc_azul", "css_sup_azul", "css_top_rojo","css_jng_rojo", "css_mid_rojo", "css_adc_rojo", "css_sup_rojo", "wards_destroyed_azul", "wards_destroyed_rojo", "wards_placed_azul", "wards_placed_rojo","jng_share_15_azul","jng_share_15_rojo", "jng_share_azul", "jng_share_rojo"]
    atributos = [[tiempo, parche, nombre_azul, nombre_rojo, gana_azul, gana_rojo, num_asesinatos_azul, num_asesinatos_rojo, primera_sangre, num_torres_azul, num_torres_rojo, primera_torre, num_dragones_azul, num_dragones_viento_azul,num_dragones_infierno_azul, num_dragones_oceano_azul, num_dragones_montaña_azul, num_dragones_rojo, num_dragones_viento_rojo,num_dragones_infierno_rojo, num_dragones_oceano_rojo, num_dragones_montaña_rojo,num_nashors_azul, num_nashors_rojo, num_oro_azul, num_oro_rojo,ban1_azul,ban2_azul,ban3_azul,ban4_azul,ban5_azul,ban1_rojo,ban2_rojo,ban3_rojo,ban4_rojo,ban5_rojo,pick1_azul,pick2_azul,pick3_azul,pick4_azul,pick5_azul,pick1_rojo,pick2_rojo,pick3_rojo,pick4_rojo,pick5_rojo, top_azul, jng_azul, mid_azul, adc_azul, sup_azul, top_rojo, jng_rojo, mid_rojo, adc_rojo, sup_rojo, kills_top_azul, deaths_top_azul, assists_top_azul, kills_jng_azul, deaths_jng_azul, assists_jng_azul, kills_mid_azul, deaths_mid_azul, assists_mid_azul, kills_adc_azul, deaths_adc_azul, assists_adc_azul, kills_sup_azul, deaths_sup_azul, assists_sup_azul ,kills_top_rojo, deaths_top_rojo, assists_top_rojo, kills_jng_rojo, deaths_jng_rojo, assists_jng_rojo, kills_mid_rojo, deaths_mid_rojo, assists_mid_rojo, kills_adc_rojo, deaths_adc_rojo, assists_adc_rojo, kills_sup_rojo, deaths_sup_rojo, assists_sup_rojo, summoner_1_top_azul, summoner_2_top_azul, summoner_1_jng_azul, summoner_2_jng_azul, summoner_1_mid_azul, summoner_2_mid_azul, summoner_1_adc_azul, summoner_2_adc_azul, summoner_1_sup_azul, summoner_2_sup_azul, summoner_1_top_rojo, summoner_2_top_rojo, summoner_1_jng_rojo, summoner_2_jng_rojo, summoner_1_mid_rojo, summoner_2_mid_rojo, summoner_1_adc_rojo, summoner_2_adc_rojo, summoner_1_sup_rojo, summoner_2_sup_rojo, css_top_azul, css_jng_azul, css_mid_azul, css_adc_azul, css_sup_azul, css_top_rojo, css_jng_rojo, css_mid_rojo, css_adc_rojo, css_sup_rojo, wards_destroyed_azul, wards_destroyed_rojo, wards_placed_azul, wards_placed_rojo,jng_share_15_azul,jng_share_15_rojo, jng_share_azul, jng_share_rojo]]
    results = pd.DataFrame(atributos, columns=nombres)
    return results



# esta función recibe el dato de un nombre que se quiere extraer para cada jugador de la tabla de estadísticas y genera las 10 variables, una para cada jugador
def get_stat(driver,var,name):
    try:
        table_stats = driver.find_element_by_css_selector(".completestats")
        var_top_azul = table_stats.find_element_by_xpath(".//td[contains(text(),'"+str(var)+"')]/following-sibling::td")
        var_jng_azul = var_top_azul.find_element_by_xpath(".//following-sibling::td")
        var_mid_azul = var_jng_azul.find_element_by_xpath(".//following-sibling::td")
        var_adc_azul = var_mid_azul.find_element_by_xpath(".//following-sibling::td")
        var_sup_azul = var_adc_azul.find_element_by_xpath(".//following-sibling::td")
        var_top_rojo = var_sup_azul.find_element_by_xpath(".//following-sibling::td")
        var_jng_rojo = var_top_rojo.find_element_by_xpath(".//following-sibling::td")
        var_mid_rojo = var_jng_rojo.find_element_by_xpath(".//following-sibling::td")
        var_adc_rojo = var_mid_rojo.find_element_by_xpath(".//following-sibling::td")
        var_sup_rojo = var_adc_rojo.find_element_by_xpath(".//following-sibling::td")
        var_top_azul = var_top_azul.text
        var_jng_azul = var_jng_azul.text
        var_mid_azul = var_mid_azul.text
        var_adc_azul = var_adc_azul.text
        var_sup_azul = var_sup_azul.text
        var_top_rojo = var_top_rojo.text
        var_jng_rojo = var_jng_rojo.text
        var_mid_rojo = var_mid_rojo.text
        var_adc_rojo = var_adc_rojo.text
        var_sup_rojo = var_sup_rojo.text
        positions = ['top', 'jng', 'mid','adc','sup']
        teams = ['azul','rojo']
        nombres = []
        for team in teams:
            for pos in positions:
                nombres.append(name+"_"+team+"_"+pos)
        atributos = [[var_top_azul, var_jng_azul, var_mid_azul, var_adc_azul, var_sup_azul,var_top_rojo, var_jng_rojo, var_mid_rojo, var_adc_rojo,var_sup_rojo]]
        results = pd.DataFrame(atributos, columns=nombres)
    except:
        positions = ['top', 'jng', 'mid','adc','sup']
        teams = ['azul','rojo']
        nombres = []
        for team in teams:
            for pos in positions:
                nombres.append(name+"_"+team+"_"+pos)
        atributos = [[None, None, None, None, None,None, None, None, None,None]]
        results = pd.DataFrame(atributos, columns=nombres)
    return results

# esta función llama a la función anterior para cada variable que se quiere obtener y se juntan todos los dataframes resultantes en uno
def get_stats_table(driver):
    dfs=[get_stat(driver,"CS in Team", "cs_in_jung_team"),get_stat(driver,"CS in Enemy", "cs_in_jung_enemy"),get_stat(driver,"CSM","CSM"),get_stat(driver,"Golds","Golds"), get_stat(driver,"GPM","GPM"), get_stat(driver,"GOLD","GOLD"),
    get_stat(driver,"Vision Score", "Vision_Score"), get_stat(driver,"Wards placed", "Wards_placed"), get_stat(driver,"Wards destroyed","Wards_destroyed"),get_stat(driver,"Control Wards", "Control_Wards"),get_stat(driver,'VS%','VS%'),
    get_stat(driver,"Total damage to", "Total_damage_Champios"), get_stat(driver,"Physical Damage", "Physical_Damage_Champions"), get_stat(driver,"Magic Damage", "Magic_Damage_Champions"), get_stat(driver,"True Damage","True_Damage_Champions"), get_stat(driver,"DPM", "DPM"),
    get_stat(driver,"DMG","DMG"), get_stat(driver,"Solo kills","Solo_kills"), get_stat(driver,"Double kills","Double_kills"),get_stat(driver,"Triple kills","Triple_kills"),get_stat(driver,"Quadra kills","Quadra_kills"), get_stat(driver,"Penta kills","Penta_kills"),
    get_stat(driver,"CSD@15","CSD@15"),get_stat(driver,"XPD@15","XPD@15"), get_stat(driver,"LVLD@15", "LVLD@15"),
    get_stat(driver,"to turrets","Damage_towers"),get_stat(driver,"heal","heal"),get_stat(driver,"ccing","ccing")]
    df_final = reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True), dfs)

    return(df_final)
