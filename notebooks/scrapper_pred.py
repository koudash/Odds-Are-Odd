from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
from notebooks.config import league_info, companies_training


def live_scrapper (league):

    # Dict for window handle (wh)
    wh_dict = {
        "week": "",
        "match": "",
        "company": ""
    }

    # Use selenium in Chrome
    driver = webdriver.Chrome(executable_path=r"notebooks/chromedriver.exe")

    # Load url
    driver.get(league_info[league]["live_url"])

    # Note that the webpage is automatically linked to the week of incoming matches
    # There is no need to code for week
    # Window handle (wh) for week of match page
    wh_dict["week"] = driver.window_handles[0]

    # Create (Reset) DataFrame to store scrapped info for matches of each week
    match = pd.DataFrame(columns=["home", "away", "company", "win_odds", "draw_odds",\
        "lose_odds", "odds_delta_time", "result"])  

    # All rows in match table
    # Note that the first two rows are actually headers
    rows_match_table = driver.find_elements_by_xpath('//*[@id="Table3"]/tbody/*')

    # Loop through all matches of selected week for matches that have not been played
    for m in range(3, 1 + len(rows_match_table)):
        
        # match score equals to "" if has not been played
        # Note that "find_elements_by_tag_name()" start counting from 0, so use "[3]" for "td[4] in "xpath"
        if rows_match_table[m - 1].find_elements_by_tag_name("td")[3].text =="":  

            # ********** |Retrieve info. from match list of selected week| ********** #
            # Name of home and away team
            home = driver.find_elements_by_xpath(f'//*[@id="Table3"]/tbody/tr[{m}]/td[3]/a')[0].text
            away = driver.find_elements_by_xpath(f'//*[@id="Table3"]/tbody/tr[{m}]/td[5]/a')[0].text            
            # Match result (not available as has not been played)
            result = "N/A"            
                
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
                # Note that we are scraping data from Chinese website, which sometimes could be very slow                
                # Set the waiting time forever(1h) for class name="rb" to respond to calls before sending Exception message
                element = WebDriverWait(driver, 3600).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "rb"))
                )

                # ********** |Retrieve info. from specific match (as represented by iterator j) of selected week| ********** #                
                # All text under "td" element with match date info
                all_text = driver.find_elements_by_xpath('//*[@id="team"]/form/table/tbody/tr[1]/td')[0].text
                # Split "all_text" and get string with date info
                date_info = all_text.split("]")[-1]
                # Year info. of selected match
                year = date_info[:4]
                month = date_info[5:7]
                day = date_info[8:10]
                time_info = date_info[-5:]
                # Concatenate "match_time" and convert to timestamps format
                # Note that match time is scrapped as Central Standard Time (CST), no need to adjust for Central Daylight Time (CDT)
                match_time = pd.to_datetime(f"{year}-{month}-{day} {time_info}", format="%Y-%m-%d %H:%M", errors="ignore")        

                # Retrieve all "tr" that have odds data provided by different companies
                rows_company = driver.find_elements_by_xpath(f'//*[@id="oddsList_tab"]/tbody/*')

                # Iterate through company list
                for company in league_info[league]["company_pred"]:

                    # Look for row of "12Bet"
                    for row in rows_company:

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
                    
                    # Close "match" window
                    driver.close()   

                    # Switch driver to odds info from iterated company for the specific match
                    driver.switch_to.window(wh_dict["company"])

                    try:
                        # Use WebDriverWait in combination with ExpectedCondition to setup implicit wait
                        element = WebDriverWait(driver, 3600).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "font13"))
                        )

                        # ********** |Scrape odds data from selected company| ********** #
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
                            match.loc[index, "home"] = league_info[league]["name_transl"][home]
                            match.loc[index, "away"] = league_info[league]["name_transl"][away]
                            match.loc[index, "company"] = companies_training[company]
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
                            odds_time = pd.to_datetime(year + "-" + dict_im[-1], format="%Y-%m-%d %H:%M", errors="ignore")
                            # Calculate minutes difference of odds update time towards the start of match
                            # Note that "match_time" is GMT-6 and "odds_time" is GMT+8, +8 - (-6) = 14h
                            delta_minutes = (match_time - odds_time + pd.Timedelta(hours=14)).total_seconds() / 60
                            # There is possibility that odds were released by the end of 2018 and match played in 2019
                            # In this scenario, "delta_minutes" will be calculated less than -500000 as match played was assigned to 2018
                            if delta_minutes < -100000:  # Randomly pick -100000
                                delta_minutes += 365 * 24 * 60

                            # Append minutes for odds towards starting of the match to "odds_time_list"
                            match.loc[index, "win_odds"] = dict_im[0]
                            match.loc[index, "draw_odds"] = dict_im[1]
                            match.loc[index, "lose_odds"] = dict_im[2]                    
                            match.loc[index, "odds_delta_time"] = delta_minutes

                    except:
                        raise Exception(f'Timed out. Cannot open odds-movement webpage from {companies_training[company]} ...')

                # Close "company" window
                driver.close()
                # Switch driver to week page
                driver.switch_to.window(wh_dict["week"])                

            except:
                raise Exception('Timed out. Cannot open detailed match webpage ...')
                
    # Close "week" window
    driver.close()

    return match

