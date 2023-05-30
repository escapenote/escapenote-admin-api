import json
from time import sleep
from typing import List

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

from app.prisma import prisma
from app.models.scrapper import Scrapper


async def scrap_all_themes(scrappers: List[Scrapper]):
    result = list()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service("app/chromedriver"), options=options)
    wait = WebDriverWait(driver, 10)

    for scrapper in scrappers:
        try:
            driver.get(scrapper.url)
            wait.until(presence_of_element_located((By.TAG_NAME, "body")))
            wait.until(
                lambda driver: driver.execute_script("return document.readyState")
                == "complete"
            )
            sleep(1)

            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(Keys.END)
            sleep(1)
        except Exception as e:
            print("[error]", e)
            continue

        # XPath
        if scrapper.themeSelector and scrapper.themeSelector[0] == "/":
            wait.until(presence_of_element_located((By.XPATH, scrapper.themeSelector)))
            scrapped_theme_els = driver.find_elements(By.XPATH, scrapper.themeSelector)
        # CSS
        else:
            wait.until(
                presence_of_element_located((By.CSS_SELECTOR, scrapper.themeSelector))
            )
            scrapped_theme_els = driver.find_elements(
                By.CSS_SELECTOR, scrapper.themeSelector
            )
        scrapped_theme_names = list(
            map(lambda e: str(e.text).replace("\n", " ").strip(), scrapped_theme_els)
        )
        scrapped_theme_names.sort()

        themes = await prisma.theme.find_many(where={"cafeId": scrapper.cafeId})
        current_theme_names = list(map(lambda x: x.name, themes))
        current_theme_names.sort()

        different_theme_names = list()
        for current_theme_name in current_theme_names:
            if current_theme_name not in scrapped_theme_names:
                different_theme_names.append(current_theme_name)
        for scrapped_theme_name in scrapped_theme_names:
            if scrapped_theme_name not in current_theme_names:
                different_theme_names.append(scrapped_theme_name)
        different_theme_names = list(set(different_theme_names))
        different_theme_names.sort()

        result.append(
            {
                "scrapperId": scrapper.id,
                "currentThemes": json.dumps(current_theme_names),
                "scrappedThemes": json.dumps(scrapped_theme_names),
                "differentThemes": json.dumps(different_theme_names),
                "status": "SOMETHING_WRONG"
                if different_theme_names
                else "NOTHING_WRONG",
            }
        )

    await prisma.metric.delete_many()
    await prisma.metric.create_many(data=result)
