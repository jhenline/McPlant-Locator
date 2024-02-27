from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Set up headless browser
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run headless
chrome_options.add_argument("--disable-gpu")  # Disable GPU usage

# Path to chromedriver executable
chromedriver_path = "/opt/homebrew/bin/chromedriver"

# Start headless browser
service = Service(chromedriver_path)
service.start()
driver = webdriver.Remote(service.service_url, options=chrome_options)

# URL of the webpage containing zip codes
url = "https://www.mcdonalds.com/us/en-us/mcplant-locations.html"

# Visit the webpage
driver.get(url)

# Find all rows in the table
rows = driver.find_elements(By.XPATH, "//table[@border='1']/tbody/tr")

# Extract zip codes from each row
zip_codes = []
for row in rows:
    cells = row.find_elements(By.TAG_NAME, "td")
    if len(cells) >= 4:
        zip_code = cells[3].text.strip()  # Assuming zip code is in the 4th column
        zip_codes.append(zip_code)

# Display the extracted zip codes
print("Extracted Zip Codes:")
for zip_code in zip_codes:
    print(zip_code)

# Close the headless browser
driver.quit()
