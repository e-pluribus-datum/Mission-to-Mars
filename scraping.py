from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

# Run all 3 scraping functions
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_blurb = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    scraped_data = {
        "news_title": news_title,
        "news_paragraph": news_blurb,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return scraped_data

# Scrape Mars News
def mars_news(browser):
    # Visit the Mars NASA news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Handle errors
    try:
        slide_elem = news_soup.select_one('div.list_text')
        
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        
        # Use the parent element to find the paragraph text
        news_blurb = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_blurb

# Scrape featured image
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Handle errors
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

def mars_facts():
    # Handle errors
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        mars_df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    mars_df.columns=['Description', 'Mars', 'Earth']
    mars_df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return mars_df.to_html()

def hemispheres(browser):
    # Visit URL
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create list to hold the images and titles
    hemisphere_image_urls = []

    # Retrieve the image urls and titles for each hemisphere
    hemi_links = browser.find_by_css('a.product-item img')

    for i in range(len(hemi_links)):
        hemi_data = {}

        # Find ordinal image and click through
        browser.find_by_css('a.product-item img')[i].click()

        # Find sample image
        sample_elem = browser.find_by_text('Sample').first
        hemi_data['img_url'] = sample_elem['href']

        # Get the image title
        hemi_data['title'] = browser.find_by_css('h2.title').text

        # Append dictionary to list
        hemisphere_image_urls.append(hemi_data)

        # Send browser to previous page
        browser.back()

    return hemisphere_image_urls

# If running as script, print scraped data
if __name__ == "__main__":
    print(scrape_all())