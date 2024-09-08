from dataclasses import dataclass
import pandas as pd
import csv
from datetime import datetime
from models.championship_tasks import Tasks
@dataclass
#TODO sterge meciul
class Matches:
    ROUND: str
    date: str
    home: str
    away: str
    home_score: int
    away_score: int
    #add_sports : list
    sport : str
    #stage : str
    url : str
    def __repr__(self):
        return f"{self.ROUND}, {self.date}, {self.home}, {self.away}, {self.home_score}, {self.away_score}, {self.sport}, {self.url}"
    
    # def adding(self):
    #     add_matches = []
    #     add_matches.append([self.ROUND, self.date, self.home, self.away, self.home_score, self.away_score])
    #     self.add_sports.append([self.ROUND, self.date, self.home, self.away, self.home_score, self.away_score])

    #     return add_matches
    

    # def out_list(self):
    #     return self.add_sports
    
    def read_matches_from_csv(file_path: str):
        matches = []

        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                match = Matches(
                    ROUND=row['Round'],
                    home=row['Home'],
                    away=row['Away'],
                    home_score=row['Home_score'],
                    away_score=row['Away_score'],
                    date=row['Date'],
                    sport = row['Sport'],
                    url = row['Url']
                )
                matches.append(match)

        return matches
    
    @staticmethod
    def sort_matches_by_date(file_path: str):
        df = pd.read_csv(file_path)

        
        df['Date'] = pd.to_datetime(df['Date'], format='%d %m %Y  %H:%M')

    # Step 2: sort values by date
        df = df.sort_values(by='Date')
    # Step 3: Write the reversed DataFrame to a new CSV file
        df.to_csv(file_path, index=False)

@dataclass
class Validator:
    csv_file : str

    def validate(self):
        with open("errors_found.txt", 'w') as file:

            matches = Matches.read_matches_from_csv(self.csv_file)

            self.check_for_incomplete_rounds(matches, file)
            self.check_data_structure(matches, file)
            self.check_missing_rounds(matches, file)

    def check_for_incomplete_rounds(self, matches: list, file):
        rounds_dict = {}
        maximum_match_per_round = 0
        for match in matches:
            if 'ROUND' in match.ROUND:
                if match.ROUND not in rounds_dict:
                    rounds_dict[match.ROUND] = 1
                else:
                    rounds_dict[match.ROUND] += 1
                    if rounds_dict[match.ROUND] > maximum_match_per_round:
                        maximum_match_per_round = rounds_dict[match.ROUND]
        error_rounds = []
        for key, value in rounds_dict.items():
            if value != maximum_match_per_round:
                error_rounds.append(f"{key} : {value}")
        
        if len(error_rounds):
            print(f"The {self.csv_file} has incomplete rounds: {', '.join(error_rounds)}", file=file)
        

    def check_data_structure(self, matches: list, file):
        round_count = {}
        for match in matches:
            if match.ROUND not in round_count:
                round_count[match.ROUND] = 1
        
        if "FINAL" not in round_count:
            print(f"{self.csv_file} does not have a structure! The final is missing!", file=file)
        elif "SEMI-FINALS" not in round_count:
            print(f"{self.csv_file} does not have a structure! The semi-finals are missing!", file=file)
        elif "ROUND" not in round_count:
            print(f"{self.csv_file} does not have a structure! The rounds are missing!", file=file)


    def check_missing_rounds(self, matches: list, file):
        matches_object = Tasks(matches)
        max_round = matches_object.maximum_round( )
        rounds = {}
        for index in range(1, max_round + 1):
            rounds[f"ROUND {index}"] = 0

        for match in matches:
            if "ROUND" in match.ROUND:
                rounds[match.ROUND] = 1
        
        missing_rounds = []
        for key, value in rounds.items():
            if value == 0:  
                missing_rounds.append(key)
        
        if len(missing_rounds):
            missing_rounds_2 = ', '.join(missing_rounds)
            print(f"{self.csv_file} has missing rounds : {missing_rounds_2}", file=file)
            

    
