#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Spotify search
@author: mcj
Created on Thu May 14 19:54:43 2020
"""

import json
import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from setupFile import INPUT_FILENAME, OUTPUT_FILENAME
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager


def startDatabase(dbName):
    dbBackupName = dbName.replace('.txt', "_previous.txt")
    try:
        shutil.copyfile(dbName, dbBackupName)
        db = open(dbName, 'w', newline='\n')
        db.close()
    except FileNotFoundError:
        open(dbName, 'w', newline='\n')

searchesTempFilename = INPUT_FILENAME.replace('.json','_temp.json')

with open(INPUT_FILENAME) as f:
    howManyQueries = len(json.load(f))
    print(howManyQueries,"songs to retrieve.")

breakFlag = False
songNumber = 0

options = Options()
options.headless = True

startDatabase(OUTPUT_FILENAME)

while songNumber < howManyQueries:
    pbar = tqdm(total=howManyQueries)

    with open(INPUT_FILENAME) as f:
        searchQueries = json.load(f)

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get('http://www.google.com')

    consentButton = driver.find_element_by_xpath('//*[@id="L2AGLb"]/div')
    consentButton.click()

    export = []

    for entry in searchQueries:

        day = entry['searchTime'][0:10]
        hour = entry['searchTime'][11:19]
        query = entry['searchQuery']
        extractedTargetUrls = entry['searchInteractionURIs']

        if len(extractedTargetUrls) > 0:
            targets = []
            for target in extractedTargetUrls:
                driver.get('http://www.google.com')
                elem = driver.find_element_by_class_name('gLFyf')
                elem.send_keys(target.replace('spotify:', ''))
                elem.send_keys(Keys.RETURN)

                try:
                    targetText = driver.find_element_by_css_selector(
                        'h3').text.split(" | Spotify")[0]
                except:
                    # NoSuchElementException
                    currentUrl = driver.current_url
                    if 'www.google.com/sorry/' in currentUrl:
                        lastIndex = searchQueries.index(entry)
                        INPUT_FILENAME = searchesTempFilename
                        with open(searchesTempFilename, 'w') as jsonFile:
                            jsonString = json.dumps(searchQueries[lastIndex:])
                            jsonFile.write(jsonString)
                            driver.close()
                            breakFlag = True
                            break
                    else:
                        targetText = '*****Unknown*****'

                targets += [targetText]

        else:
            targets = ['']

        export += [[day, hour, query, targets]]
        songNumber += 1

        pbar.update(1)

        if songNumber == howManyQueries or breakFlag:
            breakFlag = False
            break

    with open(OUTPUT_FILENAME, 'a', encoding='utf-8') as output:
        for line in export:
                
            lineToWrite = line[0] + ": " + ", ".join(line[3]) + " (" + line[2] +")\n"
            output.writelines(lineToWrite)

driver.close()
try:
    os.remove(searchesTempFilename)
except FileNotFoundError:
    pass
try:
    os.remove(OUTPUT_FILENAME.replace('.txt', "_previous.txt"))
except FileNotFoundError:
    pass

print("\nConsider it done.\n")

pbar.close()