from dataclasses import dataclass
from selenium import webdriver
from models.championship_tasks import Tasks
import numpy as np
from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from models.matches import Matches

@dataclass
class Analyzer:
    matches : List[Matches]
    sport : str
    def find_stabilization_round(self):
        teams = {}
        index = 1
        for match in self.matches:
            if match.home not in teams:
                teams[match.home] = {'points': 0, 'games': 0, 'goal_diff': 0, 'rank' : index }
                index += 1
            if match.away not in teams:
                teams[match.away] = {'points': 0, 'games': 0, 'goal_diff': 0, 'rank' : index}
                index += 1


        index = 1
        stability_score = {}
        for match in self.matches:
            if "ROUND" in match.ROUND:
                temp = match.ROUND.split(' ')
                if index != int(temp[1]):
                    sorted_teams = sorted(teams.items(), key = lambda x: (-x[1]['points'], -x[1]['goal_diff'], x[0]))
                    
                    top_3_ranks = [sorted_teams[i][1]['rank'] for i in range(min(3, len(sorted_teams)))]

                    
                    #calculate rank volatility or standard deviation
                    if len(top_3_ranks) > 1:  # Standard deviation calculation requires at least two data points
                        standard_deviation = np.std(top_3_ranks)
                    else:
                        standard_deviation = float('nan')  # Not enough data to calculate standard deviation
                    
                    stability_score[index] = standard_deviation
                    index = int(temp[1])

                

                teams[match.home]['games'] += 1
                teams[match.away]['games'] += 1
                teams[match.home]['goal_diff'] += (int(match.home_score) - int(match.away_score))
                teams[match.away]['goal_diff'] += (int(match.away_score) - int(match.home_score))
                
                if match.home_score > match.away_score:
                    teams[match.home]['points'] += 2
                else:
                    teams[match.away]['points'] += 2

        sorted_teams = sorted(teams.items(), key = lambda x: (-x[1]['points']/x[1]['games'], x[1]['goal_diff'], x[0]))
                    
        top_3_ranks = [sorted_teams[i][1]['rank'] for i in range(min(3, len(sorted_teams)))]

                    
                    #calculate rank volatility or standard deviation
        if len(top_3_ranks) > 1:  # Standard deviation calculation requires at least two data points
            standard_deviation = np.std(top_3_ranks)
        else:
            standard_deviation = float('nan')  # Not enough data to calculate standard deviation
                    
            stability_score[index] = standard_deviation

        
        sorted_teams = sorted(teams.items(), key = lambda x: (-x[1]['points'], x[1]['goal_diff'], x[0]))
                    
        top_3_ranks = [sorted_teams[i][1]['rank'] for i in range(min(3, len(sorted_teams)))]

        
        #calculate rank volatility or standard deviation
        if len(top_3_ranks) > 1:  # Standard deviation calculation requires at least two data points
            standard_deviation = np.std(top_3_ranks)
        else:
            standard_deviation = float('nan')  # Not enough data to calculate standard deviation
        
        stability_score[index] = standard_deviation

        #store the deviations in a list of floats
        deviations = [float(value) for value in stability_score.values()]
        round_query = []
        temp1 = 0
        temp2 = 0
        for item in deviations:
            temp1 = item
            if temp1 and temp2:
                round_query.append(abs(temp1 - temp2))
            temp2 = item

        # Step 2: Determine a threshold for "approximately constant"
        epsilon = 0.01

        # Step 3: Identify linear segments
        linear_segments = []
        current_segment = [0]  # Start with the first index

        for i in range(1, len(round_query)):
            if abs(round_query[i] - round_query[i-1]) <= epsilon:
                current_segment.append(i)
            else:
                if len(current_segment) > 1:  # A segment needs at least 2 points
                    linear_segments.append(current_segment)
                current_segment = [i]  # Start a new segment

        # Don't forget to add the last segment if it was linear
        if len(current_segment) > 1:
            linear_segments.append(current_segment)

        best_round = 0
        best_difference = 0
        for segment in linear_segments:
    
            if len(segment)> best_difference:
                best_difference = len(segment)
                best_round = segment[0]

        return best_round 
    
    def favorable_teams_betting(self):
        
        #stabilization_round = self.find_stabilization_round()
        stabilization_round = 11
        tasks = Tasks(self.matches)
        maximum_round = tasks.maximum_round()

        for roundd in range(stabilization_round + 1, maximum_round + 1):
            teams = tasks.leaderboard_after_input_round(roundd - 1, self.sport, 0)
            #getting the first n teams to bet on
            teams = teams[:3]

            matches_played = []
            #variable to stop iteration after getting matches from the curent round
            ok = 0
            for match in self.matches:
                if str(roundd) in match.ROUND:
                    ok = 1
                    if match.home in teams or match.away in teams:
                        matches_played.append(match)

                elif ok == 1:
                    break
            analyze_match(matches_played)
            break

def analyze_match(matches_played: list):
    """this function tells if a bet is good on favorable team or not, 
    if it isn't good, it will return where the match has been lost

    Args:
        matches_played (list): list with the matches of top n teams
    """
    for match in matches_played:
        #crawl_data_per_match(match)
        point_by_point_analyze(match)
        
        break

def analyze_pbp_quarter(match, q):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(q)
    points = driver.find_element(By.TAG_NAME, 'body')
    points_2 = points.find_element(By.CSS_SELECTOR, 'div.container__detail div.container__detailInner div.matchHistoryRowWrapper')
    new_point = points_2.find_elements(By.CLASS_NAME, 'matchHistoryRow')
    points_ahead_home = []
    points_ahead_away = []
    #using to check the score for a comeback
    for point in new_point:
        # home_ahead = point.find_element(By.CLASS_NAME, 'matchHistoryRow__home')
        # away_ahead = point.find_element(By.CLASS_NAME, 'matchHistoryRow__away')
        score = point.find_element(By.CLASS_NAME, 'matchHistoryRow__scoreBox ')
        scores = score.find_elements(By.CLASS_NAME, 'matchHistoryRow__score ')
        home_score = scores[0]
        away_score = scores[1]
        home_score = int(home_score.text)
        away_score = int(away_score.text)
        if home_score > away_score:
            difference = home_score - away_score
            
            points_ahead_home.append(difference)    
            
            
        elif away_score > home_score:
            difference = away_score - home_score
            
            points_ahead_away.append(difference)

    driver.quit()

    if match.home_score > match.away_score:
        if len(points_ahead_home):
            maximum_ahead = max(points_ahead_home)
            minimum_ahead = min(points_ahead_home)

            return maximum_ahead, minimum_ahead
        else:
            return 1, 1
        
    else:
        if len(points_ahead_away):
            maximum_ahead = max(points_ahead_away)
            minimum_ahead = min(points_ahead_away)
            return maximum_ahead, minimum_ahead
        else:
            return 1, 1
        
            

def point_by_point_analyze(match):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    # match.url = "https://www.flashscore.com/match/bNESX057/#/match-summary"
    
    # match.home = 'Valencia'
    # match.away = 'Real Madrid'
    # match.home_score = 99
    # match.away_score = 93
    driver.get(match.url)
    button = driver.find_element(By.TAG_NAME, 'body')
    button = button.find_element(By.CSS_SELECTOR, 'div.container__detail div.container__detailInner div.filterOver div[role="tablist"]')
    link_array = button.find_elements(By.TAG_NAME, 'a')
    button = link_array[4]
    
    button.click()
    time.sleep(2)
    button = driver.find_element(By.TAG_NAME, 'body')

    quarters = button.find_elements(By.CSS_SELECTOR, 'div.container__detail div.container__detailInner div.subFilterOver div[role="tablist"] a')
    quarter_urls = []
    for link in quarters:
        quarter_urls.append(link.get_attribute('href'))

    driver.quit()


    quarter_urls.reverse()
    maximum_differences = {}
    quart = 1
    for q in quarter_urls:
        dif_max, dif_min = analyze_pbp_quarter(match, q)
        maximum_differences[quart] = [dif_min, dif_max]
        quart += 1
    # for key, value in maximum_differences.items():
    #     print(f"{key} - {value}")
    procent = []
    procent.append(0)
   
    for key in maximum_differences:
        procent.append(float(100 - maximum_differences[key][0] / maximum_differences[key][1] * 100))
    # print(procent)
    quarter_where_match_is_lost = 0
    max_procent = 0
    index = 0
    for item in procent:
        if item > max_procent:
            max_procent = item
            quarter_where_match_is_lost = 4 - index + 1
        index += 1
    
    print(f"The match was lost in quarter {quarter_where_match_is_lost}, with a difference between lowest and highest points of {max_procent}%.")




def get_quarters_link(driver):
    link = driver.find_element(By.TAG_NAME, 'body')
    links = link.find_elements(By.CSS_SELECTOR, 'div.container__detail div.container__detailInner div.subFilterOver div[role="tablist"] a')
    quarters = []
    for link in links:
        quarters.append(link.get_attribute('href'))

    del quarters[0]

    return quarters

def analyze_by_scoring(team_a, team_b, match, file, q, metrics_home, metrics_away):
    total_score_team_a = 2 * team_a[3] + 3 * team_a[5] + team_a[7]
    total_score_team_b = 2 * team_b[3] + 3 * team_b[5] + team_b[7]
    temp = team_a[2:]
    #updating the metrics 
    for metric in range(0, len(temp)):
        metrics_home[metric] += temp[metric]

    temp = team_b[2:]
    for metric in range(0, len(temp)):
        metrics_away[metric] += temp[metric]

   
    match.home_score += total_score_team_a
    match.away_score += total_score_team_b

    if match.home_score > match.away_score:
        file.write(f"{match.home} is ahead with {match.home_score - match.away_score} points in quarter {q}.")
        file.write('\n')

        remaining_2p = metrics_away[0] - metrics_away[1]
        remaining_3p = metrics_away[2] - metrics_away[3]
        remaining_ft = metrics_away[4] - metrics_away[5]
        potential_points = remaining_2p * 2 + remaining_3p * 3 + remaining_ft
        if match.away_score + potential_points < match.home_score:
            file.write(f"Match is lost for {match.away} in quarter {q}")
            file.write('\n')

            

    else:
        file.write(f"{match.away} is ahead with {match.away_score - match.home_score} points in quarter {q}.")
        file.write('\n')

        remaining_2p = metrics_home[0] - metrics_home[1]
        remaining_3p = metrics_home[2] - metrics_home[3]
        remaining_ft = metrics_home[4] - metrics_home[5]
        potential_points = remaining_2p * 2 + remaining_3p * 3 + remaining_ft
        if match.home_score + potential_points < match.away_score:
            file.write(f"Match is lost for {match.home} in quarter {q}")
            file.write('\n')

            

def analyze_by_rebounds(team_a, team_b, match, file, q):
    if team_a[2] > team_b[2]:
        procent = float(team_b[2] / team_a[2] * 100)
        if procent > 50:
            file.write(f"Team {match.away} is more likey to lose in quarter {q}")
            file.write('\n')

            
        else:
            file.write(f"Team {match.home} is having a better movement with a rebound {procent} higher than {match.home} in quarter{q}")
            file.write('\n')

    elif team_a[2] < team_b[2]:
        procent = float(team_a[2] / team_b[2] * 100)
        if procent > 50:
            file.write(f"Team {match.home} is more likey to lose in quarter {q}")
            file.write('\n')

            
        else:
            file.write(f"Team {match.away} is having a better movement with a rebound {procent} higher than {match.away} in quarter{q}")
            file.write('\n')

    else:
        file.write(f"Both teams have equal % in rebounds in quarter {q}")
        file.write('\n')


def analyze_by_other_metrics(team_a, team_b, match, file, q):
    """this function analyze the match by other metrics like assists, blocks etc

    Args:
        team_a (list): home team
        team_b (list): away team
        match (str): the match final results
        file(str) : file with the analise of the match
    """

    #which one has the metrics higher
    a = 0
    b = 0
    for i in range(0, len(team_a)):
        if team_a[i] > team_b[i]:
            a += 1
        elif team_b[i] > team_a[i]:
            b += 1
        else:
            a += 1
            b += 1

    if a > b:
        file.write(f"Team {match.home} has a better controll over the game in quarter {q}")
        file.write('\n')

    else:
        file.write(f"Team {match.away} has a better controll over the game in quarter {q}")
        file.write('\n')


def analyze_per_quarter(match, stats, file, q):
    home_team =[]
    away_team =[]
    index = 0
    for stat in stats:
        if index % 2 == 0:
            home_team.append(int(stat))
        else:
            away_team.append(int(stat))
        
        index += 1
    #what represents the elements stored in home_team and away_team lists:
    #'FGA' 'FGM' '2PA' '2PM' '3PA' '3PM' 'FTA'  'FTM' 'Rebounds' 'AST' 'BLK' 'STL' 'TO' 

    #reseting the score to 0 for both
    match.home_score = 0
    match.away_score = 0
    #store the '2PA' '2PM' '3PA' '3PM' 'FTA'  'FTM' for updating mid game
    metric_home = [0,0,0,0,0,0]
    metrics_away = [0,0,0,0,0,0]

    analyze_by_scoring(home_team[:8], away_team[:8], match, file, q, metric_home, metrics_away)
    analyze_by_rebounds(home_team[8:11], away_team[8:11], match, file, q)
    analyze_by_other_metrics(home_team[11:], away_team[11:], match, file, q)
    
def crawl_data_per_match(match):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(match.url)
    time.sleep(2)
    button = driver.find_element(By.TAG_NAME, 'body')
    button_list = button.find_elements(By.CSS_SELECTOR, 'div.container__detail div.container__detailInner div.filterOver div[role="tablist"] a')    
    button_list[2].click()
    time.sleep(2)
    quarter_links = get_quarters_link(driver)
    
    driver.quit()
    q = 1
    with open("match_analize.txt", "w") as file:
        for quarter in quarter_links:

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.get(quarter)

            #getting sections with the metrics
            sections = driver.find_elements(By.CLASS_NAME, 'section')
            #retrieving the metrics
            with open("match_stats.txt", "w") as match_stats:
                for section in sections:
                    match_stats.write(section.text)
                    match_stats.write('\n')
            with open("match_stats.txt", "r") as match_stats:
                lines = match_stats.readlines()
            stats = []
            key_words = ['Made', 'Attempted', '%', 'SCORING', 'OTHER', 'REBOUNDS', 'Rebounds', 'Assists', 'Blocks', 'Turnovers', 'Steals', 'Fouls']

            for line in lines:
                line = line.strip()
                if any(keyword in line for keyword in key_words):
                    pass
                else:
                    stats.append(line)
            index = 0
            for stat in stats:
                if 'PRE' in stat:
                    break
                index += 1

            stats = stats[:index]
            analyze_per_quarter(match, stats,file, q)
        
            driver.quit()
            q += 1
            

