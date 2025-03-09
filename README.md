
# imdb-scraper-visualization

## Overview
[IMDb](https://www.imdb.com/) scraper that fetches data from [top 250 movies](https://www.imdb.com/chart/top/) using Selenium (for loading a page) and Beautiful Soup (for reading html code), such as title, release date, cast, genres, ratings etc. Using Pandas, it processes data, that will later be loaded into local databse using SQLite. Using database querying and matplotlib, we can create interesting graphs. Everything is shown and explained in `main.ipynb`. Also, there's no need to scrape data youself, there are files in `csvs` folder that can be read directly by script.




## Installation

```bash
# Clone the repository
git clone https://github.com/Spacoon/imdb-scraper-visualization/

# Navigate to the directory
cd imdb-scraper-visualization

# Create virtual environment
python -m venv venv

# if it throws security error try:
# Set-ExecutionPolicy Unrestricted -Scope Process

venv/Scripts/activate # on Windows
source env/bin/activate # on Mac

# Install dependencies
pip install -r requirements.txt
```

## Usage
Follow `main.ipynb` step-by-step.
