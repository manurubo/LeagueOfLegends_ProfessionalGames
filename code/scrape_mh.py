from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from functools import reduce
import pandas as pd



def get_dif_gold(driver):
    puntos = driver.find_element_by_css_selector("#timeline-graph-259").find_elements_by_css_selector("circle")
    tiempo = driver.find_element_by_css_selector(".map-header-duration").text
    minutos = int(tiempo.split(":")[0])
    diferencia_oro_azul = {}
    diferencia_oro_rojo = {}
    for i in range(5,minutos,5):
        hover= ActionChains(driver).move_to_element(puntos[i])
        hover.perform()
        diferencia_oro = driver.find_element_by_css_selector("#codex-tooltip-1").text
        equipo_ventaja = diferencia_oro.split(" ahead")[0]
        dif = diferencia_oro.split("by ")[1].split(" at")[0].replace("k",'')
        if '.' in dif:
            dif = float(dif)*1000
        dif=int(dif)
        if (equipo_ventaja == 'Blue'):
            diferencia_oro_azul[str(i)+' min']=dif
            diferencia_oro_rojo[str(i)+' min']=-dif
        elif(equipo_ventaja == 'Red'):
            diferencia_oro_azul[str(i)+' min']=-dif
            diferencia_oro_rojo[str(i)+' min']=dif
        else:
            diferencia_oro_azul[str(i)+' min']=0
            diferencia_oro_rojo[str(i)+' min']=0

    return(diferencia_oro_azul, diferencia_oro_rojo)



def get_gold_team(driver,color):
    tiempo = driver.find_element_by_css_selector(".map-header-duration").text
    minutos = int(tiempo.split(":")[0])
    if (color == 'azul'):
        puntos = driver.find_element_by_css_selector("#timeline-graph-260").find_elements_by_css_selector(".point.team-1")
    elif(color=='rojo'):
        puntos = driver.find_element_by_css_selector("#timeline-graph-260").find_elements_by_css_selector(".point.team-2")
    oro_equipo  = {}
    for i in range(5,minutos,5):
        hover= ActionChains(driver).move_to_element(puntos[i])
        hover.perform()

        oro = driver.find_element_by_css_selector("#codex-tooltip-1").text
        oro_equipo[str(i)+' min'] = int(float(oro.split(" at")[0].replace("k",""))*1000)

    return(oro_equipo)

def reset_players(driver):
    champs = driver.find_element_by_css_selector("#timeline-graph-261").find_elements_by_css_selector(".champion-portrait")
    for champ in champs:
        champ.click()

def get_gold_player(driver,player):
    tiempo = driver.find_element_by_css_selector(".map-header-duration").text
    minutos = int(tiempo.split(":")[0])
    champs = driver.find_element_by_css_selector("#timeline-graph-261").find_elements_by_css_selector(".champion-portrait")
    champ=champs[player]
    champ.click()
    puntos = driver.find_element_by_css_selector("#timeline-graph-261").find_elements_by_css_selector(".champion-gold-"+str(player))
    oro_player  = {}
    for i in range(5,minutos,5):
        hover= ActionChains(driver).move_to_element(puntos[i+1])
        hover.perform()

        oro = driver.find_element_by_css_selector("#codex-tooltip-1").text
        oro=oro.split(" at")[0].replace("k","")
        if '.' in oro:
            oro = float(oro)*1000
        oro=int(oro)
        oro_player[str(i)+' min'] = oro

    champ.click()
    return(oro_player)




def scrap_gold_graphs(driver):
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR , "svg.line-graph")))


        graphs=driver.find_element_by_xpath("//ul[@id='graph-switcher-262-menu']").find_elements_by_css_selector('a')
        i = 1

        for graph in graphs:
            driver.find_element_by_xpath("//a[@id='graph-switcher-262-toggle']").click()
        #     WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH , "//a[contains(text(),'Team Gold Advantage')]")))

            graph.click()
            if i == 1:
                diferencia_oro_azul, diferencia_oro_rojo = get_dif_gold(driver)
                i+=1
            elif( i == 2):
                oro_rojo =get_gold_team(driver,'rojo')
                oro_azul = {}
                for it in diferencia_oro_azul:
                    oro_azul[it] = oro_rojo[it]+round(diferencia_oro_azul[it],-2)

                i+=1
            elif( i == 3):
                reset_players(driver)
                gold_top_azul = get_gold_player(driver,0)
                gold_jng_azul = get_gold_player(driver,1)
                gold_mid_azul = get_gold_player(driver,2)
                gold_adc_azul = get_gold_player(driver,3)
                gold_sup_azul = get_gold_player(driver,4)
                gold_top_rojo = get_gold_player(driver,5)
                gold_jng_rojo = get_gold_player(driver,6)
                gold_mid_rojo = get_gold_player(driver,7)
                gold_adc_rojo = get_gold_player(driver,8)
                gold_sup_rojo = get_gold_player(driver,9)
        nombres = ["diferencia_oro_azul", "diferencia_oro_rojo","oro_azul","oro_rojo","gold_top_azul","gold_jng_azul","gold_mid_azul","gold_adc_azul","gold_sup_azul","gold_top_rojo","gold_jng_rojo","gold_mid_rojo","gold_adc_rojo","gold_sup_rojo"]
        atributos = [[diferencia_oro_azul, diferencia_oro_rojo, oro_azul,oro_rojo,gold_top_azul,gold_jng_azul,gold_mid_azul,gold_adc_azul,gold_sup_azul,gold_top_rojo,gold_jng_rojo,gold_mid_rojo,gold_adc_rojo,gold_sup_rojo]]
        results = pd.DataFrame(atributos, columns=nombres)
    except:
        nombres = ["diferencia_oro_azul", "diferencia_oro_rojo", "oro_rojo","oro_azul","gold_top_azul","gold_jng_azul","gold_mid_azul","gold_adc_azul","gold_sup_azul","gold_top_rojo","gold_jng_rojo","gold_mid_rojo","gold_adc_rojo","gold_sup_rojo"]
        atributos = [[None, None, None,None,None,None,None,None,None,None,None,None,None,None]]
        results = pd.DataFrame(atributos, columns=nombres)

    return (results)

def get_heralds_and_inhibitors(driver):
    try:
        heraldos = driver.find_elements_by_css_selector("div.rift-herald-kills")
        heraldos_azul = heraldos[0].text
        heraldos_rojo = heraldos[1].text

        inhibs = driver.find_elements_by_css_selector("div.inhibitor-kills")
        inhibs_azul = inhibs[0].text
        inhibs_rojo = inhibs[1].text
        nombres = ['heraldos_azul','heraldos_rojo', 'inhibs_azul', 'inhibs_rojo']
        atributos = [[heraldos_azul,heraldos_rojo, inhibs_azul, inhibs_rojo]]
        results = pd.DataFrame(atributos, columns=nombres)
    except:
        nombres = ['heraldos_azul','heraldos_rojo', 'inhibs_azul', 'inhibs_rojo']
        atributos = [[None,None, None, None]]
        results = pd.DataFrame(atributos, columns=nombres)
    return(results)

def get_fb(driver):
    try:
        fbs = driver.find_element_by_xpath(".//div[contains(text(),'First Blood') and @class='view']").find_element_by_xpath('../..').find_elements_by_css_selector("td")
        fbs = fbs[1:11]
        positions = ['top_azul', 'jng_azul', 'mid_azul','adc_azul','sup_azul','top_rojo', 'jng_rojo', 'mid_rojo','adc_rojo','sup_rojo']
        i=0
        for fb in fbs:
            if '●' in fb.text:
                first_blood = positions[i]
            i +=1
        nombres = ['First_Blood']
        atributos = [[first_blood]]
        results = pd.DataFrame(atributos, columns=nombres)
    except:
        nombres = ['First_Blood']
        atributos = [[None]]
        results = pd.DataFrame(atributos, columns=nombres)
    return(results)


def get_stat_mh(driver,var,name):
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR , "#stats-body")))
        var_top_azul = driver.find_element_by_xpath(".//div[contains(text(),'"+str(var)+"')]/../following-sibling::td")
        var_jng_azul = var_top_azul.find_element_by_xpath(".//following-sibling::td")
        var_mid_azul = var_jng_azul.find_element_by_xpath(".//following-sibling::td")
        var_adc_azul = var_mid_azul.find_element_by_xpath(".//following-sibling::td")
        var_sup_azul = var_adc_azul.find_element_by_xpath(".//following-sibling::td")
        var_top_rojo = var_sup_azul.find_element_by_xpath(".//following-sibling::td")
        var_jng_rojo = var_top_rojo.find_element_by_xpath(".//following-sibling::td")
        var_mid_rojo = var_jng_rojo.find_element_by_xpath(".//following-sibling::td")
        var_adc_rojo = var_mid_rojo.find_element_by_xpath(".//following-sibling::td")
        var_sup_rojo = var_adc_rojo.find_element_by_xpath(".//following-sibling::td")
        var_top_azul = var_top_azul.text.replace("k","")
        if '.' in var_top_azul:
            var_top_azul = float(var_top_azul)*1000
        var_top_azul = int(var_top_azul)
        var_jng_azul = var_jng_azul.text.replace("k","")
        if '.' in var_jng_azul:
            var_jng_azul = float(var_jng_azul)*1000
        var_jng_azul = int(var_jng_azul)
        var_mid_azul = var_mid_azul.text.replace("k","")
        if '.' in var_mid_azul:
            var_mid_azul = float(var_mid_azul)*1000
        var_mid_azul = int(var_mid_azul)
        var_adc_azul = var_adc_azul.text.replace("k","")
        if '.' in var_adc_azul:
            var_adc_azul = float(var_adc_azul)*1000
        var_adc_azul = int(var_adc_azul)
        var_sup_azul = var_sup_azul.text.replace("k","")
        if '.' in var_sup_azul:
            var_sup_azul = float(var_sup_azul)*1000
        var_sup_azul = int(var_sup_azul)
        var_top_rojo = var_top_rojo.text.replace("k","")
        if '.' in var_top_rojo:
            var_top_rojo = float(var_top_rojo)*1000
        var_top_rojo = int(var_top_rojo)
        var_jng_rojo = var_jng_rojo.text.replace("k","")
        if '.' in var_jng_rojo:
            var_jng_rojo = float(var_jng_rojo)*1000
        var_jng_rojo = int(var_jng_rojo)
        var_mid_rojo = var_mid_rojo.text.replace("k","")
        if '.' in var_mid_rojo:
            var_mid_rojo = float(var_mid_rojo)*1000
        var_mid_rojo = int(var_mid_rojo)
        var_adc_rojo = var_adc_rojo.text.replace("k","")
        if '.' in var_adc_rojo:
            var_adc_rojo = float(var_adc_rojo)*1000
        var_adc_rojo = int(var_adc_rojo)
        var_sup_rojo = var_sup_rojo.text.replace("k","")
        if '.' in var_sup_rojo:
            var_sup_rojo = float(var_sup_rojo)*1000
        var_sup_rojo = int(var_sup_rojo)
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

    return(results)


def get_stats_table_mh(driver):

    dfs=[get_heralds_and_inhibitors(driver),get_fb(driver),get_stat_mh(driver,'Total Damage Dealt', "Total_Damage_Dealt"), get_stat_mh(driver,'Physical Damage Dealt', "Physical_Damage_Dealt"),get_stat_mh(driver,'Magic Damage Dealt', "Magic_Damage_Dealt"),get_stat_mh(driver,'True Damage Dealt', "True_Damage_Dealt"),
    get_stat_mh(driver,'Total Damage to Objectives', "Total_Damage_Objectives"),get_stat_mh(driver,'Damage Taken', "Damage_Taken"),get_stat_mh(driver,'Physical Damage Taken', "Physical_Damage_Taken"),get_stat_mh(driver,'Magic Damage Taken', "Magic_Damage_Taken"),get_stat_mh(driver,'True Damage Taken', "True_Damage_Taken"),]
    df_final = reduce(lambda left,right: pd.merge(left,right, left_index=True, right_index=True), dfs)

    return (df_final)
