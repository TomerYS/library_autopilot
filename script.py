# Import necessary modules
from datetime import datetime, timedelta
import logging
import os
import schedule
import time
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

# Define constants
CHROME_PATH = "/usr/bin/chromedriver"
LOGIN_URL = "https://schedule.tau.ac.il/scilib/Web/index.php?redirect="
WAITING_PERIOD = 10

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('room_reservation.log'), logging.StreamHandler()])

def initialize_webdriver():
    """Initializes and returns the webdriver."""
    options = ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(CHROME_PATH)
    return webdriver.Chrome(service=service, options=options)

def authenticate_user(driver, username, password):
    """Logs the user into the scheduling system."""
    driver.get(LOGIN_URL)
    try:
        username_field = WebDriverWait(driver, WAITING_PERIOD).until(EC.presence_of_element_located((By.ID, 'email')))
        password_field = WebDriverWait(driver, WAITING_PERIOD).until(EC.presence_of_element_located((By.ID, 'password')))
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button = WebDriverWait(driver, WAITING_PERIOD).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-box"]/div[4]/button')))
        login_button.click()
        WebDriverWait(driver, WAITING_PERIOD).until(EC.presence_of_element_located((By.ID, 'navSignOut')))
        logging.info("Successfully logged in.")
    except Exception as e:
        logging.error(f"Login error: {str(e)}")
        raise e

def wait_for_next_hour():
    """Waits until the beginning of the next hour."""
    current_time = datetime.now()
    next_hour = current_time.replace(minute=0, second=0) + timedelta(hours=1)
    wait_seconds = (next_hour - current_time).total_seconds()
    wait_seconds += 1  # Add 1 second to ensure the next hour has started
    logging.info(f"Waiting {wait_seconds} seconds until the next round hour.")
    time.sleep(wait_seconds)

def wait_for_next_hour_minus_100sec():
    """Waits until one minute before the next hour."""
    current_time = datetime.now()
    next_hour = current_time.replace(minute=0, second=0) + timedelta(hours=1)
    wait_seconds = (next_hour - current_time).total_seconds()
    wait_seconds -= 100  # Add 1 second to ensure the next hour has started
    logging.info(f"Waiting {wait_seconds} seconds until the next round hour.")
    time.sleep(wait_seconds)

def reserve_room(driver, username, password, room=None):
    """Function to reserve a room"""
    wait_for_next_hour()
    logging.info("Reserving room...")
    authenticate_user(driver, username, password)

    desired_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d') # Getting date for the next week
    desired_hour = (datetime.now() - timedelta(hours=1)).strftime('%H:00') # Getting time for last hour
    
    # for non headless mode:
                #desired_hour = (datetime.now() - timedelta(hours=1)).strftime('%I:00 %p')
                
                # If desired_hour starts with 0, remove it
                # if desired_hour[0] == '0':
                #     desired_hour = desired_hour[1:]
        
    # Room preference list
    room_list = [29,128,126,125,127,28,24,25,23,26]

    # Try each room in the preference list
    for room in room_list:
        try:
            # Navigate to room reservation page
            driver.get(f"https://schedule.tau.ac.il/scilib/Web/reservation.php?rid={room}&sid=3&rd={desired_date}&sd={desired_date}%2019%3A00%3A00&ed={desired_date}%2020%3A00%3A00")
            
            time.sleep(1)
            logging.info(f"current url: {driver.current_url}")

            # Select desired time and submit reservation
            time_menu = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'BeginPeriod')))
            time_menu.click()
            if time_menu is not None:
                logging.info("Time menu located.")
            else:  
                logging.error("Time menu not located.")
            time.sleep(0.5)
            Select(time_menu).select_by_visible_text(desired_hour)
            time_menu.click()
            
            # Click create button
            create_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'btnCreate')))
            if create_button is not None:
                logging.info("create button located.")
            else:  
                logging.error("create button not located.")
            WebDriverWait(driver, 10).until_not(EC.presence_of_element_located((By.CSS_SELECTOR, '.blockUI.blockOverlay')))
            create_button.click()

            time.sleep(1.5)
            
            # If reservation was successful, return room and reference number
            reference_number_element = driver.find_element(By.ID, 'reference-number')
            reference_number = reference_number_element.text if reference_number_element else None
            if reference_number_element:
                logging.info(f"Room {room} is available. refetence number:{reference_number}.")
                return room, reference_number
        except Exception as e:
            logging.info(f"Error occurred when reserving room {room}. Trying next room...\n \n {str(e)} \n \n")
            driver.quit()

    # If no room could be reserved, return None, None
    driver.quit()
    return None, None


def update_reservation(username, password, room, reference_number):
    """Function to update a room reservation"""
    try:
        logging.info("Wait for the next hour - 100 seconds.")
        wait_for_next_hour_minus_100sec()
        logging.info("Initialize WebDriver.")
        driver = initialize_webdriver()
        logging.info("WebDriver initialized.")
        logging.info("Authenticate user.")
        authenticate_user(driver, username, password)
        logging.info("User authenticated.")
        logging.info("Wait for the next hour.")
        wait_for_next_hour()
        desired_hour = (datetime.now()).strftime('%H:00') # Getting time for last hour
        logging.info(f"Desired hour: {desired_hour}.")
        driver.save_screenshot('1.png')

        # Navigate to reservation update page
        logging.info(f"Navigate to reservation page: https://schedule.tau.ac.il/scilib/Web/reservation.php?rn={reference_number}.")
        driver.get(f"https://schedule.tau.ac.il/scilib/Web/reservation.php?rn={reference_number}")
        logging.info(f"Navigated to reservation page. Current URL: {driver.current_url}")
        driver.save_screenshot('2.png')

        try:
            # Select desired ending time and submit update
            logging.info("Locate time menu.")
            time_menu = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'EndPeriod')))
            logging.info("Time menu located.")
            time_menu.click()
            driver.save_screenshot('3.png')

            # Locate and click desired ending time
            logging.info("Locate and click desired ending time.")
            desired_option = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//option[text()='{desired_hour}']")))
            desired_option.click()
            driver.save_screenshot('4.png')

            # Click update button
            logging.info("Locate update button.")
            update_button = WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form-reservation"]/div[1]/div[2]/div/button[2]')))
            logging.info("Update button located.")
            update_button.click()
            driver.save_screenshot('5.png')

            # If reservation was successful, return room and reference number
            reference_number_element = driver.find_element(By.ID, 'reference-number')
            reference_number = reference_number_element.text if reference_number_element else None
            if reference_number_element:
                logging.info(f"Room {room} was updated. refetence number:{reference_number}.")
                return room, reference_number

        except Exception as e:
            logging.error(f"Error occurred while updating room {room} reservation. Stacktrace:")
            logging.error(traceback.format_exc())

        finally:
            logging.info("Quit driver.")
            driver.save_screenshot('6.png')
            driver.quit()

    except Exception as e:
        logging.error(f"Error occurred in update_reservation function room {room}. Stacktrace:")
        logging.error(traceback.format_exc())

    return None, None


def run_scheduled_job(username, password):
    """Function to run as scheduled job"""
    logging.info("Starting job...")
    driver = initialize_webdriver()
    try:
        # Reserve room for 1st hour
        room, reference_number = reserve_room(driver, username, password)

        # If reservation was successful, update to add 2nd hour
        if room is not None:
            room, reference_number = update_reservation(username, password, room, reference_number)
        
        # If update was successful, update to add 3rd hour
        if room is not None:
            reference_number = update_reservation(username, password, room, reference_number)
    except Exception as e:
        logging.error(f"Error occurred: \n \n{str(e)} \n \n")

    finally:
        logging.info(f"Job completed. Next job scheduled at: {schedule.next_run()}")


def get_seconds_until_next_job():
    """Function that returns the number of seconds until the next scheduled pending job"""
    return (schedule.next_run() - datetime.now()).total_seconds()

def schedule_and_run_jobs():
    """Main function to schedule and run the job"""
    username = os.environ.get('ROOM_RESERVATION_USERNAME')  # Read username from environment variable
    password = os.environ.get('ROOM_RESERVATION_PASSWORD')  # Read password from environment variable
    #schedule.every().wednesday.at("15:58").do(run_scheduled_job, username, password)
    update_reservation(username, password, 29, "647744d8ce4f6394698804")
    logging.info(f"Next job scheduled at: {schedule.next_run()}")
    while True:
        sleep_duration = get_seconds_until_next_job()
        logging.info(f"Sleeping for {sleep_duration} seconds...")
        time.sleep(sleep_duration)
        schedule.run_pending()

# Running the script
if __name__ == "__main__":
    try:
        schedule_and_run_jobs()
    except Exception as e:
        logging.error("Unhandled exception occurred. Stacktrace:")
        logging.error(traceback.format_exc())