#Prints sis_user_id and group name for all students and groups in a course to a csv file.

#import libraries
import requests #for API requests
import json #used to parse API request
import re #for getting URLs
import pandas as pd #used to write tables
print("Libraries loaded")

#canvas credentials
API_key = "PUT_YOUR_API_KEY_HERE" #update with your API key
headers = {'Authorization' : f'Bearer {API_key}'} #not sure why people use headers for this value
API_URL = 'YOUR_COURSE_API_URL' #probably something like https://INSTITUTION.instructure.com/api/v1
COURSE_ID = 'COURSE_ID' #change to course ID   
COURSE_API_URL = f'{API_URL}/courses/{COURSE_ID}'
COURSE_NAME = json.loads(requests.get(COURSE_API_URL, headers = headers).text)['name']
print(COURSE_NAME)
print(COURSE_API_URL)

#Code segment to get list of all users and their groups
#Note the code stops after 100 groups because I did not need to code in a loop to fix that since I have fewer than 100 groups

#Store all group categories to a list
group_categories_list = pd.DataFrame({'Group_Category':[],
                                        'id':[]})
group_categories_raw = requests.get(f'{COURSE_API_URL}/group_categories?per_page=100', headers = headers)
group_categories_data = json.loads(group_categories_raw.text)
for group_category in group_categories_data:
    try:
        row = pd.DataFrame({'Group_Category':[str(group_category['name'])],
                            'id':[str(group_category['id'])]})
        group_categories_list = pd.concat([group_categories_list,row])
    except:
        print("Error pulling categories list")
#print(group_categories_list)

#pull all students in all groups
student_groups = pd.DataFrame({'sis_user_id':[]})
#print(student_groups)

for index, group_category in group_categories_list.iterrows():
    try:
        group_category_name = group_category['Group_Category']
        group_category_id = group_category['id']
        group_users = pd.DataFrame({'sis_user_id':[],
                            group_category_name:[]})
        
        group_list_raw = requests.get(f'{API_URL}/group_categories/{group_category_id}/groups?per_page=100', headers = headers)
        group_list_data = json.loads(group_list_raw.text)
        #print(group_list_data[1])
        for group in group_list_data:
            try:
                group_id = group['id']
                #print(group_id)
                group_raw = requests.get(f'{API_URL}/groups/{group_id}?include[]=users', headers = headers)
                group_data = json.loads(group_raw.text)
                #print(group_data)
                group_name = group_data['name']
                for user in group_data['users']:
                    try:
                        row = pd.DataFrame({'sis_user_id':[str(user['sis_user_id'])],
                                                group_category_name:[group_name]})
                        group_users=pd.concat([group_users,row])
                    except:
                        print("Error looping users")
            except:
                print("Error looping group list")
        #print(group_users)
        student_groups = pd.merge(student_groups, group_users, how ='outer', on = 'sis_user_id')
        #print(student_groups)
        print(f'Printing {group_category_name}')
    except:
        print("Error pulling groups")
print(f'Finished constructing dataframe. Printing to csv...')
csv_name = f'{COURSE_NAME} Groups.csv'
student_groups.to_csv(csv_name)
print(f'Printed groups to {csv_name}')
