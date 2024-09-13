from dataclasses import dataclass

@dataclass
class Tasks: 
    matches : list
    

    def goal_average(self):
        dict_with_teams = {}

        for match in self.matches:
            if match.home not in dict_with_teams:
                dict_with_teams[match.home] = [0, 0]
            elif match.away not in dict_with_teams:
                dict_with_teams[match.away] = [0, 0]
    
        #dict_with_teams[][0] -> goals done
        #dict_with_teams[][1] -> goals got

        for match in self.matches:
            dict_with_teams[match.home][0] += int(match.home_score)
            dict_with_teams[match.home][1] += int(match.away_score)
            dict_with_teams[match.away][0] += int(match.away_score)
            dict_with_teams[match.away][1] += int(match.home_score)

        dict_of_goal_average = {}
        for key in dict_with_teams:
            dict_of_goal_average[key] = dict_with_teams[key][0] - dict_with_teams[key][1]

        return dict_of_goal_average
    
    def total_goals_per_team(self):
        total_goal_dict = {}
        for match in self.matches:
            if match.home not in total_goal_dict:
                total_goal_dict[match.home] = 0
            elif match.away not in total_goal_dict:
                total_goal_dict[match.away] = 0

        for match in self.matches:
            total_goal_dict[match.home] += int(match.home_score)
            total_goal_dict[match.away] += int(match.away_score)

        return total_goal_dict


    def leaderboard_after_input_round(self, roundd: int, sport: str, option: int):
        """function have as parameters the round till you want the leaderboard, the matches
        list and the sport

        Args:
            roundd (int): the round inputed at option 2
            matches (list): list of the matches
            sport (str) : the sport of the championship

        Returns:
            dict: returns a dictionary with the teams and their score sorted in descending order
        """

        
        teams_dict = {}
        for match in self.matches:
            if match.home not in teams_dict:
                teams_dict[match.home] =[0, 0, 0, 0]
            if match.away not in teams_dict:
                teams_dict[match.away] = [0, 0, 0, 0]

        for key in teams_dict:
            teams_dict[key][0] = 0 #points
            teams_dict[key][1] = 0 #matches played     
            teams_dict[key][2] = 0 #goal average
            teams_dict[key][3] = 0 #total goals

        if option == 3:
            return teams_dict

        goal_average_per_team = self.goal_average()
        total_goals = self.total_goals_per_team()

        
        for key in goal_average_per_team:
            teams_dict[key][2] = goal_average_per_team[key]

        for key in total_goals:
            teams_dict[key][3] = total_goals[key]

        index = 0
        #teams_dict[][0] -> points
        #teams_dict[][1] -> games played
        for match in self.matches:
            if 'ROUND' in match.ROUND:
                temp_ind =  match.ROUND.strip().split(' ')
                index = int(temp_ind[1])
                match.home_score = int(match.home_score)
                match.away_score = int(match.away_score)
                if index <= roundd:
                    if sport == 'Basketball':
                            if match.home_score > match.away_score:
                                teams_dict[match.home][0] += 2
                                teams_dict[match.home][1] += 1
                                teams_dict[match.away][1] += 1
                            else:
                                teams_dict[match.away][0] += 2
                                teams_dict[match.away][1] += 1
                                teams_dict[match.home][1] += 1
                        
                        
                    else:
                        if match.home_score > match.away_score:
                            teams_dict[match.home][0] += 3
                            teams_dict[match.home][1] += 1
                            teams_dict[match.away][1] += 1


                        elif match.home_score < match.away_score:
                            teams_dict[match.away][0] += 3
                            teams_dict[match.home][1] += 1
                            teams_dict[match.away][1] += 1
                        else:
                            teams_dict[match.away][0] += 1
                            teams_dict[match.home][0] += 1
                            teams_dict[match.home][1] += 1
                            teams_dict[match.away][1] += 1
                else:
                    break

        
        #problema de rezolvat!!!!!!!!!!!!!
        teams_dict = dict(sorted(
            {
                key: value
                for key, value in teams_dict.items()
                if value[1] != 0
            }.items(),
            key=lambda item: (
            -item[1][0] / item[1][1],  # Then sort by points per game (descending)
            item[1][2],                # Then sort by goal average (descending)
            item[1][3],                # Then sort by total goals scored (descending)
            item[0]                    # Finally, sort alphabetically by team name (ascending)
    )
        ))
        
        if option == 2:
            for key in teams_dict:
                print(f"{key} - {teams_dict[key][0]}")
        else:
            
            ordered_matches = []
            for key in teams_dict:
                ordered_matches.append(key)

            return ordered_matches


    def matches_played_till_given_round(self, roundd: int, team_to_find: str):
        list_of_matches = []
        for match in self.matches:
            if 'ROUND' in match.ROUND:
                temp_ind =  match.ROUND.strip().split(' ')
                index = int(temp_ind[1])
                if index <= roundd:
                    if match.home == team_to_find or match.away == team_to_find:
                        list_of_matches.append(match)
        
        for match in list_of_matches:
            print(match)        

    def maximum_round(self):

        maximum = 0
        for match in self.matches:
            if 'ROUND' in match.ROUND:
                temp = match.ROUND.strip().split(' ')
                maximum = max(int(temp[1]), maximum)
        return maximum
    
    def firstn_vs_lastm(self, left: int, right: int, option_2: int, sport: int):
        victory = 0
        draws = 0
        loses = 0
        W = []
        L = []
        if left > right:
            raise ValueError("[left, right] must be an interval with right >= left!")
            

        else:
            for index in range(left, right + 1):

                team = self.leaderboard_after_input_round(index - 1, sport, 0)
                first_3 = team[:3]
                last_3 = team[-3:]
               
                for match in self.matches:
                    if 'ROUND' in match.ROUND:
                        match.home_score = int(match.home_score)
                        match.away_score = int(match.away_score)
                        
                        temp = match.ROUND.strip().split(' ')
                        valid_round = int(temp[1])
                        
                        if valid_round == index:
                            if match.home in first_3:
                                if match.away in last_3:                    
                                    if match.home_score > match.away_score:
                                        victory += 1
                                        W.append(match)
                                        #W.append([first_3, last_3])
                                    elif match.home_score == match.away_score:
                                        draws += 1

                                    else:
                                        loses += 1
                                        L.append(match)
                                        #L.append([first_3, last_3])
                                else:
                                    pass
                            elif match.away in first_3:
                                if match.home in last_3:
                                
                                    if match.home_score < match.away_score:
                                        victory += 1
                                        W.append(match)
                                        #W.append([first_3, last_3])

                                    elif match.home_score == match.away_score:
                                        draws += 1
                                    else:
                                        loses += 1
                                        L.append(match)
                                        #L.append([first_3, last_3])
                                else:
                                    pass
                            else:
                                pass
                

            
            if option_2 == 2:
                print("Here are the wins, loses and draws for the first 3 teams:\n")
                print(victory, draws, loses, sep=" ")
                for w in W:
                    print(w)
                print()
                for l in L:
                    print(l)
                
            else:
                return victory, draws, loses