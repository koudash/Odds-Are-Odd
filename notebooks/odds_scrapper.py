from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

from name_translator import companies, seria_a

def scrapper (league, season, name_translator, url, team_ct):

    # Print league info
    print(f"START ODDS-MOVEMENT SCRAPING FOR {league}_S{season} ... ")
    print("*" * 50)
    
    # List for company names
    company_list = ["bet 365(英国)", "威廉希尔(英国)", "Bwin(奥地利)", "12BET(菲律宾)"]

    # Dict for window handle (wh)
    wh_dict = {
        "week": "",
        "match": "",
        "company": ""
    }

    # Use selenium in Chrome
    driver = webdriver.Chrome()

    # Load url
    driver.get(url)

    # Loop through all weeks of matches
    for wk in range(1, 2 * (team_ct - 1) + 1):

        # Create (Reset) DataFrame to store scrapped info for matches of each week
        match = pd.DataFrame(columns=["week", "home", "away", "company", "win_odds", "draw_odds",\
            "lose_odds", "odds_delta_time", "result"])        

        # Print out week of match info currently under scrapping
        print(f"Matches from week{wk} is under scrapping ...")

        # Element where week of match is selected
        if wk <= 19:
            ele_wk = driver.find_elements_by_xpath(f'//*[@id="Table2"]/tbody/tr[1]/td[{wk + 1}]')[0]
        else:
            ele_wk = driver.find_elements_by_xpath(f'//*[@id="Table2"]/tbody/tr[2]/td[{wk - 19}]')[0]

        # Scroll down and move to element of target and click using JavaScript
        # https://stackoverflow.com/questions/49867377/how-do-i-scroll-up-and-then-click-with-selenium-and-python
        driver.execute_script("arguments[0].scrollIntoView(true);", ele_wk)
        driver.execute_script("arguments[0].click()", ele_wk)
        
        # Window handle (wh) for week of match page
        wh_dict["week"] = driver.window_handles[0]

        # Loop through all matches of selected week
        # Note that "team_ct / 2" will be automatically recognized as "float"
        for m in range(3, 3 + int(team_ct / 2)):

            # ********** |Retrieve info. from match list of selected week| ********** #
            # Splited match time by "\n" and temporarily stored in "match_time_split"
            match_time_split = driver.find_elements_by_xpath(f'//*[@id="Table3"]/tbody/tr[{m}]/td[2]')[0].text.split("\n")
            # Concatenate for "match_time" in "%m-%d %H:%M" format
            match_time = match_time_split[0] + " " + match_time_split[1]
            # Name of home and away team
            home = driver.find_elements_by_xpath(f'//*[@id="Table3"]/tbody/tr[{m}]/td[3]/a')[0].text
            away = driver.find_elements_by_xpath(f'//*[@id="Table3"]/tbody/tr[{m}]/td[5]/a')[0].text            
            # Match score
            score = driver.find_elements_by_xpath(f'//*[@id="Table3"]/tbody/tr[{m}]/td[4]/div/a')[0].text
            # Convert match score to "W-D-L" category
            home_score = int(score.split("-")[0])
            away_score = int(score.split("-")[1])
            if home_score > away_score:
                result = "W"
            elif home_score < away_score:
                result = "L"
            else:
                result = "D"  

            # Element where a specific match from iterated week is selected
            ele_match = driver.find_elements_by_xpath(f'//*[@id="Table3"]/tbody/tr[{m}]/td[10]/a[2]')[0]

            # Scroll down and move to element of target and click using JavaScript
            driver.execute_script("arguments[0].scrollIntoView(true);", ele_match)
            driver.execute_script("arguments[0].click()", ele_match)

            # Window handle for specific match page
            wh_dict["match"] = driver.window_handles[1]

            # Switch driver to specific match page
            driver.switch_to.window(wh_dict["match"])

            try:
                # Use WebDriverWait in combination with ExpectedCondition to setup implicit wait
                # In this case, it is 10 min for class name="rb" to respond to calls before sending Exception message
                # Note that we are scraping data from Chinese website, which sometimes could be very slow                
                element = WebDriverWait(driver, 600).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "rb"))
                )

                # ********** |Retrieve info. from specific match (as represented by iterator j) of selected week| ********** #                
                # All text under "td" element
                all_text = driver.find_elements_by_xpath('//*[@id="team"]/form/table/tbody/tr[1]/td')[0].text
                # text of the second "span" from bottom will be used as separator to split "all_text"
                # Note that text of the last "span" is ""
                sep = driver.find_elements_by_xpath('//*[@id="team"]/form/table/tbody/tr[1]/td/*')[-2].text                
                # Year info. of selected match
                year = all_text.split(sep)[-1][:4]            
                # With "year" being retrieved, convert "match_time" to timestamps format
                match_time = pd.to_datetime(str(year) + "-" + match_time, format="%Y-%m-%d %H:%M", errors="ignore")        
                
                # Retrieve all "tr" that have odds data provided by different companies
                rows_companies = driver.find_elements_by_xpath(f'//*[@id="oddsList_tab"]/tbody/*')
                
                # Iterate through company list
                for company in company_list:                    
                    
                    # Look for row of iterated company
                    for row in rows_companies:

                        # Retrieve all "td" under iterated "tr"
                        row_data = row.find_elements_by_tag_name("td")

                        if row_data[1].text == company:
                            # Element linking to pop-up window where odds-in-movement info. is displayed
                            ele_company = row_data[2]
                            # Jump out of "for loop" once row of iterated company has been found
                            break                                

                    # Scroll down and move to element of target and click using JavaScript
                    driver.execute_script("arguments[0].scrollIntoView(true);", ele_company)
                    driver.execute_script("arguments[0].click()", ele_company)

                    # Window handle for odds info from iterated company for the specific match
                    wh_dict["company"] = driver.window_handles[2]
                    
                    # Switch driver to odds info from iterated company for the specific match
                    driver.switch_to.window(wh_dict["company"])

                    try:
                        # Use WebDriverWait in combination with ExpectedCondition to setup implicit wait
                        # In this case, it is 10 min for class name="font13" to respond to calls before sending Exception message
                        element = WebDriverWait(driver, 600).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "font13"))
                        )

                        # ********** |Scrape odds data from selected company| ********** #
                        # Hour difference between Central (Daylight/Standard) Time (GMT-5/-6 for CDT/CST) and China Standard Time (GMT+8)
                        if (match_time < pd.Timestamp('2018-11-04')) or (match_time >= pd.Timestamp('2019-03-10')):
                            delta_hour = 13
                        else:
                            delta_hour = 14

                        # Retrieve all rows from tbody
                        rows_odds = driver.find_elements_by_xpath('/html/body/table/tbody/*')

                        # Loop through each row (except the header)
                        # Note that there is no "th" in this table and header is actually the first "tr"
                        for o in range(1, len(rows_odds)):
                            # Find all "td"
                            tds = rows_odds[o].find_elements_by_xpath(f'/html/body/table/tbody/tr[{o + 1}]/*')

                            # Variable to hold the row in "match" where new data are to be appended
                            index = len(match)

                            # Append match info. to "match"
                            match.loc[index, "week"] = wk
                            match.loc[index, "home"] = name_translator[home]
                            match.loc[index, "away"] = name_translator[away]
                            match.loc[index, "company"] = companies[company]
                            match.loc[index, "result"] = result

                            # Dict to store win, draw, loss odds as well as update time for home team 
                            dict_im = {0:"", 1:"", 2:"", -1:""}
                            # Scrape odds as well as time features and save under corresponding keys to "dict_im"
                            for key in list(dict_im.keys()):
                                dict_im[key] = tds[key].text
                            # Remove "\xa" from odds update time in "dict_im[-1]" list
                            dict_im[-1] = dict_im[-1][2:]
                            # Remove unnecessary Chinese character from original odds                    
                            if o == len(rows_odds) - 1:
                                dict_im[-1] = dict_im[-1][:-4]
                            # Convert the type of odds time from string to Timestamp
                            odds_time = pd.to_datetime(str(year) + "-" + dict_im[-1], format="%Y-%m-%d %H:%M", errors="ignore")
                            # Calculate minutes difference of odds update time towards the start of match
                            # Note that "match_time" is scrapped as CDT/CST and "odds_time" is scarpped as China Standard Time
                            delta_minutes = (match_time - odds_time + pd.Timedelta(hours=delta_hour)).total_seconds() / 60

                            # Append minutes for odds towards starting of the match to "odds_time_list"
                            match.loc[index, "win_odds"] = dict_im[0]
                            match.loc[index, "draw_odds"] = dict_im[1]
                            match.loc[index, "lose_odds"] = dict_im[2]                    
                            match.loc[index, "odds_delta_time"] = delta_minutes

                    except:
                        raise Exception(f'Timed out. Cannot open odds-movement webpage from {companies[company]} ...')

                    # Close "company" window
                    driver.close()
                    # Switch driver to specific match page
                    driver.switch_to.window(wh_dict["match"])                

                # Close "match" window
                driver.close()            
                # Switch driver to matches of iterated week page
                driver.switch_to.window(wh_dict["week"])

            except:
                raise Exception('Timed out. Cannot open detailed match webpage ...')

        # Save match of iterated week as csv file
        # Note that this will greatly reduce RAM usage for scrapped data if otherwise saving as an entity after all scrapping work
        match.to_csv(f"../data/{league}_S{season}-Week{wk}.csv", index=False, header=True)

    # Close "week" window
    driver.close()
    
    # Scrapping complete
    print("*" * 50)
    print(f"SCRAPING COMPLETE FOR {league}_S{season}")