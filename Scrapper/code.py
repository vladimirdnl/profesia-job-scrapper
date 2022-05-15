#importing needed libraries
from bs4 import BeautifulSoup as BS
import requests as re
from datetime import datetime
from os import system as sys, name as sys_name
from time import sleep

#defining default variables
link = 'https://www.profesia.sk' #setting original link
csv_file_loc = 'prsk_jobs.csv' #location of the csv
header_row_csv = 'Job,Employer,Location,Salary,WO_CV,Paid_ride_to_work,Housing,Available_for_UKR\n' #header row for csv file

#creating csv file / erasing all the previous data
with open(csv_file_loc, 'w+', encoding = 'utf-8') as csv_file:
    csv_file.write(header_row_csv)
    csv_file.close()

#creating function which prepares a string to be written into csv
def string_for_csv(data, salary = False):
    if salary == False:
        return str(data).replace(',', '')
    else:
        return str(data).replace(',', '.')

#going to a page with job groups and scanning it
link_positions = ''.join([link, '/praca/zoznam-pozicii/']) #the link to webpage with groups of jobs
page_positions = re.get(link_positions) #getting the webpage
soup_positions = BS(page_positions.text, 'lxml') #parsing the webpage
job_pos_list = soup_positions.find('ul', class_ = "list-reset") #finding a list of job groups
job_positions = job_pos_list.find_all('li') #finding every job group in this list

#improving UI in command line for different platforms
def clear(): #define clear function
    if sys_name == 'nt': #for windows
        _ = sys('cls')
    else:   #for mac and linux
        _ = sys('clear')
def print_progress(jobs_count, datetime_start): #define print_progress functions
    clear() #clear terminal
    print('Scanning is in progress...') 
    #print the achieved progress and round it
    current_datetime = datetime.now()
    time_spent = (current_datetime - datetime_start).total_seconds()
    avg_speed = float(jobs_count)/time_spent
    print(f'Totally {jobs_count} jobs scanned') 
    print(f'Time spent scanning: {int(time_spent//60)} min {round(time_spent - time_spent//60*60, 3)} sec')
    print(f'Avg speed: {round(avg_speed, 2)} jobs/s')

#print that scanning is started before scanning
print('Scanning begins...')
sleep(0.7)

#creating current time instance for tracking the progress
#Setting 
start_datetime = datetime.now()

#setting jobs counter to 0
jobs_counter = 0

#initialize the loop for every job group in the list
for index, job_position in enumerate(job_positions):
    #limit_index = 10 #to control the loop
    job_name_text = job_position.a.text #getting a job group title
    offer_list_link = ''.join([link, job_position.a.get('href')]) #creating link to job offers

    #getting the first page and setting additional info
    current_page_num = 1 #setting number of page to 1
    page = re.get(offer_list_link) #getting the first page of offers
    soup = BS(page.text, 'lxml') #parsing the first page of offers

    #getting the last page number for job offers
    nav_bar = soup.find('ul', class_ = 'pagination') #getting pagination element
    if type(nav_bar) == type(None): #if there is no navigation bar
        last_page_num = 1 #then the last page is the first page
    else:
        last_page_num = int(nav_bar.find_all('li', class_ = '')[-2].text) #getting last page number
                                                                          # as an integer
    #creating a do-while loop for scraping
    while True:
        jobs = soup.find_all('li', class_ = 'list-row') #finding all job cards on the current page
        page_data = '' #setting the page data to an empty string

        #'for' loop in order to extract data from every job and write it to csv
        for job in jobs:
            #getting the employer
            job_employer = job.find('span', class_ = 'employer') #getting employer instance
            if type(job_employer) == type(None): #if there is none
                job_employer_text = 'None' #then we'll write 'None' to csv
            else:
                job_employer_text = job_employer.text #else remembering the employer's name

            #getting the location 
            job_location = job.find('span', class_ = 'job-location') #getting location instance
            if type(job_location) == type(None): #if there is none
                job_location_text = 'None' #then we'll write 'None' to csv
            else:
                job_location_text = job_location.text #else remebering the job's location

            #finding the salary or paid ride (they have the same span) - and one or two may be missing
            job_salary_and_paid_ride = job.find_all('span', class_ = 'label label-bordered green half-margin-on-top')
            job_salary_text = None #the default value - 'Salary is missing'
            paid_ride = 0   #the default value - 'Paid ride is missing'
            if type(job_salary_and_paid_ride) != type(None): #And if there were found istances of this span
                for instance in job_salary_and_paid_ride: #for each instance
                    if instance.svg.get('class')[1] == 'money': #if corresponding icon's class is "money"
                        job_salary_text = instance.text.strip() #get the salary and remember it
                    else: paid_ride = 1    #if not - setting paid_ride to 1, because each instance has 
                                           # svg's class either "money" or "bus"

            #finding first benefit - employment without a cv
            job_wo_cv = job.find('span', class_ = 'label label-bordered blue half-margin-on-top') 
            if type(job_wo_cv) != type(None): #if found - putting 1
                    WO_CV = 1
            else: WO_CV = 0    #if not - setting variable to 0

            #finding next benefit - paid housing for an employee
            job_housing = job.find('span', class_ = 'label label-bordered purple half-margin-on-top') 
            if type(job_housing) != type(None): #if found - putting 1
                    housing = 1
            else: housing = 0    #if not - setting variable to 0

            #finding last benefit - if the job isnavailable for ukrainians
            job_for_UKR = job.find('span', class_ = 'label label-bordered yellow half-margin-on-top half-margin-on-bottom') 
            if type(job_for_UKR) != type(None): #if found - putting 1
                    for_UKR = 1
            else: for_UKR = 0    #if not - setting variable to 0

            #creating a string for job data
            job_data = ''.join([string_for_csv(job_name_text),',', \
                            string_for_csv(job_employer_text), ',', \
                            string_for_csv(job_location_text), ',', \
                            string_for_csv(job_salary_text, salary=True), ',', \
                            str(WO_CV), ',', str(paid_ride), ',', str(housing), ',', \
                            str(for_UKR), '\n'])

            page_data = ''.join([page_data, job_data]) #adding current job info to page_data

            #at the end, updating the progress and showing it
            jobs_counter += 1
            print_progress(jobs_counter, start_datetime)
        
        #writing page to a csv file
        with open(csv_file_loc, 'a', encoding = 'utf-8') as csv_file: #opening to append with utf-8
            csv_file.write(page_data) #writing a page
            csv_file.close() #closing file
        
        #'if-else' block to control the 'do-while'loop 
        if current_page_num >= last_page_num: #if there are no left pages - break the loop
            break
        else: #else, do following:
            current_page_num += 1 #increasing page number
            next_page_link = ''.join([offer_list_link,f'?page_num={current_page_num}']) #opening a new page
            page = re.get(next_page_link) #updating html page
            soup = BS(page.text, 'lxml') #parsing updated html page and starting over
    
    #if index >= limit_index: #controlling the loop
    #   break
print('The scanning is complete!')