from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import NoSuchDriverException
from selenium.webdriver.remote.webdriver import WebDriver

WEBDRIVERS  = {webdriver.ChromeOptions: webdriver.Chrome, 
               webdriver.EdgeOptions: webdriver.Edge,
               webdriver.SafariOptions: webdriver.Safari,
               webdriver.FirefoxOptions: webdriver.Firefox}

def get_calendar_info(url) -> list[str]:
    driver = None

    for driver_options in WEBDRIVERS:
        try:
           options = driver_options()
           # ensure browser opens in backgound
           options.add_argument("--headless=new")
           driver = WEBDRIVERS[driver_options](options = options)
           # if we get here, we found an available driver
           break
        except Exception as e:
            # TODO: may need a better message here (maybe?)
            if type(e) is not NoSuchDriverException:
                print(e)

    if not driver:
        print("Sorry, you do not have a browser that supports this application.")
        print("Please download Chrome (or any Chrome-based browser), Edge, Safari, or Firefox to use this application.")
        return []

    return scrape_calendar_page(driver)

def scrape_calendar_page(driver: WebDriver) -> list[str]:
    pre_and_coreq_html = []
     # Open browser at the given url
    driver.get(url)
    # Wait (up to) 10 seconds for the browser to load at the url
    driver.implicitly_wait(10)
    # Search for <span> who has a direct child of tag <h3> containing Prerequisites or Pre- or corequisites
    cal_sections = driver.find_elements(By.XPATH, "//span[h3[contains(text(), 'Prerequisites') or contains(text(), 'Pre- or corequisites')]]")

    for section in cal_sections:
        pre_and_coreq_html.append(section.get_attribute("innerHTML"))
    
    return pre_and_coreq_html



if __name__ == '__main__':
    # TODO: remove mock urls
    # CASE 1: Pre and Coreqs present
    url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/ryzikO6QN?q=CSC%20361&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computer%20Communications%20and%20Networks&bcItemType=courses"
    # CASE 2: No pre or coreqs
    # url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/HJZck_TmV?q=CSC105&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Computers%20and%20Information%20Processing&bcItemType=courses"
    # CASE 3: Prereqs only
    #url = "https://www.uvic.ca/calendar/undergrad/index.php#/courses/r1l00yY67E?q=SENG265&&limit=20&skip=0&bc=true&bcCurrent=&bcCurrent=Software%20Development%20Methods&bcItemType=courses"


    # TODO: remove for loop below once implementation complete
    pre_and_coreqs = get_calendar_info(url)
    for idx in range(len(pre_and_coreqs)):
        print(f"pre_and_coreqs[{idx}] =")
        print(pre_and_coreqs[idx])
