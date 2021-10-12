#!/usr/bin/env python3

import pylotoncycle
from stravalib.client import Client
from stravalib.client import unithelper
from mdutils.mdutils import MdUtils
from mdutils import Html
import urllib.request
from dotenv import load_dotenv
import os
import datetime
from datetime import timedelta
import sys
import re

# take environment variables from .env.
load_dotenv()  

def pelly():
    """Pulls data out of the Peloton API 
        and outputs it in markdown to a file
        read by hugo    
    """
    PellyUser = os.environ.get("PELLY_USER")
    PellyPass = os.environ.get("PELLY_PASS")
    
    try:
     conn = pylotoncycle.PylotonCycle(PellyUser, PellyPass)
    except Exception as err:
        print("Connection error raised", err)
        sys.exit(1)

    try:
        # no clean way to get by date setting to 6 because I doubt I ever do that many in a single day
        today_workouts = conn.GetRecentWorkouts(6)
        today_workouts.sort(key = lambda x:x['start_time'])

    except Exception as err:
        print("This is weird, unable to find a workout", err)

    #returns all your profile data
    try:
        me = conn.GetMe() 
    except Exception as err:
        print("User may not exist", err)
        sys.exit(1)

    profile_url = "https://members.onepeloton.com/members/{0}/overview".format(me['username'])
    total_workouts = me['total_workouts']
    hugo_file = "../hugo/main/content/hobbies/fitness/peloton.md"
    static_files = "../hugo/main/static/images/"
    
    # use count to validate if any workouts happened today and if not print no workouts
    count = 0 

    try:
        mdFile = MdUtils(file_name=hugo_file)
    except Exception as err:
        print("Path to file does not exist", err)
        sys.exit(1)

    # create the hugo header which elimantes needing to have hugo stub the page out
    mdFile.new_paragraph('---')
    mdFile.new_paragraph('title: "Peloton"')
    mdFile.new_paragraph("date: {0}".format(datetime.date.today()))
    mdFile.new_paragraph("draft: false")
    mdFile.new_paragraph('tags:  ["peloton", "fitness"]')
    mdFile.new_paragraph('categories:  ["fitness"]')
    mdFile.new_paragraph('---')

    mdFile.new_header(level=1, title='Profile')
    mdFile.new_paragraph("**Profile**: " +  mdFile.new_inline_link(link=profile_url, text=me['username'], bold_italics_code='b'))
    mdFile.new_paragraph("**Total Workouts:** {0}".format(total_workouts))
    
    mdFile.new_header(level=2, title="Today's workouts")    

    with open(hugo_file, "w+") as f:
        for w in today_workouts:            
            # date is stored as epoch from the api. Takking current date and epoch date to format to y-m-d as a string to compare
            start_time =  datetime.datetime.fromtimestamp(w['start_time']).strftime('%y-%m-%d')
            current_date = datetime.date.today().strftime('%y-%m-%d')

            if start_time == current_date:
                count += 1
                workout_id = w['id']
                resp = conn.GetWorkoutById(workout_id)
                mdFile.new_header(level=3, title=resp['name'])
                class_image = resp['ride']['image_url']
                name = resp['name']
                title = resp['ride']['title']
                discipline=resp['fitness_discipline']
                classId=resp['ride']['id']
                class_url = "https://members.onepeloton.com/classes/{0}?classId={1}&modal=classDetailsModal".format(discipline, classId)

                # we only get the ID of the instructor and have to look up their name in a dict pulled from the api
                try:
                    instructor = conn.instructor_id_dict[resp['ride']['instructor_id']]
                except Exception as err:
                    print("Coach was not found", err)
                
                coach=instructor['name']
                
                classimage__save_path = "{0}{1}-{2}.jpg".format(static_files, "class", w['id'])
                classimage_url = "{0}{1}-{2}.jpg".format("/images/", "class", w['id'])
                urllib.request.urlretrieve(class_image, classimage__save_path)
                mdFile.new_paragraph(Html.image(path=classimage_url, size='x250'))

                mdFile.new_paragraph("**Workout Type:** {0}".format(name))
                mdFile.new_paragraph("**Title:** " + mdFile.new_inline_link(link=class_url, text=title, bold_italics_code='b'))
                mdFile.new_paragraph("**Instructor:** {0}".format(coach))
                mdFile.new_paragraph("**Badges:** {0}".format(len(resp['achievement_templates'])))

                for badge in resp['achievement_templates']:
                    sanitze_badge = re.sub(r'\W+', '', badge['name'])
                    badge__save_path = "{0}{1}{2}".format(static_files, sanitze_badge, '.jpg')
                    badge_url = "{0}{1}{2}".format("/images/", sanitze_badge, ".jpg")
                    urllib.request.urlretrieve(badge['image_url'], badge__save_path)
                    mdFile.new_paragraph(Html.image(path=badge_url, size='x50'))   
                mdFile.write('\n')        
        if count == 0:
            print("No workouts found today, slacker!!")
            mdFile.new_paragraph("**No workouts today**")
        
        mdFile.new_paragraph("**Total today:** {0}".format(count))

        print("Writting Peloton Hugo Page")
        f.write(mdFile.file_data_text)        

def strava():
    """Pulls data out of the Strava API 
        and outputs it in markdown to a file
        read by hugo    
    """
    hugo_file = "../hugo/main/content/hobbies/fitness/strava.md"
    
    # these are all needed in order to re-auth and refresh the API Token
    MY_STRAVA_CLIENT_ID=os.environ.get("STRAVA_CLIENT_ID")
    MY_STRAVA_CLIENT_SECRET=os.environ.get("STRAVA_CLIENT_SECRET")
    MY_STRAVA_REFRESH_TOKEN=os.environ.get("STRAVA_REFRESH_TOKEN")

    # use count to validate if any workouts happened today and if not print no workouts
    count = 0 

    # create an empty client
    client = Client()

    # refresh the API token, it expires every 6h and this will only run once a day
    try:
        refresh_response = client.refresh_access_token(client_id=MY_STRAVA_CLIENT_ID, client_secret=MY_STRAVA_CLIENT_SECRET, refresh_token=MY_STRAVA_REFRESH_TOKEN)
        client.access_token = refresh_response['access_token']
        client.refresh_token = MY_STRAVA_REFRESH_TOKEN
    except Exception as err:
        print("Something has gone wrong with the API token refresh....", err)
        sys.exit(1)

    athlete = client.get_athlete()
    
    # get the last 5 workouts during the last 24 hours
    today_utc = datetime.datetime.utcnow()
    yesterday_utc = today_utc - timedelta(days=1)
    yesterday_utc = yesterday_utc.strftime("%Y-%m-%d %H:%M:%S")
    today_activites = client.get_activities(after=yesterday_utc, limit=5)       

    profile_url = "https://www.strava.com/athletes/{}/".format(athlete.id)

    try:
        mdFile = MdUtils(file_name=hugo_file)
    except Exception as err:
        print("Path to file does not exist", err)
        sys.exit(1)

    run_ytd_totals = client.get_athlete_stats().ytd_run_totals
    run_monthly_totals = client.get_athlete_stats().recent_run_totals
    
    # create the hugo header which elimantes needing to have hugo stub the page out
    mdFile.new_paragraph('---')
    mdFile.new_paragraph('title: "Strava Running"')
    mdFile.new_paragraph("date: {0}".format(datetime.date.today()))
    mdFile.new_paragraph("draft: false")
    mdFile.new_paragraph('tags:  ["strava", "running", "fitness"]')
    mdFile.new_paragraph('categories:  ["fitness"]')
    mdFile.new_paragraph('---')

    mdFile.new_header(level=1, title='Profile Stats')
    mdFile.new_paragraph("**Profile**: " +  mdFile.new_inline_link(link=profile_url, text="qgriffith", bold_italics_code='b'))
    mdFile.new_paragraph("**YTD Total Runs:** {0}".format(run_ytd_totals.count))
    mdFile.new_paragraph("**YTD Total Miles Ran:** {0}".format(unithelper.miles(run_ytd_totals.distance)))
    mdFile.new_paragraph("**Last 30 days Total Runs:** {0}".format(run_monthly_totals.count))
    mdFile.new_paragraph("**30 Day Total Miles Ran:** {0}".format(unithelper.miles(run_monthly_totals.distance)))
    
    mdFile.new_header(level=2, title="Today's Runs")
    
    with open(hugo_file, "w+") as f:
        for a in today_activites:            
            if "Run" in a.type:
                pace_seconds = a.moving_time.seconds/unithelper.miles(a.distance).num
                count += 1
                mdFile.new_paragraph("**Workout Type:** {0}".format(a.type))
                mdFile.new_paragraph("**Title:** {}".format(a.name))
                mdFile.new_paragraph("**Date:** {}".format(a.start_date_local.strftime("%y-%m-%d %H:%M")))
                mdFile.new_paragraph("**Time:** {0}".format(a.elapsed_time))
                mdFile.new_paragraph("**Distance:** {0}".format(unithelper.miles(a.distance)))
                mdFile.new_paragraph("**Pace:** {0}/mi".format(round(pace_seconds/60, 2)))
                mdFile.new_paragraph("**Average Speed:** {0}".format(unithelper.miles_per_hour(a.average_speed)))
                mdFile.new_paragraph("**Max Speed:** {0}".format(unithelper.miles_per_hour(a.max_speed)))
                
        if count == 0:
            print("No runs found today, slacker!!")
            mdFile.new_paragraph("**No runs today**")
        
        print("Writting Strava Hugo Page")    
        f.write(mdFile.file_data_text)

if __name__ == "__main__":
   print("Gathering Peloton Data........")
   pelly()

   print("Gathering Stava Data........")
   strava()