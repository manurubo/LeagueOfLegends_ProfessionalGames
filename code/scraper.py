# ---------------------------------------------------------------
# Código para hacer web scraping a los datos de los mapas de las
# partidas de League of Legends
#
# 2020 Manuel Ruiz Botella, Tarragona, España
# Released under CC0: Public Domain License.
# email manuel.ruiz.botella@gmail.com or manurubo@uoc.edu
# ---------------------------------------------------------------


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

# import de las funciones creadas para el scraping
from scrape_gol import *
from scrape_mh import *
from navegate_web import *


# Creo el driver para navegar con selenium
driver = webdriver.Chrome(ChromeDriverManager().install())

# Web principal a la que acceder para scrapear los datos
web="https://gol.gg"
subdomain="/esports/home/"

# Se ha de maximizar la pantalla porque sino no funciona alguna pestaña de las que queremos scrapear
driver.maximize_window()
driver.get(web+subdomain)
try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'table_list ')))
except TimeoutException:
    print('Page timed out after 10 secs.')

# Se utiliza la función get_tournaments para obtener los torneos principales del año.
torneos = get_tournaments(driver)

# Se hace scraping de los partidos de los torneos que se indican en la lista.
# Se puede hacer varios torneos a la vez o producir uno cada vez
torneos_importantes = ["WORLDS","LEC", "LCS"]

# Token de inicio de sesión del historial de partidas
token=0

# Creo un dataframe donde almaceno los datos
extracted_data=pd.DataFrame()

# Tengo que acceder a cada torneo
for torneo, url in torneos.items():
    if torneo in torneos_importantes:
        # Se busca el texto del torneo en la página y se accede a su url
        elemento_torneo=driver.find_element_by_link_text(torneo)
        elemento_torneo.click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//th[contains(text(),'Tournament data')]")))


        # Cada torneo tiene varias partes (liga, playoff, relegations, etc)
        # Cada parte tiene una pestaña con su url. Se obtiene las partes de un torneo y en cada iteración se accede a una parte.
        parts = get_tournament_parts(driver)
        for part, part_low in parts.items():
            # Se busca el texto de la parte y se accede
            part_torneo=driver.find_element_by_link_text(part)
            part_torneo.click()


            WebDriverWait(driver, 30).until(EC.title_contains(part_low))

            time.sleep(3)

            # En la página hay varias headers, aquella que contiene los partidos es 'Last Games'
            headers1 = driver.find_elements_by_css_selector('h1')

            # Se recorren todos los headers pero solo se trabaja con la de partidos.
            # Está implementado así por si en un futuro se quiere hacer scraping de estadisticas del torneo, que son los otros headers
            for h1 in headers1:
                if (h1.text == 'Last games'):

                    # Se obtienen todos los partidos de la parte del torneo
                    partidos = get_partidos(h1)

                    # Se comprueba que se accede al partido correcto y no al mismo entre dos equipos siempre
                    # Se busca el dia del partido, sus equipos y la semana de la parte
                    # Son necesarios estos 3 datos porque dos equipos pueden llegar a jugar dos partidas el mismo día, pero una será de liga y la otra de tiebreaker
                    for equipos,fecha,semana in partidos:
                        # Se busca el dia
                        partidosdia = driver.find_elements_by_xpath("//td[contains(text(), '"+str(fecha)+"')]")
                        for partido in partidosdia:
                            partido = partido.find_element_by_xpath('..')

                            # Si los equipos están en el texto, es que es el partido correcto
                            if(equipos in partido.text) and (semana in partido.text):
                                break
                        # Se guarda la url actual para poder regresar a la página donde están todos los partidos
                        url_atras = driver.current_url
                        ref_partido = partido.find_element_by_css_selector('[href]').get_attribute("href")

                        # Si el partido todavía no se ha jugado, indica preview en su referencia y tenemos que ignorarlo
                        if 'preview' in ref_partido:
                            print("Partido no jugado todavía")
                        # Si el partido hes una serie de mapas, tiene indicado un summary, entonces trataremos cada mapa para extraer los datos
                        elif 'summary' in ref_partido:

                            # Se guardan los datos básicos hasta ahora.
                            nombres = ["torneo","parte","fecha","semana"]
                            atributos = [[torneo,part_low, fecha,semana]]
                            datos_partido = pd.DataFrame(atributos, columns=nombres)

                            # Se accede al partido
                            partido.find_element_by_css_selector('[href]').click()
                            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID , "gameMenuToggler")))

                            # Se obtienen los mapas del partido, para cada mapa se extraen unos datos
                            games=driver.find_elements_by_xpath("//a[contains(text(), 'Game')]")
                            for i in range(1,len(games)+1):
                                try:
                                    # Se accede al mapa
                                    game =driver.find_element_by_xpath("//a[contains(text(), 'Game "+str(i)+"')]")

                                    game.click()

                                    # Primero se accede al historial de partida de riot games, para ello se espera a que esté el enlace
                                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR , "a[title='Riot Match History']")))

                                    # Se accede al link con la función match_history y se devuelve la pestaña actual, ya que la función genera otra pestaña
                                    wind_before=match_history(driver)
                                    # Si es la primera vez que se accede al match_history en la ejecución se tiene que hacer login
                                    if(token == 0):
                                        sign_in(driver)
                                        token = 1

                                    # Se hace scraping de las gráficas interactivas de oro de la partida
                                    gold_graphs_data=scrap_gold_graphs(driver)

                                    # Se intenta acceder a la pestaña de estadisticas y se hace scraping
                                    # Si no se accedió a las estadisticas, simplemente los resultados serán vacios
                                    try:
                                        driver.find_element_by_xpath("//div[contains(text(),'Statistics')]").click()
                                    except:
                                        pass
                                    mh_stats = get_stats_table_mh(driver)
                                    # Se cierra la pestaña de match_history y se accede a la pestaña enterior de la web gol.gg
                                    close_match_history(driver,wind_before)
                                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR , "a[title='Riot Match History']")))

                                    # Se obtiene los datos del sumario de la página del mapa de gol.gg, son los unicos datos que no pueden ser nulos
                                    gol_summary=get_stats_summary(driver)

                                    # Se accede a la pestaña de stats
                                    driver.find_element_by_xpath("//a[contains(text(),'All stats')]").click()
                                    time.sleep(3)
                                    # A veces falla por internet ya que es una misma url todo, asique se refresca
                                    driver.refresh()
                                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME , 'completestats')))

                                    # Se obtienen las stas de gol
                                    gol_stats=get_stats_table(driver)

                                    # Cada una de las partes de extracción de datos ha generado un dataframe de pandas. Ahora se unen todos en uno
                                    dfs=[datos_partido,gol_summary,gold_graphs_data, mh_stats,gol_stats]
                                    df_final = reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True), dfs)

                                    # Si el dataset final está vacio, se asigna el dataset del mapa (solo ocurre la primera vez)
                                    if(extracted_data.empty):
                                        extracted_data=df_final
                                    # Sino, se añaden los datos del mapa a los datos en el dataset de otros mapas
                                    else:
                                        extracted_data = pd.concat([extracted_data,df_final])
                                except:
                                    print("Algo fue mal en el partido: "+str(equipos)+ " "+ str(fecha)+" Game "+str(i))
                                    print("Me salto este partido")
                                    pass
                            # Se vuelve a la página de la parte del torneo para ir al siguiente partido
                            driver.get(url_atras)
                            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME , 'footable-loaded')))

                        # Si el partido ha sido solo un mapa se accede directamente a hacer scraping del mapa
                        else:
                            try:

                                # Se guardan los datos básicos hasta ahora.
                                nombres = ["torneo","parte","fecha","semana"]
                                atributos = [[torneo,part_low, fecha,semana]]
                                datos_partido = pd.DataFrame(atributos, columns=nombres)

                                partido.find_element_by_css_selector('[href]').click()

                                # Primero se accede al historial de partida de riot games, para ello se espera a que esté el enlace
                                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR , "a[title='Riot Match History']")))
                                # Se accede al link con la función match_history y se devuelve la pestaña actual, ya que la función genera otra pestaña
                                wind_before=match_history(driver)
                                # Si es la primera vez que se accede al match_history en la ejecución se tiene que hacer login
                                if(token == 0):
                                    sign_in(driver)
                                    token = 1

                                # Se hace scraping de las gráficas interactivas de oro de la partida
                                gold_graphs_data=scrap_gold_graphs(driver)

                                # Se intenta acceder a la pestaña de estadisticas y se hace scraping
                                # Si no se accedió a las estadisticas, porque no existen, simplemente los resultados serán vacios
                                try:
                                    driver.find_element_by_xpath("//div[contains(text(),'Statistics')]").click()
                                except:
                                    pass
                                mh_stats = get_stats_table_mh(driver)

                                # Se cierra la pestaña de match_history y se accede a la pestaña enterior de la web gol.gg
                                close_match_history(driver,wind_before)
                                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR , "a[title='Riot Match History']")))


                                # Se obtiene los datos del sumario de la página del mapa de gol.gg
                                gol_summary=get_stats_summary(driver)

                                # Se accede a la pestaña de stats
                                driver.find_element_by_xpath("//a[contains(text(),'All stats')]").click()
                                time.sleep(3)
                                # A veces falla por internet ya que es una misma url todo, asique se refresca
                                driver.refresh()
                                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME , 'completestats')))

                                # Se obtienen las stas de gol
                                gol_stats=get_stats_table(driver)

                                # Cada una de las partes de extracción de datos ha generado un dataframe de pandas. Ahora se unen todos en uno
                                dfs=[datos_partido,gol_summary,gold_graphs_data, mh_stats,gol_stats]
                                df_final = reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True), dfs)
                                # Si el dataset final está vacio, se asigna el dataset del mapa (solo ocurre la primera vez)
                                if(extracted_data.empty):
                                    extracted_data=df_final
                                # Sino, se añaden los datos del mapa a los datos en el dataset de otros mapas
                                else:
                                    extracted_data = pd.concat([extracted_data,df_final])
                                # Se vuelve a la página de la parte del torneo para ir al siguiente partido
                                driver.get(url_atras)
                                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME , 'footable-loaded')))
                            except:
                                print("Algo fue mal en el partido: "+str(equipos)+ " "+ str(fecha))
                                print("Me salto este partido")


                                driver.get(url_atras)
                                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME , 'footable-loaded')))
                                pass

        # Cuando se acaba un torneo, se vuelve a la página inicial para el siguiente torneo
        driver.get(web+subdomain)

# Los datos extraídos se guardan en un csv
extracted_data.to_csv("Lol_ProfessionalGames.csv",index=False)
