import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class OracleWebAgent:
    """
    An autonomous web agent using Selenium to control a real browser.
    This allows for true web scraping, dynamic content handling, and form submission.
    """
    def __init__(self):
        self.driver = None
        self.log_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'web_agent.log')
        self._initialize_driver()

    def _log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

    def _initialize_driver(self):
        """Initializes the Chrome WebDriver in headless mode."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.binary_location = "/usr/bin/chromium-browser"
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Use the system's ChromeDriver which matches the installed Chromium version
            service = Service("/usr/bin/chromedriver")
            self.driver = webdriver.Chrome(service=service, options=options)
            self._log("WebDriver initialized successfully.")
        except Exception as e:
            self._log(f"Error initializing WebDriver: {e}")
            self.driver = None

    def close(self):
        """Closes the WebDriver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
            self._log("WebDriver closed.")

    def navigate_and_scrape(self, url: str) -> str:
        """Navigates to a URL and returns the parsed text content."""
        if not self.driver:
            return "FAILURE: Web agent is not initialized. Check logs for driver error."

        try:
            self.driver.get(url)
            self._log(f"Navigated to: {url}")
            
            # Wait for the body content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get the page source and use BeautifulSoup for clean text extraction
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            
            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            self._log(f"Scraped {len(text)} characters of text from {url}")
            return f"SUCCESS: I have scraped the content from {url}. The content is ready for analysis."
            
        except Exception as e:
            self._log(f"Error during navigation and scraping: {e}")
            return f"FAILURE: I encountered an error while trying to scrape {url}. Error: {e}"

    def get_current_page_text(self) -> str:
        """Returns the text of the currently loaded page for the LLM to analyze."""
        if not self.driver:
            return "FAILURE: No page is currently loaded."
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text

    def fill_form_element(self, selector_type: str, selector_value: str, value: str) -> str:
        """
        Fills a single form element based on a selector.
        NOTE: This method should only be called after user confirmation.
        """
        if not self.driver:
            return "FAILURE: Web agent is not initialized."
        
        try:
            by_type = getattr(By, selector_type.upper(), None)
            if not by_type:
                return f"FAILURE: Invalid selector type '{selector_type}'. Must be ID, NAME, XPATH, etc."

            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((by_type, selector_value))
            )
            
            element.clear()
            element.send_keys(value)
            self._log(f"Filled element {selector_type}={selector_value} with value: {value}")
            return f"SUCCESS: I have filled the element with selector {selector_type}='{selector_value}'."
            
        except Exception as e:
            self._log(f"Error filling form element: {e}")
            return f"FAILURE: Could not find or fill element {selector_type}='{selector_value}'. Error: {e}"

    def click_element(self, selector_type: str, selector_value: str) -> str:
        """
        Clicks a single element based on a selector.
        NOTE: This method should only be called after user confirmation.
        """
        if not self.driver:
            return "FAILURE: Web agent is not initialized."
        
        try:
            by_type = getattr(By, selector_type.upper(), None)
            if not by_type:
                return f"FAILURE: Invalid selector type '{selector_type}'. Must be ID, NAME, XPATH, etc."

            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_type, selector_value))
            )
            
            element.click()
            self._log(f"Clicked element {selector_type}={selector_value}")
            return f"SUCCESS: I have clicked the element with selector {selector_type}='{selector_value}'."
            
        except Exception as e:
            self._log(f"Error clicking element: {e}")
            return f"FAILURE: Could not find or click element {selector_type}='{selector_value}'. Error: {e}"

# Ensure the driver is closed when the program exits
import atexit
web_agent_instance = OracleWebAgent()
atexit.register(web_agent_instance.close)
