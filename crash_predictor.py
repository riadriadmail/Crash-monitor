import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Set up logging - only to file, not console
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crash_monitor.log"),
    ]
)

def setup_driver():
    """Set up Chrome WebDriver with appropriate options"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # Add user agent to mimic real browser
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
    
    # Run in headless mode to avoid showing browser window
    chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def check_for_iframes(driver):
    """Check if there are iframes and switch to the relevant one"""
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    logging.info(f"Found {len(iframes)} iframes on the page")
    
    for i, iframe in enumerate(iframes):
        try:
            driver.switch_to.frame(iframe)
            # Check if the game element exists in this iframe
            elements = driver.find_elements(By.CLASS_NAME, "crash-game__counter")
            if elements:
                logging.info(f"Found game elements in iframe {i}")
                return True
            driver.switch_to.default_content()
        except Exception as e:
            logging.warning(f"Error checking iframe {i}: {e}")
            driver.switch_to.default_content()
    
    return False

def save_round_data(last_value):
    """Save the round data to a text file"""
    try:
        with open("crash_results.txt", "a") as file:
            file.write(f"{last_value}\n")
        print(f"Saved: {last_value}")  # Only show when a value is saved
    except Exception as e:
        logging.error(f"Error saving to file: {e}")

def monitor_crash_game(url, wait_time=10):
    """Monitor crash game and collect crash points"""
    print("Starting crash game monitor...")
    print("Navigating to game page...")
    
    driver = setup_driver()
    
    try:
        logging.info("Chrome WebDriver setup successfully")
        logging.info("Starting crash game monitor...")
        logging.info("Navigating to game page...")
        
        driver.get(url)
        
        # Wait for page to load completely
        logging.info("Waiting for page to load...")
        print("Waiting for page to load...")
        
        # Wait for either the game element or body to load
        try:
            WebDriverWait(driver, wait_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, "crash-game__counter"))
            )
            logging.info("Game counter element found directly")
            print("Game page loaded successfully!")
        except TimeoutException:
            logging.warning("Game counter not found directly. Checking for iframes...")
            print("Checking for iframes...")
            # Check if the element is inside an iframe
            if not check_for_iframes(driver):
                logging.warning("Game counter not found in iframes either. Trying alternative selectors...")
                print("Trying alternative selectors...")
                
                # Try different selectors for the counter
                selectors = [
                    (By.CLASS_NAME, "crash-game__counter"),
                    (By.CLASS_NAME, "crash-game_counter"),  # alternative spelling
                    (By.CSS_SELECTOR, "[class*='counter']"),
                    (By.CSS_SELECTOR, "[class*='crash']"),
                    (By.CSS_SELECTOR, "svg text"),  # SVG text elements often contain the counter
                ]
                
                element_found = False
                for by, selector in selectors:
                    try:
                        element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((by, selector))
                        )
                        logging.info(f"Found element using {by}: {selector}")
                        element_found = True
                        break
                    except (TimeoutException, NoSuchElementException):
                        continue
                
                if not element_found:
                    logging.error("Could not find any game elements. Please check the page structure.")
                    print("Error: Could not find game elements. Check crash_monitor.log for details.")
                    # Take a screenshot for debugging
                    driver.save_screenshot("page_debug.png")
                    logging.info("Screenshot saved as 'page_debug.png' for debugging")
                    return
        
        print("Monitoring started. Press Ctrl+C to stop.")
        print("Only the final crash values will be displayed:")
        print("-" * 30)
        
        # Initialize variables for tracking rounds
        previous_value = None
        last_round_value = None
        
        # Monitor the game continuously
        logging.info("Monitoring game for crash points...")
        
        while True:
            try:
                # Try different ways to get the multiplier value
                multiplier = None
                
                # Method 1: Direct class name
                try:
                    multiplier_element = driver.find_element(By.CLASS_NAME, "crash-game__counter")
                    multiplier = multiplier_element.text
                except NoSuchElementException:
                    pass
                
                # Method 2: SVG text elements
                if not multiplier:
                    try:
                        text_elements = driver.find_elements(By.CSS_SELECTOR, "svg text")
                        for element in text_elements:
                            text = element.text.strip()
                            if text and any(char.isdigit() or char == '.' for char in text):
                                multiplier = text
                                break
                    except NoSuchElementException:
                        pass
                
                if multiplier:
                    # Detect new round (value resets to 1.00x or similar)
                    if multiplier.startswith("1.00") or multiplier == "1.00x":
                        # If we have a previous value from the last round, save it
                        if last_round_value and last_round_value != "1.00x":
                            save_round_data(last_round_value)
                            last_round_value = None
                    
                    # Update the last value seen in the current round
                    if multiplier != previous_value:
                        last_round_value = multiplier
                        previous_value = multiplier
                
                time.sleep(0.5)  # Check every second
                    
            except KeyboardInterrupt:
                print("\nStopping monitor...")
                break
            except Exception as e:
                logging.warning(f"Error reading multiplier: {str(e)}")
                time.sleep(2)
        
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        print(f"Error: {e}. Check crash_monitor.log for details.")
        # Take screenshot on error
        driver.save_screenshot("error_screenshot.png")
        logging.info("Screenshot saved as 'error_screenshot.png'")
    finally:
        # Save any remaining value before exiting
        if last_round_value and last_round_value != "1.00x":
            save_round_data(last_round_value)
        
        driver.quit()
        logging.info("WebDriver closed successfully")
        print("WebDriver closed successfully")

if __name__ == "__main__":
    # Replace with the actual URL of the crash game
    GAME_URL = "https://gecwlsp6ylfo.pro/en/games/crash"  # Update this URL
    
    # Create or clear the results file at start
    open("crash_results.txt", "w").close()
    
    monitor_crash_game(GAME_URL)
    print("Monitoring ended")