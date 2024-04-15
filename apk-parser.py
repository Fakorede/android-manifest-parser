# first install package with pip install git+https://github.com/appknox/pyaxmlparser.git
"""
Usage:
python apk-parser.py
"""
import glob
import csv
import time
import zipfile
from pyaxmlparser import APK
from pyaxmlparser.axmlprinter import AXMLPrinter
import re
import xml.etree.ElementTree as ET

def get_xml_from_apk():
    # process APKs first
    for file in glob.glob("apks/*.apk"):
        print("started analyzing {}".format(file))
        apk = APK(file)
        app_name = apk.application
        try:
            with zipfile.ZipFile(file, "r") as zip:
                zip.extractall(r"extracted-apks/{}-apk".format(app_name))
        except Exception as e:
            print("An error occured while extracting apk {}:".format(app_name), e)

        try:
            xml = AXMLPrinter(
                open("extracted-apks/{}-apk/AndroidManifest.xml".format(app_name), 'rb').read()).get_xml()
        except Exception as e:
            print("An error occured while reading xml file for {}:".format(app_name), e)

        if not search_xml_file("com.google.android.gms.car.application", xml):
            continue

        write_to_csv(app_name, file)
        print("done analyzing {}".format(file))

def search_xml_file(meta_string, xml_string):
    try:
        # Parse the XML string
        root = ET.fromstring(xml_string)

        # Convert XML tree to string
        xml_string = ET.tostring(root).decode()

        matches = re.findall(meta_string, xml_string)

        if matches:
            print("Found a match")
            return True
        else:
            return False
    except Exception as e:
        print("An error occurred while processing the XML string:", e)

def write_to_csv(app_name, file):
    try:
        with open('android-auto-apps.csv', "a", newline='') as output_file:
            fieldnames = ['APP', 'APK']

            writer = csv.writer(output_file)

            if output_file.tell() == 0:
                writer.writerow(fieldnames)  # Write header if file is empty

            writer.writerow([app_name, file])

    except Exception as e:
        print("An error occurred while writing to the CSV file:", e)

start_time = time.time()
get_xml_from_apk()
end_time = time.time()
elapsed_time_minutes = (end_time - start_time) / 60
print("ANALYSIS COMPLETE")
print("Elapsed time: {:.2f} minutes".format(elapsed_time_minutes))
