from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time, asyncio

# Settings
CHROME_PATH = r"/home/jack/jackbot/chromedriver"

# Testing
# _HTML = open("example_page.html", "r").read()

class LostCrawler:
	def __init__(self, url = 'https://lostmerchants.com'):
		chrome_options = Options()
		chrome_options.add_argument("--headless")
		chrome_options.add_argument("--log-level=3");

		self.driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=CHROME_PATH)
		self.driver.get(url)
		self.action = ActionChains(self.driver)

		self.handlers = []

	def addHandler(self, handler):
		self.handlers.append(handler)

	async def start(self, region="NA East", server="Avesta", poll_interval = 10):
		# Helper methods
		def waitForId(driver, id):
			element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.ID, id))
			)
			return element
		def waitForText(driver, id, txt):
			element = WebDriverWait(driver, 10).until(
				EC.text_to_be_present_in_element((By.ID, id), txt)
			)
			return element

		def actionSelect(action, element, option):
			action.click(on_element = element)
			action.perform()
			
			sel = Select(element)
			sel.select_by_visible_text(option)

		# Wait til it loads to server select page
		e_region = waitForId(self.driver, "severRegion")
		e_server = waitForId(self.driver, "server")

		# Select region & server
		actionSelect(self.action, e_region, region)
		actionSelect(self.action, e_server, server)

		# Analyze page
		while True:
			html = self.driver.page_source
			# html = _HTML
			for h in self.handlers:
				await h(html)
			await asyncio.sleep(poll_interval)

	async def close(self):
		self.driver.close()

		
if __name__ == "__main__":
	crawler = LostCrawler()
	async def h(html):
		print("tick")
		print(html)
	crawler.addHandler(h)

	loop = asyncio.get_event_loop()
	loop.run_until_complete(crawler.start())
	loop.run_until_complete(crawler.close())
	loop.close()
