from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from crawldata import Crawler
import os

class Crawl_matches:
    def __init__(self, driver):
        self.driver = driver 

def driver_initialize():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-proxy-server')
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

if __name__ == '__main__':
    url = input("Enter the url of the team matches from flashscore: ")
    # wisla_url = 'https://www.flashscore.com/team/wisla-plock/zPDZ2YnB/results/'
    # korona_url = 'https://www.flashscore.com/team/industria-kielce/C0B1zszf/results/'
    url_parts = url.split('/')
    team_name = url_parts[4]
    driver = driver_initialize()
    crawler = Crawler(driver)
    crawler.crawl_match_details(url, team_name)
    with open(f"{team_name}_links.txt", "r") as links_file:
            links = links_file.readlines()
    index = 0
    with open(f"{team_name}_analyze.txt", "w") as stat_file:
        for link in links:
            driver = driver_initialize()
            crawler = Crawler(driver)
            h1, h2 = crawler.handball_halfs_extraction(link, stat_file)
            
            driver.quit()
            try:
                winner =''
                maximum_ahead_1 = 0
                maximum_ahead_2 = 0
                driver = driver_initialize()
                crawler = Crawler(driver)
                winner, maximum_ahead_1 = crawler.point_by_point(h1, team_name)
                driver = driver_initialize()
                crawler = Crawler(driver)
                winner, maximum_ahead_2 = crawler.point_by_point(h2, team_name)
                max_ahead = max(maximum_ahead_2, maximum_ahead_1)
                if max_ahead == -1:
                    stat_file.write(f"{link} - {team_name} never had been overcame.")
                    stat_file.write('\n')
                elif 'draw' == winner:
                    stat_file.write(f"{link} - The match ended with a draw and {team_name} has been overcame with maximum {max_ahead} points.")
                    stat_file.write('\n')
                elif max_ahead > 0 and winner in team_name:
                    stat_file.write(f"{link} - {team_name} has had been overcame with maximum {max_ahead} points, but still won the game.")
                    stat_file.write('\n')
                elif max_ahead > 0 and winner not in team_name:
                    stat_file.write(f"{link} - {team_name} has had been overcame with maximum {max_ahead} points and lost the game.")
                    stat_file.write('\n')
            except:
                stat_file.write(f"{link} - Match doesn't have the stats repr. on halfs!")
                stat_file.write('\n')

            index += 1
            if index == 1:
                exit()
            