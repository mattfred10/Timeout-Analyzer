# -*- coding: utf-8 -*-

# TODO: Need to return dscorediff/dt, timeout (caller/false), eventual winner


# TODO: Pandas join? make tables to simplify data collection (eventual winner, tournament team, reduce data volume)


def find_runs(gamedata):
    """Uses scoring rate to determine whether a run is occurring and how it ends"""

    # Define runs based on average scoring rate over the course of the game

    final_score = list(map(int, gamedata.iloc[-1]['score'].split('-')))  # Should be indexed

    avg_scoring_rate = sum(final_score)/80  # 40 minutes * 2 teams
    is_run = False

    tempscorehistory = [[0,0,1200]] # [['home','away','time']]
    score_history = []
    interrupt = []
    runstart = []

    # runner and slipper correspond to the indices of the home and away teams [homescore, awayscore]
    runner = -1  # Throw an error if not assigned
    slipper = -1
    need120 = True
    need90 = True
    need60 = True
    need30 = True

    for a, grow in gamedata.iterrows():  # grow = gamerow

        current_score = list(map(int, grow['score'].split('-').extend(grow['time'])))

        # Need to account for both home and away
        # Need to account for counter runs after TO

        if is_run:
            # Remember if there is time stoppage during run
            if "TV" in grow['event']:
                interrupt.append(["TV", current_score[2]])
            elif "Timeout" in grow['event']:
                interrupt.append([TOCaller, current_score[2]])  ######################

            # Player named "Skylar Halford" matched "Half" so searching for 1st and/or 2nd in case other names appear
            elif "1st Half" in grow['event'] or "2nd Half" in grow['event'] or "Overtime" in grow['event']:
                interrupt.append(["Period", current_score[2]])
                is_run = False  # Not considering runs across halves/OTs
            elif a == gamedata['id'].iloc[-1]:  # End of game - Not always reported by ESPN, but should be last row no matter what
                interrupt.append(["GameOver", current_score[2]])
                is_run = False  # probably unnecessary as there shouldn't be another loop, but just in case


            if current_score[2] >= runstart[2] + 120 and need120:
                next120 = (current_score[runner] - runstart[runner]) - (current_score[slipper] - runstart[slipper])
                need120 = False
            elif current_score[2] >= runstart[2] + 90 and need90:
                next90 = (current_score[runner] - runstart[runner]) - (current_score[slipper] - runstart[slipper])
                need90 = False
            elif current_score[2] >= runstart[2] + 60 and need60:
                next60 = (current_score[runner] - runstart[runner]) - (current_score[slipper] - runstart[slipper])
                need60 = False
            elif current_score[2] >= runstart[2] + 30 and need30:
                next30 = (current_score[runner] - runstart[runner]) - (current_score[slipper] - runstart[slipper])
                need30 = False

            if next30 < 0 and next60 < 0 or next90 < 1 or next120 < 3: #need to decide termination conditions. Maybe just collect next 90.
                is_run = False
                for row in tempscorehistory:
                    if row[2] <= current_score[2] + 30:
                          scorehistory.append([tempscorehistory[0][runner]-tempscorehistory[0][slipper], row[runner] - row[slipper]]) #[60 second history, 30 s history]
                          break
                tempscorehistory = []
        else:
            if current_score[2] <= tempscorehistory[0][2] - 60:
                run60 = (current_score[0] - tempscorehistory[0][0]) - (current_score[1] - tempscorehistory[0][1])
                tempscorehistory.pop(0) #it should be impossible for this list to be empty as some events have to occur for the score differential to increase

            # Increase in differential greater than average score rate = run (one team stopped scoring or the other is scoring much faster than normal)
            # Might relax this a bit in the future - could bin it to determine what actually constitutes a run
            # Going to start with a 60 second run. average scoring rate is probably around 1.5 points/minute. Could get set off very easily
            # TODO: What we really want is the differential, e.g., +min 5pts (only 2 possesions) &|| +2x avg rate (actually only ~3 pts) with no slipper score
            # &|| score differential 10(?)pts with some scores by slipper
            if run60 >= avg_scoring_rate * 2:  # Allowing starts of runs to span TOs - might need to change this, but I think it's valid
                runner = 0  # Home team, score index = 0
                slipper = 1  # Just set the value rather than doing calculations
                is_run = True
                runstart = current_score
            elif run60 >= avg_scoring_rate * -2:
                runner = 1  # Away team, score index = 1
                slipper = 0
                is_run = True
                runstart = current_score

            tempscorehistory.append(current_score)