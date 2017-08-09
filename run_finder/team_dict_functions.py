import MFLibrary as mf

# Catchall dictionary for duplicate keys, untenable name variations and typos
# Will be used when the main dictionary fails
# Determined empirically using these functions
errordict = {
    'BSU' : 'Bowie',
    'FAIR' : 'Fairview',
    'HOU' : 'Howard Payne',
    'MAR' : 'Marygrove',
    'NCST' : 'NC St',
    'NKU' : 'N Kentucky',
    'NDSU' : 'North Dakota',
    'PITT' : 'Pittsburg State',
    'SF' : 'Sioux Falls',
    'SLU' : 'Saint Louis',
    'TRGV' : 'Rio Grande',
    'UPST' : 'South Carolina Upstate',
    'WASH' : 'Washburn',
    'WIL' : 'Wilmington OH',
    }

def determine_TO_caller(event, teamlist, teamdict, errordict):
    """Determines the caller of a timeout.

    Also verifies that the team dictionary is unique.
    """

    # ABRs that fail to uniquely identify a tam are added to unqiuecheck
    uniquecheck = []
    # ABRs that pass are added to unqiuepass - only used during dictionary creation
    uniquepass = []

    if "television" in event.lower() or "tv " in event.lower() or "t.v." in event.lower() or "official" in event.lower():
        return "TV"

    caller = 'error'

    # Testing whether the dictionary values can uniquely identify the teams (e.g., Miami vs. Miami (OH))

    # First, find out if team[0] is in team[1] (e.g., Florida vs. Florida St). If the first dictionary term contains
    # the second term, it should still work with the normal routine, so pass it. Otherwise,
    # we need to try team[1], i.e., Florida will never be tested unless the event lacks 'St'.

    if teamdict[teamlist[0]] in teamdict[teamlist[1]]:  # Team[1] needs to be tested first
        if teamdict[teamlist[1]] != teamdict[teamlist[0]]:  # In case the team names are the same somehow
            for team in reversed(teamlist):
                if team in event or teamdict[team] in event:
                    uniquecheck.extend([team, teamdict[team], event])
                    return team
            # Didn't find a team - check the error dictionary
            for team in reversed(teamlist):  # Still need reversed order in the small dictionaries
                if errordict.get(team, 'None') in event:
                    uniquecheck.extend([team, teamdict[team], event])
                    return team
                elif 'N.C. St' in event:  # NCST requires 3 special cases
                    return 'NCST'

    # General case
    else:  # team[0] is longer than team[1] (Florida St, Florida) or not in team[1] at all (Florida, Georgia)
        for team in teamlist:
            if teamdict[team] in event or team in event:
                if teamdict[teamlist[0]] in teamdict[teamlist[1]] or teamdict[teamlist[1]] in teamdict[teamlist[0]]:
                    uniquepass.extend([caller, teamlist, event])
                return team
        # Didn't find a team - check the error dictionary
        for team in teamlist:
            if errordict.get(team, 'None') in event:
                if teamdict[teamlist[0]] in teamdict[teamlist[1]] or teamdict[teamlist[1]] in teamdict[teamlist[0]]:
                    uniquepass.extend([caller, teamlist, event])
                return team
            elif 'N.C. St' in event:
                if teamdict[teamlist[0]] in teamdict[teamlist[1]] or teamdict[teamlist[1]] in teamdict[teamlist[0]]:
                    uniquepass.extend([caller, teamlist, event])
                return 'NCST'

    return caller

def is_caller_winning(teamlist, score, caller):
    """Returns T/F if the TO caller is winning"""

    if teamlist.index(caller) == 0:
        if score[0] > score[1]:
            winning = True
        else:
            winning = False
    else:
        if score[0] > score[1]:
            winning = False
        else:
            winning = True

    return winning