import os
import time
import sys
import platform
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
        
        # Determine the base directory for logs
        if getattr(sys, 'frozen', False):
            # Running as a bundled executable
            base_dir = os.path.dirname(sys.executable)
        else:
            # Running as a script
            base_dir = os.path.join(os.path.dirname(__file__), '..')
            
        log_dir = os.path.join(base_dir, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        self.log_file = os.path.join(log_dir, 'web_agent.log')
        # We don't initialize here to avoid opening a browser immediately on startup
        # self._initialize_driver()

    def _log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")

    def _initialize_driver(self, headless=False):
        """Initializes the Chrome WebDriver. Defaulting to visible mode for Dad's oversight."""
        try:
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            # Use a more realistic user agent to avoid bot detection
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
            
            # Ignore certificate errors for smoother browsing
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--allow-running-insecure-content')
            
            # Keep the browser open after the script finishes if not in headless mode
            if not headless:
                options.add_experimental_option("detach", True)
            
            if platform.system() == "Windows":
                # On Windows, let webdriver-manager handle the driver automatically
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service as ChromeService
                
                try:
                    # Try to install the driver
                    driver_path = ChromeDriverManager().install()
                    service = ChromeService(driver_path)
                    self.driver = webdriver.Chrome(service=service, options=options)
                except Exception as manager_err:
                    self._log(f"WebDriverManager failed: {manager_err}. Trying direct initialization.")
                    # Fallback to direct initialization if manager fails
                    self.driver = webdriver.Chrome(options=options)
            else:
                # On Linux (Sandbox environment), use the pre-installed Chromium/ChromeDriver
                options.binary_location = "/usr/bin/chromium-browser"
                service = Service("/usr/bin/chromedriver")
                self.driver = webdriver.Chrome(service=service, options=options)
                
            self._log("WebDriver initialized successfully.")
        except Exception as e:
            self._log(f"Error initializing WebDriver: {e}")
            # Final Fallback: Try to initialize with minimal options
            try:
                fallback_options = webdriver.ChromeOptions()
                if headless: fallback_options.add_argument('--headless')
                self.driver = webdriver.Chrome(options=fallback_options)
                self._log("WebDriver initialized via final fallback.")
            except Exception as e2:
                self._log(f"Final fallback initialization failed: {e2}")
                self.driver = None

    def close(self):
        """Closes the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            self._log("WebDriver closed.")

    def navigate_and_scrape(self, url: str) -> str:
        """Navigates to a URL and returns the text content."""
        if not self.driver:
            self._initialize_driver(headless=False)
            
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
            # Return the first 3000 characters of text so the LLM can actually see the data
            return f"SUCCESS: I have scraped the content from {url}. Here is the content for your analysis:\n\n{text[:3000]}"
            
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
        """
        if not self.driver:
            self._initialize_driver(headless=False)
        
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
        """
        if not self.driver:
            self._initialize_driver(headless=False)
        
        if not self.driver:
            return "FAILURE: Web agent is not initialized."
        
        try:
            by_type = getattr(By, selector_type.upper(), None)
            if not by_type:
                # Try to find by text if it's not a standard selector
                try:
                    element = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{selector_value}')]")
                    element.click()
                    return f"SUCCESS: Clicked element containing text '{selector_value}'"
                except:
                    return f"FAILURE: Invalid selector type '{selector_type}'."

            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_type, selector_value))
            )
            
            # Scroll into view before clicking
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            element.click()
            self._log(f"Clicked element {selector_type}={selector_value}")
            return f"SUCCESS: I have clicked the element with selector {selector_type}='{selector_value}'."
            
        except Exception as e:
            self._log(f"Error clicking element: {e}")
            return f"FAILURE: Could not find or click element {selector_type}='{selector_value}'. Error: {e}"

    def scroll_page(self, direction: str = "down") -> str:
        """Scrolls the page up or down."""
        if not self.driver:
            self._initialize_driver(headless=False)
            
        if not self.driver: return "FAILURE: No driver."
        try:
            if direction.lower() == "down":
                self.driver.execute_script("window.scrollBy(0, 500);")
            else:
                self.driver.execute_script("window.scrollBy(0, -500);")
            return f"SUCCESS: Scrolled {direction}."
        except Exception as e:
            return f"FAILURE: {e}"

    def switch_to_visible_mode(self):
        """Restarts the driver in visible mode (redundant now but kept for compatibility)."""
        self.close()
        self._initialize_driver(headless=False)
        return "SUCCESS: Browser is now visible. Dad, you can take over if you need to log in!"

# Ensure the driver is closed when the program exits
import atexit
web_agent_instance = OracleWebAgent()
atexit.register(web_agent_instance.close)
