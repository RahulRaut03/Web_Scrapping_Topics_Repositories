import requests                     #import Request library (to Download the webpage)
from bs4 import BeautifulSoup       #import beautifulsoup   (to parse the data)
import pandas as pd                 #import Pandas library  (to create csv file)
import os

def get_topic_titles(doc):
    selection_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
    topic_title_tags = doc.findAll('p', {'class': selection_class})

    topic_titles = []
    for tag in topic_title_tags:
        topic_titles.append(tag.text)  # this line will append topic names in topic_titles list
    return topic_titles

def get_topic_desc(doc):
    desc_selection = 'f5 color-fg-muted mb-0 mt-1'
    topic_desc_tags = doc.findAll('p', {'class': desc_selection})

    topic_desc = []
    for tag in topic_desc_tags:
        topic_desc.append(tag.text.strip())  # this line will append topic desc in topic_desc list
    return topic_desc

def get_topic_url(doc):
    link_selection = 'no-underline flex-1 d-flex flex-column'
    topic_link_tags = doc.findAll('a', {'class': link_selection})

    topic_urls = []
    base_url = 'https://github.com'
    for tag in topic_link_tags:
        topic_urls.append(base_url + tag['href'])
    return topic_urls

def scrape_topics():
    topics_url = 'https://github.com/topics'    # put the url which you want to scrap
    response = requests.get(topics_url)         # this line will download the given webpage and store it in response

   # with open('webpage.html', 'w', encoding='UTF-8')as f:
    #    f.write(response.text)

    if response.status_code != 200:             #check for the successful response
        raise Exception('Failed to load url {}'.format(topics_url))

    doc = BeautifulSoup(response.text, 'html.parser')

    topics_dict = {'Title': get_topic_titles(doc),
                   'Description': get_topic_desc(doc),
                   'Url': get_topic_url(doc)}  # this line will create a dictionaries from the list

    #topic_df = pd.DataFrame(topics_dict)
    #topic_df.to_csv('Topics.csv')
    return  pd.DataFrame(topics_dict)
#print(scrape_topics())

def parse_star_count(stars_str):
    stars_str = stars_str.strip()
    if stars_str[-1] == 'k':
        return int(float(stars_str[:-1]) * 1000)

def get_repo_info(repo_tags,star_tags):
    #returns all the information about the repository
    base_url = 'https://github.com'
    a_tag = repo_tags.findAll('a')
    #print(a_tag)
    repo_username = a_tag[0].text.strip()
    #print(repo_username)
    repo_name = a_tag[1].text.strip()
    repo_url = base_url + a_tag[1]['href']
    repo_stars = parse_star_count(star_tags.text.strip())
    return repo_username, repo_name, repo_url, repo_stars


def get_topic_repos(topic_url):
    #download the page
    response = requests.get(topic_url)
    #check successful response
    if response.status_code != 200:
        raise Exception('Failed to load url {}'.format(topic_url))
    #parse using beautifulsoup
    topic_doc = BeautifulSoup(response.text, 'html.parser')
    #get h1 tags containing repo title,username,url,stars count
    h1_sel = 'f3 color-fg-muted text-normal lh-condensed'
    repo_tags = topic_doc.findAll('h3', {'class': h1_sel})

    star_sel = 'Counter js-social-count'
    star_tags = topic_doc.findAll('span', {'class': star_sel})

    topic_repos_dec = {'Username': [],
                       'Repo_name': [],
                       'Repo_url': [],
                       'Stars_count': []}
    #get repo info
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], star_tags[i])
        topic_repos_dec['Username'].append(repo_info[0])
        topic_repos_dec['Repo_name'].append(repo_info[1])
        topic_repos_dec['Repo_url'].append((repo_info[2]))
        topic_repos_dec['Stars_count'].append((repo_info[3]))
    return pd.DataFrame(topic_repos_dec)


def scrape_topic(topic_url, path):
    if os.path.exists(path):
        print("The file {} already exists....Skipping....".format(path))
        return
    topics_df = get_topic_repos(topic_url)
    topics_df.to_csv(path, index=None)



def scrape_topics_repos():
    print("Scrapping list of topics...")
    topics_df = scrape_topics()

    #create a folder
    os.makedirs('Data', exist_ok=True)

    for index, row in topics_df.iterrows():
        #print(row['Url'], row['Title'])
        print('Scrapping top repositories for "{}"'.format(row['Title']))
        scrape_topic(row['Url'], 'Data/{}.csv'.format(row['Title']))

scrape_topics_repos()