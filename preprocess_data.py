"""Preprocess the strava folder of activity information."""
import os
import subprocess
import csv
import sys

# CONSTANTS ------------------------------------
UNZIPPED_FOLDER = "export_26262221"
STRAVA_ACTIVITIES_SUBFOLDER = "activities"
STRAVA_ACTIVITIES_FILE = "activities.csv"
# ----------------------------------------------

# unzip and delete the archive -----------------
def unzip(file):
    import gzip
    import shutil
    with gzip.open(file, 'rb') as f_in:
        with open(file.lower().replace('.gz', ''), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
            os.remove(file)

# helper for executing babel -------------------
def exec_cmd(command):
    result = subprocess.Popen(command, shell=True)
    _ = result.communicate()[0]
    return_code = result.returncode
    if return_code != 0:
        return False
    return True

# exit with error ------------------------------
def die(error):
    print("Error: " + error)
    quit()

# main -----------------------------------------
def main():
    global UNZIPPED_FOLDER
    global STRAVA_ACTIVITIES_SUBFOLDER
    global STRAVA_ACTIVITIES_FILE

    # assemble paths
    strava_unzipped_folder = os.path.join(".", UNZIPPED_FOLDER)
    strava_unzipped_activities_folder = os.path.join(
        ".", UNZIPPED_FOLDER, STRAVA_ACTIVITIES_SUBFOLDER)
    strava_unzipped_activities_file = os.path.join(
        ".", UNZIPPED_FOLDER, STRAVA_ACTIVITIES_FILE)

    # pre-check
    if not os.path.exists(strava_unzipped_folder):
        die("Folder with expected unzipped Strava archive '{path}' doesn't exits.".format(path=strava_unzipped_folder))

    if not os.path.exists(strava_unzipped_activities_folder):
        die("Folder with activities in unzipped Strava archive '{path}' doesn't exits.".format(path=strava_unzipped_activities_folder))

    if not os.path.isfile(strava_unzipped_activities_file):
        die("File with activities in unzipped Strava archive '{path}' doesn't exits.".format(path=strava_unzipped_activities_file))

    # reading the activities.csv file and storing the list in activities_list
    print("Reading '{path}'".format(path=strava_unzipped_activities_file));
    try:
        with open(strava_unzipped_activities_file, newline='\n', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            activities_list = list(reader)
    except Exception as ex:
        die("Cannot read '{path}'. {err}".format(path=strava_unzipped_activities_file, err=str(ex)))

    # get the count of the activities
    cnt = len(activities_list)
    print("Found {cnt} activities ".format(cnt=str(cnt)))

    # let's go through the list and unzip any .gz files if exists
    print("Unzipping ...")
    sys.stdout.write("Progress: ")
    ucnt = 0
    for line in activities_list:
        x = 0
        filename = os.path.join(strava_unzipped_folder, line['Filename'])
        ucnt += 1
        sys.stdout.write("{:2.0%}".format(ucnt / cnt).rjust(5, " "))
        sys.stdout.flush()
        if filename.endswith(".gz") and os.path.exists(filename):
            unzip(filename)
        line['Filename'] = line['Filename'].replace(".gz", "")
        sys.stdout.write("\b\b\b\b\b")
        sys.stdout.flush()
        x += 1
    sys.stdout.write("\n")

    # now remove extra \n from GPX and convert TCX to GPX using gpsbabel
    print("Normalizing ...")
    for line in activities_list:
        filename = os.path.join(strava_unzipped_folder, line['Filename'])
        extension = os.path.splitext(filename)[1][1:].strip().lower()

        if os.path.exists(filename):
            if extension == "gpx":
                pass

            # strip spaces from tcx
            if extension == "tcx":
                os.remove(filename)  # see if we need these

            # remove .fit files - LifeTime classes (no movement outside)
            if extension == "fit":
                os.remove(filename)


    # assemble the filename for the backup file
    new_activities_file = strava_unzipped_activities_file + ".original"
    print("Backing up the original activities as '{new}' ...".format(new=new_activities_file))
    os.rename(strava_unzipped_activities_file, new_activities_file)

    # rewrite the activities file
    print("Saving new activities ...")
    with open(strava_unzipped_activities_file, 'w', newline='\n', encoding='utf-8') as csvfile:
        fieldnames = list(activities_list[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for line in activities_list:
            writer.writerow(line)

# run ------------------------------------------------------
if __name__ == "__main__":
    main()
