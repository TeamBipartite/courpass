from selenium import webdriver
from selenium.webdriver.common.by import By


def get_calendar_info(url) -> list[str]:
    pre_and_coreq_html = []

    # Configure driver such that browser window opens in background
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    # Configure driver for Chrome browser
    driver = webdriver.Chrome(options=options)
    # Open Chrome browser at the given url
    driver.get(url)
    # Wait 5 seconds for the browser to load at the url
    driver.implicitly_wait(5)
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
