from itertools import count

from bs4 import BeautifulSoup
from pprint import pprint

import requests
from bs4 import BeautifulSoup
import re

import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IMDBScraper:
    def __init__(self, headless_mode: bool = True):
        """
        Initialize the IMDBScraper
        :param headless_mode: Whether to run the scraper in headless mode (no browser window)
        """

        self.page_source = None
        self._setup_driver(headless_mode=headless_mode)

    def load_page(self, present_class_name: str, url: str = "https://www.imdb.com/chart/top/"):
        """
        Load a page and wait until the element with the class 'present_class_name' is present
        :param present_class_name: The class name of the element to wait for, eg. 'ipc-metadata-list-summary-item'
        :param url: The URL of the page to load
        """

        self.driver.get(url)

        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, present_class_name))
            WebDriverWait(self.driver, 10).until(element_present)
            print("Page loaded successfully!")
        except TimeoutException:
            print("Loading took too much time!")

        time.sleep(5)

        self.page_source = self.driver.page_source

    def scrape_top_movies_titles(self) -> list:
        """
        Scrape the top movies from the page and return a list of movie titles and URLs
        :return: List of movie titles
        """
        soup = BeautifulSoup(self.page_source, "html.parser")
        elements = soup.find_all('li', class_='ipc-metadata-list-summary-item')

        movies = []
        ranking = count(1)

        for element in elements:
            # tag with the movie link
            link_tag = element.find('a', class_='ipc-lockup-overlay')

            if link_tag and 'href' in link_tag.attrs:
                # create link
                movie_path = link_tag['href'].split('?ref_=chttp_i_')[0]
                full_url = f"https://www.imdb.com{movie_path}"

                # Extract title from aria-label attribute if available
                title = link_tag.get('aria-label', '').replace('View title page for ',
                                                               '') if 'aria-label' in link_tag.attrs else 'Unknown'

                # Store movie info
                movies.append({
                    'ranking': next(ranking),
                    'title': title,
                    'url': full_url
                })

        return movies

    def scrape_movie_details(self, url: str) -> dict:
        """
        Scrape the details of a movie from the page
        :param url: url of the movie, eg 'tt0133093' for Matrix
        :return: Dictionary containing the movie details
        """
        self.driver.get(url)

        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'hero__primary-text'))
            WebDriverWait(self.driver, 10).until(element_present)
            print(f"{url} loaded successfully!")
        except TimeoutException:
            print(f"Loading {url} took too much time!")

        time.sleep(1)

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # Extract the title
        title = soup.find('span', class_='hero__primary-text').text
        release_date = soup.select_one(
            'div.sc-9a2a0028-3.bwWOiy a.ipc-link.ipc-link--baseAlt.ipc-link--inherit-color').text

        imdb_rating = soup.find('span', class_='sc-d541859f-1 imUuxf').text
        imdb_number_of_ratings = soup.find('div', class_='sc-d541859f-3 dwhNqC').text


        # if populaerity_element exists (does not exist on https://www.imdb.com/title/tt0986264/ at the time being)
        popularity_element = soup.find('div', class_='sc-39d285cf-1 dxqvqi')
        popularity = popularity_element.text if popularity_element else ''

        # Extract the genres
        genres = [genre.text for genre in soup.find_all('a', class_='ipc-chip ipc-chip--on-baseAlt')]

        # Extract directors
        directors = []

        details = soup.find('div', class_='sc-70a366cc-2 bscNnP')
        directors_and_writers = details.find_all('li',
                                                 class_='ipc-metadata-list__item ipc-metadata-list__item--align-end')
        for item in directors_and_writers:
            label_elem = item.find('span', class_='ipc-metadata-list-item__label')
            if not label_elem:
                continue

            label = label_elem.text.strip()

            # Find all links within the content area
            links = item.find_all('a', class_='ipc-metadata-list-item__list-content-item')
            names = [link.text for link in links]

            if "Director" in label:
                directors = names

        cast = self._scrape_full_cast_and_cast(url)
        return {
            'title': title,
            'release_date': release_date,
            'imdb_rating': imdb_rating,
            'imdb_number_of_ratings': imdb_number_of_ratings,
            'popularity': popularity,
            'genres': genres,
            'directors': directors,
            'cast': cast
        }

    def _scrape_full_cast_and_cast(self, url: str) -> list:
        """
        Scrape the full cast and cast of a movie from the page
        :param url: url of the movie
        :return: list of cast and cast members
        """
        # url = f"https://www.imdb.com/title/{url}/fullcredits"
        url = f"{url}fullcredits"
        self.driver.get(url)

        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'cast_list'))
            WebDriverWait(self.driver, 10).until(element_present)
            print(f"{url} loaded successfully!")
        except TimeoutException:
            print(f"Loading {url} took too much time!")

        time.sleep(3)

        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        # cast list
        cast_list = soup.find('table', class_='cast_list')
        cast = []

        if cast_list:
            for row in cast_list.find_all('tr', class_=lambda c: c in ['odd', 'even']):
                # actor name
                actor = row.find('td', class_='primary_photo').find('img')['alt']
                cast.append(actor)

        return cast

    def _setup_driver(self, headless_mode: bool = True):
        if headless_mode:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
            options.add_argument("--enable-javascript")

        self.driver = webdriver.Chrome(options=options) if headless_mode else webdriver.Chrome()
