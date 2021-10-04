#!/usr/bin/env python3

import pylotoncycle
from mdutils.mdutils import MdUtils
from mdutils import Html
import urllib.request
from dotenv import load_dotenv
import os
import datetime
import sys

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

    #get only the last workout TODO:Update to all work outs for the day
    try:
        last_workout = conn.GetRecentWorkouts(1)
    except Exception as err:
        print("This is weird, unable to find a workout", err)

    #returns all your profile data
    try:
        me = conn.GetMe() 
    except Exception as err:
        print("User may not exist", err)

    profile_url = "https://members.onepeloton.com/members/{0}/overview".format(me['username'])
    total_workouts = me['total_workouts']
    hugo_file = "../hugo/main/content/hobbies/fitness/index.md"
    static_files = "../hugo/main/static/images/"
    
    try:
        mdFile = MdUtils(file_name=hugo_file)
    except Exception as err:
        print("Path to file does not exist", err)

    # create the hugo header which elimantes needing to have hugo stub the page out
    mdFile.new_paragraph('---')
    mdFile.new_paragraph('title: "Fitness"')
    mdFile.new_paragraph("date: {0}".format(datetime.date.today()))
    mdFile.new_paragraph("draft: false")
    mdFile.new_paragraph('tags:  ["peloton", "fitness"]')
    mdFile.new_paragraph('categories:  ["fitness"]')
    mdFile.new_paragraph('---')

    mdFile.new_header(level=1, title='Peloton')
    mdFile.new_header(level=2, title='Profile')
    mdFile.new_paragraph("**Profile**: " +  mdFile.new_inline_link(link=profile_url, text=me['username'], bold_italics_code='b'))
    mdFile.new_paragraph("**Total Workouts:** {0}".format(total_workouts))
    
    mdFile.new_header(level=3, title='Last Workout')
    with open(hugo_file, "w+") as f:
        # There will ever only be a single workout in the current config but may change it to all workouts for the day
        for w in last_workout: 
            workout_id = w['id']
            resp = conn.GetWorkoutById(workout_id)
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
            
            classimage__save_path = "{0}{1}".format(static_files, "class.jpg")
            classimage_url = "{0}{1}".format("/images/", "class.jpg")
            urllib.request.urlretrieve(class_image, classimage__save_path)
            mdFile.new_paragraph(Html.image(path=classimage_url, size='x250'))

            mdFile.new_paragraph("**Workout Type:** {0}".format(name))
            mdFile.new_paragraph("**Title:** " + mdFile.new_inline_link(link=class_url, text=title, bold_italics_code='b'))
            mdFile.new_paragraph("**Instructor:** {0}".format(coach))
            mdFile.new_paragraph("**Badges:** {0}".format(len(resp['achievement_templates'])))

            for badge in resp['achievement_templates']:
                sanitze_badge = badge['name'].replace(" ", "")
                badge__save_path = "{0}{1}{2}".format(static_files, sanitze_badge, '.jpg')
                badge_url = "{0}{1}{2}".format("/images/", sanitze_badge, ".jpg")
                urllib.request.urlretrieve(badge['image_url'], badge__save_path)
                mdFile.new_paragraph(Html.image(path=badge_url, size='x50'))
        f.write(mdFile.file_data_text)



if __name__ == "__main__":
    pelly()