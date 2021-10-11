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

def strava():
    # take environment variables from .env.
    load_dotenv()
    hugo_file = "../hugo/main/content/hobbies/fitness/strava.md"
    static_files = "../hugo/main/static/images/"
    
    # these are all needed in order to re-auth and refresh the API Token
    MY_STRAVA_CLIENT_ID=os.environ.get("STRAVA_CLIENT_ID")
    MY_STRAVA_CLIENT_SECRET=os.environ.get("STRAVA_CLIENT_SECRET")
    MY_STRAVA_REFRESH_TOKEN=os.environ.get("STRAVA_REFRESH_TOKEN")

    # create an empty client
    client = Client()

    # refresh the API token, it expires every 6h and this will only run once a day
    refresh_response = client.refresh_access_token(client_id=MY_STRAVA_CLIENT_ID, client_secret=MY_STRAVA_CLIENT_SECRET, refresh_token=MY_STRAVA_REFRESH_TOKEN)
    client.access_token = refresh_response['access_token']
    client.refresh_token = MY_STRAVA_REFRESH_TOKEN
    
    athlete = client.get_athlete()
    
    # get the last 5 workouts before current time
    today_utc = datetime.datetime.utcnow()
    #today_utc = today_utc.strftime("%Y-%m-%d %H:%M:%S")
    yesterday_utc = today_utc - timedelta(days=1)
    yesterday_utc = yesterday_utc.strftime("%Y-%m-%d %H:%M:%S")
    today_activites = client.get_activities(after=yesterday_utc, limit=5)
       

    profile_url = "https://www.strava.com/athletes/{}/".format(athlete.id)

    try:
        mdFile = MdUtils(file_name=hugo_file)
    except Exception as err:
        print("Path to file does not exist", err)

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

    mdFile.new_header(level=1, title='Profile')
    mdFile.new_paragraph("**Profile**: " +  mdFile.new_inline_link(link=profile_url, text="qgriffith", bold_italics_code='b'))
    mdFile.new_paragraph("**YTD Total Runs:** {0}".format(run_ytd_totals.count))
    mdFile.new_paragraph("**YTD Total Miles Ran:** {0}".format(unithelper.miles(run_ytd_totals.distance)))
    mdFile.new_paragraph("**Last 30 days Total Runs:** {0}".format(run_monthly_totals.count))
    mdFile.new_paragraph("**30 Day Total Miles Ran:** {0}".format(unithelper.miles(run_monthly_totals.distance)))
    
    mdFile.new_header(level=2, title="Today's Runs")
    
    # use count to validate if any workouts happened today and if not print no workouts
    count = 0 

    with open(hugo_file, "w+") as f:
        for a in today_activites:
            if "Run" in a.type:
                mdFile.new_paragraph("**Workout Type:** {0}".format(a.type))
                mdFile.new_paragraph("**Title:** {}".format(a.name))
                mdFile.new_paragraph("**Time:** {0}".format(a.elapsed_time))
                mdFile.new_paragraph("**Distance:** {0}".format(unithelper.miles(a.distance)))
        f.write(mdFile.file_data_text)

    """
    athlete = client.get_athlete()
    run = client.get_athlete_stats().recent_run_totals
    run.distance
    miles= run.distance * 0.000621371192
    print(unithelper.miles(run.distance))


    activities = client.get_activities(limit=3)
    for a in activities:
        my_dict=a.to_dict()
        if "Run" in my_dict['type']:
            miles=my_dict['distance'] * 0.000621371192
            print(round(miles,2))
    """
strava()