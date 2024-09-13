from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import os
import csv
from models.matches import Matches, Validator

class Crawler:
    def __init__(self, driver):
        self.driver = driver
    def quit(self):
        self.driver.quit()
        
    def crawl_data_tag_by_tag_selenium(self, url, sport, option):

        self.driver.get(url)
        wait = WebDriverWait(self.driver, 3)
        while True:
            try:
                # Wait for the "Show More" button to be clickable
                button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".event__more")))

                # Scroll the button into view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                
                # Click the "Show More" button using JavaScript if necessary
                self.driver.execute_script("arguments[0].click();", button)

                time.sleep(1)  # Adjust sleep time based on how quickly content loads

            except:
                break
        
        
        elements = self.driver.find_element(By.CSS_SELECTOR, '.sportName')
        rounds = elements.find_elements(By.CSS_SELECTOR, '.event__round')
        runda_maxima = 0
        for round in rounds:
            temp = round.text.split(' ')
            try:
                runda_maxima = max(runda_maxima, int(temp[1]))
            except:
                pass

        matches = elements.find_elements(By.TAG_NAME, 'div')

        ok = 0
        class_atributts = 'event__round'
        all_elements = []
        for match in matches:
            class_atributte = match.get_attribute('class')

            try:
                if ok == 0:
                    if class_atributts in class_atributte.split():
                        if str(runda_maxima) in match.text:
                            ok = 1
            except:
                pass


            if ok == 1:
                class_1 = 'event__round'
                class_2 = 'event__match'
                if class_1 in class_atributte:
                    round_number = match.text.strip().split(' ')
                    
                else:
                    try:
                        if sport == 'Basketball':
                            home_team = match.find_element(By.CSS_SELECTOR, '.event__participant--home').text
                            away_team = match.find_element(By.CSS_SELECTOR, '.event__participant--away').text
                        else:
                            home_team = match.find_element(By.CSS_SELECTOR, '.event__homeParticipant').find_element(By.CSS_SELECTOR, '._simpleText_zkkvt_4').text
                            away_team = match.find_element(By.CSS_SELECTOR, '.event__awayParticipant').find_element(By.CSS_SELECTOR, '._simpleText_zkkvt_4').text
                        away_score = match.find_element(By.CSS_SELECTOR, '.event__score--away').text
                        home_score = match.find_element(By.CSS_SELECTOR, '.event__score--home').text
                        date = match.find_element(By.CSS_SELECTOR, '.event__time').text
                        all_elements.append([
                            int(round_number[1]), home_team, away_team, home_score, away_score, date
                        ])
                    except:
                        pass

        column = ['Round', 'Home', 'Away', 'Home_score', 'Away_score', 'Date']
        df = pd.DataFrame(all_elements, columns = column)

        df['Date'] = pd.to_datetime(df['Date'], format='%d.%m. %H:%M', errors="coerce")

        # Sort the DataFrame by 'Round' and 'Date'
        df = df.sort_values(by=['Round', 'Date'])

        # If you need to remove '1900-' part and it was only a display format issue, 
        # it's usually not necessary if your DataFrame is properly sorted.
        # Here you may want to format the 'Date' column back to string if needed.
        # Example to format 'Date' column back to a specific string format:
        df['Date'] = df['Date'].dt.strftime('%d.%m. %H:%M')

        df.to_csv('matches_results.csv', index=False)

    
        self.driver.quit()

        return df


    def add_date(temp_data, year):
        temp_data[1] = temp_data[1] +' '+ year
        return ' '.join(temp_data)

    def get_urls(self):
        elems = self.driver.find_elements(By.CSS_SELECTOR, '.event__match')
        urls = []
        for elem in elems:
            try:
                temp_url = elem.find_element(By.CSS_SELECTOR, '.eventRowLink').get_attribute('href')
                urls.append(temp_url)
            except:
                pass
        
       
        return urls
    def crawl_data_by_text_selenium(self, url, output_file, sport, temp_years):
        #if not os.path.exists(output_file):
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 3)
            
            while True:
                try:
                    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".event__more")))
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(1)
                except:     
                    break
            urls = Crawler.get_urls(self)
            url_index = 0

            table = self.driver.find_element(By.CSS_SELECTOR, '.sportName')
            table_text = table.text
            with open("matches.txt", "w") as file:
                file.write(table_text)

            with open("matches.txt", "r") as file:
                lines = file.readlines()

            current_date = ""
            home_team = ""
            away_team = ""
            home_score = ""
            away_score = ""
            ROUND = ""
            #stage = ""
            anterior_month = ""
            def is_integer(s):
                try:
                    int(s)
                    return True
                except ValueError:
                    return False

            with open(output_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Round', 'Home', 'Away', 'Home_score', 'Away_score', 'Date', 'Sport', 'Url'])
                for line in lines:
                    line = line.strip()
                    # if name in line.lower():
                    #     stage = line
                    
                    if 'ROUND' in line and ROUND != line:
                        if current_date and home_team and away_team and home_score and away_score:
                            away_score = int(away_score)
                            home_score = int(home_score)
                            if anterior_month != '12':
                                temp_date = current_date.split('.')
                                #getting the anterior month for each match
                                anterior_month = temp_date[1]

                            try:
                                if current_date:
                                    temp_date = current_date.split('.')
                                    if anterior_month == '12':
                                        current_date = Crawler.add_date(temp_date, temp_years[0])
                                    elif int(anterior_month) <= 12:
                                        current_date = Crawler.add_date(temp_date, temp_years[1])

                                    

                            except:
                                pass
                            match = [ROUND, home_team, away_team, home_score, away_score, current_date, sport, urls[url_index]]
                            url_index += 1
                            writer.writerow(match)
                            
                        
                        home_team = ""
                        away_team = ""
                        home_score = ""
                        away_score = ""
                        current_date = ""

                    if "ROUND" in line:
                        ROUND = line
                    elif "FINAL" in line:
                        ROUND = line
                    elif "SEMI-FINALS" in line or "QUARTER-FINALS" in line or "PLACE" in line or "Group" in line or "Relegation" in line:
                        ROUND = line
                    
                    if "AOT" in line:
                        continue
                    if ":" in line:

                        if current_date and home_team and away_team and home_score and away_score:
                            away_score = int(away_score)
                            home_score = int(home_score)
                            if anterior_month != '12':
                                temp_date = current_date.split('.')
                                #getting the anterior month for each match
                                anterior_month = temp_date[1]

                            try:
                                 if current_date:
                                    temp_date = current_date.split('.')
                                    if anterior_month == '12':
                                        current_date = Crawler.add_date(temp_date, temp_years[0])
                                    elif int(anterior_month) <= 12:
                                        current_date = Crawler.add_date(temp_date, temp_years[1])
                                    

                            except:
                                pass
                            match = [ROUND, home_team, away_team, home_score, away_score, current_date, sport, urls[url_index]]
                            url_index += 1
                            writer.writerow(match)
                        
                        current_date = ""
                        home_team = ""
                        away_team = ""
                        home_score = ""
                        away_score = ""
                        current_date = line

                    elif isinstance(line, str) and home_team == "":
                        home_team = line
                    elif isinstance(line, str) and away_team == "":
                        away_team = line
                    elif is_integer(line) and home_score == "":
                        home_score = line
                    elif home_score and away_score == "":
                        away_score = line
                    else:
                        pass
                temp_date = current_date.split('.')
                current_date = Crawler.add_date(temp_date, temp_years[0])
                match = [ROUND, home_team, away_team, home_score, away_score, current_date, sport, urls[-1]]
                writer.writerow(match)
    def check_element_existence(self):
        try:
            crawled_matches = self.driver.find_elements(By.CLASS_NAME, 'event__match')
            for match in crawled_matches:
                date = match.find_element(By.CLASS_NAME, 'event__time')
                if '2019' in date.text:
                    return True
        except:
            return False
    def close_cookie_banner(self):
        try:
            # Wait for the cookie banner to be present and close it
            cookie_banner = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))  # Example ID for "Accept Cookies"
            )
            cookie_banner.click()
            time.sleep(1)  # Wait for the banner to close
        except:
            pass            
    def point_by_point(self, h, team):
        self.driver.get(h)
        table = self.driver.find_element(By.CLASS_NAME, 'matchHistoryRowWrapper')
        rows = table.find_elements(By.CLASS_NAME, 'matchHistoryRow')
        home_team = self.driver.find_element(By.CLASS_NAME, 'duelParticipant__home').text
        away_team = self.driver.find_element(By.CLASS_NAME, 'duelParticipant__away').text
        try:
            winner = self.driver.find_element(By.CLASS_NAME, 'duelParticipant--winner').text
        except:
            winner = 'draw'
        home = home_team.lower().split(' ')
        team_split_name = team.split('-')
        if winner == 'draw':
            winner_team = 'draw'
        else:
            winner = winner.lower().split(' ')
            winner_team = winner[0]
        maximum_ahead = -1
        if team_split_name[0] == home[0]:
                for row in rows:
                    score = row.find_element(By.CLASS_NAME, 'matchHistoryRow__scoreBox')
                    scores = score.find_elements(By.CLASS_NAME, 'matchHistoryRow__score')
                    
                    if int(scores[1].text) - int(scores[0].text) >= 0:
                        maximum_ahead = max(maximum_ahead, int(scores[1].text) - int(scores[0].text))
            
        else:
                for row in rows:
                    score = row.find_element(By.CLASS_NAME, 'matchHistoryRow__scoreBox')
                    scores = score.find_elements(By.CLASS_NAME, 'matchHistoryRow__score')
                    if int(scores[0].text) - int(scores[1].text) > 0:
                        maximum_ahead = max(maximum_ahead, int(scores[0].text) - int(scores[1].text))

        self.driver.quit()
        return winner_team, maximum_ahead
    def handball_halfs_extraction(self, url, stat_file):
        self.driver.get(url)
        try:
            button = self.driver.find_element(By.CSS_SELECTOR, 'div.filterOver div[role="tablist"]')
            half_link = button.find_elements(By.TAG_NAME, 'a')
            button = half_link[2]
    
            button.click()
            time.sleep(1)
            halfs = self.driver.find_element(By.CSS_SELECTOR, 'div.subFilterOver div[role="tablist"]')
            halfs = halfs.find_elements(By.TAG_NAME, 'a')
            h1 = halfs[0].get_attribute('href')
            h2 = halfs[1].get_attribute('href')
            return h1, h2
            
        except:
            stat_file.write(f"{url} - Match doesn't have point by point stats.")
            stat_file.write('\n')
            return None, None
            
    def crawl_match_details(self, url, team):
        if not os.path.exists(f"{team}_links.txt"):
            self.driver.get(url)
            self.close_cookie_banner()
            button = self.driver.find_element(By.ID, 'main')
            while not self.check_element_existence():
                time.sleep(1)
                
                but_2 = WebDriverWait(button, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'span._caption_ruui3_4'))).click()                
                time.sleep(1)
            matches = self.driver.find_elements(By.CLASS_NAME, 'event__match')
            with open(f"{team}_links.txt", "w") as links_file:
                wins = 0
                for match in matches:
                    date = match.find_element(By.CLASS_NAME, 'event__time')
                    if '2019' in date.text:
                        links_file.write(f"Wins for {team} from 2020-2024 : {wins}")
                        break
                    link = match.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    win_or_lose = match.find_element(By.TAG_NAME, 'button')
                    if 'W' in win_or_lose.text:
                        wins += 1

                    links_file.write(link)
                    links_file.write('\n')
                    
            
            self.driver.quit()   
    

def main(sport):

    base_output_path = "C:/Users/User/Desktop/workspace/win_lose_project/sport_project"
    championships_path = os.path.join(base_output_path, 'championships')
    os.makedirs(championships_path, exist_ok=True)

    next_path = "C:/Users/User/Desktop/workspace/win_lose_project/sport_project/championships"
    sport_path = os.path.join(next_path, f"{sport}")
    os.makedirs(sport_path, exist_ok= True)

    if not os.path.exists("leagues.txt") or not os.path.exists("interest_seasons.txt"):
        raise FileNotFoundError("Error: leagues.txt or interest_seasons.txt file not found.")
        
    with open("leagues.txt", 'r') as lf, open("interest_seasons.txt", 'r') as sf:
        leagues = [line.strip() for line in lf]
        seasons = [line.strip() for line in sf]
    

    for season in seasons:

        #creating the folders for each season
        next_path = f"C:/Users/User/Desktop/workspace/win_lose_project/sport_project/championships/{sport}"
        season_path = os.path.join(next_path, f"{season}")
        os.makedirs(season_path, exist_ok=True)
        next_path = f"C:/Users/User/Desktop/workspace/win_lose_project/sport_project/championships/{sport}/{season}"
        
        #getting the years of the championship
        temp_years = season.split('-')
        
        for league in leagues:
            sport_name = sport.lower()
            #each stage for rounds/championship

            league_name_safe = league.replace('/', '_').replace('\\', '_')  # Replacing slashes if necessary
            # championship_name = league.strip().split('/')
            # full_name = re.split(r"[\/\.,,'\[\]\-]", championship_name[1])
            # full_name = ' '.join(full_name)

            #crawling each championship from leagues list
            output_file = os.path.join(next_path, f"{league_name_safe}.csv")
            
            if not os.path.exists(output_file):
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                crawler = Crawler(driver)

                url = f"https://www.flashscore.com/{sport_name}/{league}-{season}/results/"
                crawler.crawl_data_by_text_selenium(url, output_file, sport, temp_years)
                crawler.quit()
                
                Matches.sort_matches_by_date(output_file)
            validator = Validator(output_file)
            validator.validate()

    print(f"All csv fils have been successfully created.")

if __name__ == "__main__":
    main()
