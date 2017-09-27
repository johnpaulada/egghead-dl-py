# -*- coding: utf-8 -*-

import time
import re
import os
import urllib2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome()
driver.wait = WebDriverWait(driver, 10)

def open_page(link):
    driver.get(link)

def enter_credentials(username, password, username_field_id, password_field_id):
    number_field = driver.find_element_by_id(username_field_id)
    number_field.send_keys(username)

    password_field = driver.find_element_by_id(password_field_id)
    password_field.send_keys(password)

    login_form = driver.find_element_by_tag_name('form')
    login_form.submit()

def download_links(links_url):
    links = get_file_lines(links_url)

    if not os.path.exists(COURSES_DIR):
        os.mkdir(COURSES_DIR)
    os.chdir(COURSES_DIR)

    for link in links:
        download_series(link)

def download_series(link):
    try:
        open_page(link)
        end_of_url = get_end_of_url(link)
        series_title = end_of_url.replace('-', ' ').upper()
        sanitized_title = sanitize_filename(series_title)

        print("Downloading {title}...".format(title = series_title))

        if not os.path.exists(sanitized_title):
            os.mkdir(sanitized_title)
        os.chdir(sanitized_title)

        episode_links = driver.find_elements_by_css_selector('.index__courseInfoLessonList__BotOf a.mb2')
        episodes = get_episodes(episode_links)
        download_episodes(episodes)
        os.chdir('..')
    except TimeoutException:
        os.chdir('..')
        download_series(link)

def get_episodes(episode_links):
    episodes = []

    for episode_link in episode_links:
        title = episode_link.text
        link = episode_link.get_attribute('href')
        episode = {'title': title, 'link': link}
        episodes = episodes + [episode]

    return episodes

def download_episodes(episodes):
    for index, episode in enumerate(episodes):
        download_episode(episode, index+1)

def download_episode(episode, index):
    extracted_title = episode.get('title')
    sanitized_title = sanitize_filename(extracted_title)
    title = "{index}. {title}".format(index=index, title=sanitized_title)
    video_filename = title + ".mp4"
    
    if not os.path.exists(video_filename):
        link = episode.get('link')
        print("  Downloading {title}...".format(title = title))
        open_page(link)
        download_link = driver.find_element_by_css_selector('a.index__downloadHdButton__3sXG2')
        video_url = download_link.get_attribute('href')
        save_video(video_filename, video_url)

def save_video(video_filename, video_url):
    response = urllib2.urlopen(video_url)
    final_url = response.geturl()
    video_file = urllib2.urlopen(final_url)
    video_data = video_file.read()
    if not os.path.exists(video_filename):
        with open(video_filename, "wb") as file_writer:
            file_writer.write(video_data)

def get_file_lines(url):
    lines = []

    for line in open(url):
        if line != '':
            lines = lines + [line]

    return lines

def get_end_of_url(url):
    end_of_url_pattern = '(?<=/)[\\w|\-]*$'
    end_of_url = re.findall(end_of_url_pattern, url)[0]

    return end_of_url

def sanitize_filename(filename):
    as_utf8 = to_utf8(filename)
    valid_characters_only = remove_invalid_characters(as_utf8)
    sanitized_filename = valid_characters_only

    return sanitized_filename

def to_utf8(s):
    return s.encode('utf8')

def remove_invalid_characters(s):
    character_translations = [ (r'\/', '-'), (r'–', '-'), (r'’', "'") ]
    for invalid, valid in character_translations:
        s = re.sub(invalid, valid, s)

    return s

LOGIN_URL = 'https://egghead.io/users/sign_in'
USERNAME_FIELD_ID = "user_email"
PASSWORD_FIELD_ID = "user_password"
LINKS_URL = "links.txt"
COURSES_DIR = 'courses'
USERNAME_INDEX = 0
PASSWORD_INDEX = 1
CREDENTIALS = get_file_lines('credentials')
USERNAME = CREDENTIALS[USERNAME_INDEX]
PASSWORD = CREDENTIALS[PASSWORD_INDEX]

open_page(LOGIN_URL)
enter_credentials(USERNAME, PASSWORD, USERNAME_FIELD_ID, PASSWORD_FIELD_ID)
download_links(LINKS_URL)