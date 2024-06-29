import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_reviews(url):
    # Set up Selenium WebDriver
    driver = webdriver.Chrome()
    driver.get(url)
    
    # Accept cookies
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        cookie_button.click()
    except:
        print("Cookie button not found or not clickable")
    
    all_reviews = []
    
    while True:
        # Wait for the content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "bv-content-item"))
        )
        
        # Parse the page content
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract reviews
        reviews = soup.find_all('li', class_='bv-content-item')
        for review in reviews:
            review_text = review.find('div', class_='bv-content-summary-body-text')
            review_text = review_text.text.strip() if review_text else "N/A"
            
            rating_elem = review.find('span', class_='bv-rating-stars-container')
            rating = "N/A"
            if rating_elem:
                if 'title' in rating_elem.attrs:
                    rating = rating_elem['title'].split()[0]
                else:
                    rating_on = rating_elem.find('abbr', class_='bv-rating-stars-on')
                    if rating_on and 'title' in rating_on.attrs:
                        rating = rating_on['title'].split()[0]
            
            author_elem = review.find('span', class_='bv-author')
            author = author_elem.text.strip() if author_elem else "N/A"
            
            date_elem = review.find('span', class_='bv-content-datetime-stamp')
            date = date_elem.text.strip() if date_elem else "N/A"
            
            all_reviews.append({
                'text': review_text,
                'rating': rating,
                'author': author,
                'date': date
            })
        
        # Check if we're on the last page
        page_info = soup.find('div', class_='bv-content-pagination-pages-current')
        if page_info and '3221–3243 of 3243 Reviews' in page_info.text.strip():
            break
        
        # Click the next button
        try:
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span.bv-content-btn-pages-next"))
            )
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)  # Wait for the page to load
        except:
            print("Next button not found or not clickable")
            break
    
    driver.quit()
    return all_reviews

# Use the function
url = "https://ratings.bazaarvoice.com/index.html?merchant=kaercher"
reviews = scrape_reviews(url)

# Save the results to a CSV file
csv_filename = 'karcher_reviews.csv'
csv_headers = ['text', 'rating', 'author', 'date']

with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=csv_headers)
    writer.writeheader()
    for review in reviews:
        writer.writerow(review)

print(f"Total reviews scraped: {len(reviews)}")
print(f"Reviews saved to {csv_filename}")