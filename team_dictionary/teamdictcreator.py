
import psycopg2
import csv
import sys
import MFLibrary as mf

# TODO: Refactor to use dictionary

# All of this could be abstracted to a function. I don't see much point now.
#
#There are a few important post-processing notes. To find the errors, TOAnalyzer outputs a file containing all of the mismatching
# teams and calls (e.g., "BCU,	SYR, Bethune Cookm Full Timeout). Going to the dictionary we find that "Bethune-Cookman" is the most common entry.
# We adjust the dictionary to "Bethune", which matches nothing else and should match both entries. Other notable changes below:
# 1. ESPN uses periods irregularly. They were removed usually simplifying the dictionary value.
#   However, this caused a few issues that were individually addressed (e.g., Steven F Austin - period was re-added).
#   Catholic schools (e.g., St. Johns) were also notable exceptions. In some cases, St. was removed entirely (sometimes they used Saint and somtimes St).
#   Possessives were removed in similar fashion
#
# 2. Both State and St are used. To deal with this issue, State was changed to 'St', which matches both - NC State proved difficult
#
# 3. Some names were conveniently shortened (e.g., Ole Miss used both Mississippi and Ole Miss. This was resolved by using only "Miss").
#   There are potential uniqueness issues. For example, Miami of Ohio and University of Miami usually match Miami (OH) and Miami (FL).
#   If they play, Miami may match Miami (OH), but Miami (OH) is always Miami (OH).
#
# 4. Some Schools use their abbreviations as well as other names (e.g., VMI and Virginia Military)
#   Searching for the abbreviation prevented the need for post-processing.
#
# 5. A few schools may need to be handled with more advanced logic. Perhaps some of the reduced uniqueness can be addressed there.
#
# 6. Fairfield and fairmont both apparently use FAIR as their key. "fair" set as value, which shouldn't be a problem PITT = Pittsburg State
#
# 7. White space was used with some effectiveness (e.g., St. Louis and Saint Louis used "Louis " to differentiate from Louisville)


conn = psycopg2.connect(host='localhost', database='CollegeBBall', user='postgres', password='')
cur = conn.cursor()
cur.execute("""
            SELECT
            teams,event
            FROM
            playbyplay
            WHERE event like '%Timeout%' and event not like '%TV%'
            """)
rows = cur.fetchall()

foundteams = []

for row in rows:
    # Delete extraneous information
    newteams = mf.string_functions.deletemany(row[0], ['[', ']',"'"," ",'Timeout','Full','30','20','.', "'s"]).replace('State', 'St').split(',')
    print(newteams)  # why is this a list
    for newteam in newteams:
        inlist = False
        testcombo = [newteam, row[1]]
        for team in foundteams:  # use dict
            if testcombo[0] == team[0] and testcombo[1] == team[1]:
                inlist = True
                team[2] += 1
                break
        if not inlist:
            testcombo.append(1)
            foundteams.append(testcombo)

mf.csv_functions.write_list_to_csv("TOCounts.csv", foundteams)

conn.close()