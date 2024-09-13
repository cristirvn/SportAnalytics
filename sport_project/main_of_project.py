from crawldata import main
from io import StringIO
import csv
import os
from models.matches import Matches
from models.championship_tasks import Tasks
from analyzedata import Analyzer
if __name__ == '__main__':

    sports = ['Football', 'Basketball']
    print(f"Choose the sport you want from the folowing list: {sports}")
    #sport = str(input())
    sport = 'Basketball'
    print("Type one from the folowing options:")
    print("Type 1 if you want the csv file with all the matches sorted")
    print("Type 2 if you want the leaderboard after a specific round")
    print("Type 3 if you want to see all matches a team had played till a certain round")
    print("type 4 if you want to see the times the first 3 teams had beaten the last 3 teams from a range of rounds")
    print("Type 5 if you want to analize the championship in order to see if it is favorable to bet on a top team")
    option = int(input())
    
    if option == 1:
        main(sport)
    elif option == 2:
        
        print("Type the round you want to see the leaderboard after: ")
        roundd = int(input())
        main(sport)
        folder_path = f"C:/Users/User/Desktop/workspace/win_lose_project/sport_project/championships/basketball/2023-2024"
            
        all_files = os.listdir(folder_path)
        csv_files = [file for file in all_files if file.endswith('.csv')]
        for output_file in csv_files:
            full_path = os.path.join(folder_path, output_file)  # Construct the full file path
            matches = Matches.read_matches_from_csv(full_path)
            matches_object = Tasks(matches)

            max_round =  matches_object.maximum_round()
            matches_object.leaderboard_after_input_round(roundd, sport, option)
        
    elif option == 3:
        
        main(sport)
        folder_path = f"C:/Users/User/Desktop/workspace/win_lose_project/sport_project/championships/basketball/2023-2024"
            
        all_files = os.listdir(folder_path)
        csv_files = [file for file in all_files if file.endswith('.csv')]
        for output_file in csv_files:
            full_path = os.path.join(folder_path, output_file)  # Construct the full file path
            matches = Matches.read_matches_from_csv(full_path)
            matches_object = Tasks(matches)

            temp = matches_object.leaderboard_after_input_round(1, sport, option)
            roundd = int(input("Choose the round till you want to see matches: "))
            team_to_find = str(input(f"Choose a team from folowing list you want to see the matches: \n{'\n'.join(temp.keys())}\n"))
            matches_object.matches_played_till_given_round(roundd, team_to_find)
    
    
    elif option == 4:
        print("If you want to test type 1")
        print("If you want to run the code on the site datafram type 2")
        option_2 = int(input("Enter the choice: "))

        if option_2 == 1:
            data = """Round,Home,Away,Home_score,Away_score,Date,Sport
ROUND 1,Team A,Team B,2,1,0f f, Football
ROUND 1,Team C,Team D,1,3,1f f, Football
ROUND 1,Team E,Team F,0,2,2f f, Football
 
ROUND 2,Team A,Team C,1,0,3f f, Football
ROUND 2,Team B,Team E,1,1,4f f, Football
ROUND 2,Team D,Team F,2,2,5f f, Football

ROUND 3,Team A,Team D,2,2,6f f, Football
ROUND 3,Team B,Team F,1,3,7f f, Football
ROUND 3,Team C,Team E,0,2,8f f, Football

ROUND 4,Team A,Team E,0,1,9f f, Football
ROUND 4,Team B,Team C,0,2,10f f, Football
ROUND 4,Team D,Team F,1,0,11f f, Football
                        """
            
            data_io = StringIO(data)
            reader = csv.reader(data_io)

            # Open a new CSV file to write to
            with open('test_matches.csv', 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write each row from the reader to the CSV file
                for row in reader:
                    writer.writerow(row)

            matches = Matches.read_matches_from_csv("test_matches.csv")
            # Define expected results
            # Define expected results
            expected_victories = 2
            expected_draws = 0
            expected_losses = 1

            # Run the test
            right = 2
            left = 4
            matches_object = Tasks(matches)
            victory, draws, loses = matches_object.firstn_vs_lastm(right, left, option_2, sport)

            # Print the results
            print(f"Victories: {victory}, Expected: {expected_victories}")
            print(f"Draws: {draws}, Expected: {expected_draws}")
            print(f"Losses: {loses}, Expected: {expected_losses}")

            # Validate the results
            assert victory == expected_victories, f"Expected {expected_victories} victories but got {victory}"
            assert draws == expected_draws, f"Expected {expected_draws} draws but got {draws}"
            assert loses == expected_losses, f"Expected {expected_losses} losses but got {loses}"
        else:
            
            left, right = map(int,input("Type the range you want to see: ").split())
            main(sport)

            #problema la link!!!!!!!    
            folder_path = f"C:/Users/User/Desktop/workspace/win_lose_project/sport_project/championships/basketball/2023-2024"
            
            all_files = os.listdir(folder_path)
            csv_files = [file for file in all_files if file.endswith('.csv')]
            for output_file in csv_files:
                full_path = os.path.join(folder_path, output_file)  # Construct the full file path

                matches = Matches.read_matches_from_csv(full_path)
                matches_object = Tasks(matches)

                max_round =  matches_object.maximum_round()
                if left == 1 or right > max_round:
                    print(f"Right must be greater than 1 and left smaller than {max_round}!")
                else:
                    matches_object.firstn_vs_lastm(8, max_round, option_2, sport)
    else:
        folder_path = f"C:/Users/User/Desktop/workspace/win_lose_project/sport_project/championships/basketball/2023-2024"
        
        all_files = os.listdir(folder_path)
    
        csv_files = [file for file in all_files if file.endswith('.csv')]
        for output_file in csv_files:
            full_path = os.path.join(folder_path, output_file)  # Construct the full file path

            matches = Matches.read_matches_from_csv(full_path)

            analize_object = Analyzer(matches, sport)
            #check if it is favorable betting on a top team
            analize_object.favorable_teams_betting()
            '''
            
            1.ne gandim la designul aplicatiei dpdv al obiectelor din spate
            1.1. fisiere de configurare

            2. rafinam crawlerul definim fctii 
            3. optimizam timp
            4. cum salvam meciurile csv sau postgreSQL + modelarea bazei de date
            5. niste teste pt fiecare metoda apelata + rezultate
            6. creem analyerzul + definit functii pe el
            7. front end
            '''