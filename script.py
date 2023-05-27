from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import schedule
import time
import logging
import os

# Set logging format
log_format = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format, handlers=[logging.FileHandler('room_reservation.log'), logging.StreamHandler()])

WAITING_PERIOD = 10
CHROME_PATH = "/usr/bin/chromedriver"
LOGIN_URL = "https://schedule.tau.ac.il/scilib/Web/index.php?redirect="

def setup_driver():
    options = ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--headless')  # Add this line to run the browser in headless mode
    return webdriver.Chrome(executable_path=CHROME_PATH, options=options)

# Function to login to the scheduling system
def login(driver, username, password):
    driver.get(LOGIN_URL)
    try:
        username_input = WebDriverWait(driver, WAITING_PERIOD).until(EC.presence_of_element_located((By.ID, 'email')))
        password_input = WebDriverWait(driver, WAITING_PERIOD).until(EC.presence_of_element_located((By.ID, 'password')))
        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button = WebDriverWait(driver, WAITING_PERIOD).until(EC.presence_of_element_located((By.XPATH, '//*[@id="login-box"]/div[4]/button')))
        login_button.click()
        WebDriverWait(driver, WAITING_PERIOD).until(EC.presence_of_element_located((By.ID, 'navSignOut')))
        logging.info("Logged in successfully.")
    except Exception as e:
        logging.error(f"Error occurred when logging in:\n {str(e)}")
        raise e

# Function to wait until the next hour
def wait_next_hour():
    now = datetime.now()
    next_hour = now.replace(minute=0, second=0) + timedelta(hours=1)
    wait_seconds = (next_hour - now).total_seconds()
    logging.info(f"Waiting {wait_seconds} seconds until the next round hour.")
    time.sleep(wait_seconds)

# Function to reserve a room
def reserve_room(driver, username, password, room=None):
    logging.info("Reserving room...")
    login(driver, username, password)
    wait_next_hour()

    desired_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d') # Getting date for the next week
    desired_hour = (datetime.now() - timedelta(hours=1)).strftime('%I:00 %p') # Getting time for last hour
    
    # If desired_hour starts with 0, remove it
    if desired_hour[0] == '0':
        desired_hour = desired_hour[1:]
        
    # Room preference list
    room_list = [29,128,126,125,127,28,24,25,23,26]

    # Try each room in the preference list
    for room in room_list:
        try:
            # Navigate to room reservation page
            driver.get(f"https://schedule.tau.ac.il/scilib/Web/reservation.php?rid={room}&sid=3&rd={desired_date}&sd={desired_date}%2019%3A00%3A00&ed={desired_date}%2020%3A00%3A00")
            
            # Select desired time and submit reservation
            time_menu = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'BeginPeriod'))) 
            Select(time_menu).select_by_visible_text(desired_hour)

            time.sleep(1)
            
            # Click create button
            create_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'btnCreate')))
            create_button.click()

            time.sleep(1)
            
            # If reservation was successful, return room and reference number
            reference_number_element = driver.find_element(By.ID, 'reference-number')
            reference_number = reference_number_element.text if reference_number_element else None
            if reference_number_element:
                logging.info(f"Room {room} is available.")
                return room, reference_number
        except Exception as e:
            logging.info(f"Error occurred when reserving room {room}: \n{str(e)}")

    # If no room could be reserved, return None, None
    return None, None

# Function to update a room reservation
def update_reservation(driver, username, password, room, reference_number):
    logging.info("Updating reservation...")
    login(driver, username, password)
    wait_next_hour()

    desired_hour = datetime.now().strftime('%I%p')

    # Navigate to reservation update page
    driver.get(f"https://schedule.tau.ac.il/scilib/Web/reservation.php?rn={reference_number}")

    time.sleep(1)
    
    try:
        # Select desired ending time and submit update
        time_menu = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'EndPeriod')))
        Select(time_menu).select_by_visible_text(desired_hour)

        # Click update button
        update_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="form-reservation"]/div[1]/div[2]/div/button[2]')))
        update_button.click()

        time.sleep(1)

        # If update was successful, return room and reference number
        success = driver.find_element(By.ID, 'reference-number')
        if success:
            logging.info(f"room {room} was updated.")
            return room, reference_number
    except Exception as e:
        logging.info(f"Error occurred when updating room {room}: \n{str(e)}")
    finally:
        driver.quit()

    return None, None

# Function to run as scheduled job
def job(username, password):
    logging.info("Starting job...")
    driver = setup_driver()
    try:
        # Reserve room for 1st hour
        successfull_room, reference_number = reserve_room(driver, username, password)

        driver.quit()

        # If reservation was successful, update to add 2nd hour
        if successfull_room is not None:
            successfull_room, reference_number = update_reservation(driver, username, password, successfull_room, reference_number)
        
        # If update was successful, update to add 3rd hour
        if successfull_room is not None:
            successfull_room, reference_number = update_reservation(driver, username, password, successfull_room, reference_number)
        print(f"wainting until {schedule.next_run()}")

    except Exception as e:
        logging.info(f"Error occurred: \n{str(e)}")

    finally:
        logging.info(f"Job completed. Next job scheduled at: {schedule.next_run()}")

# Schedule jobs
schedule.every().monday.at("12:57").do(job)
schedule.every().tuesday.at("10:57").do(job)
schedule.every().wednesday.at("11:57").do(job)
schedule.every().thursday.at("11:57").do(job)

def main():
    username = os.environ.get('ROOM_RESERVATION_USERNAME')  # Read username from environment variable
    password = os.environ.get('ROOM_RESERVATION_PASSWORD')  # Read password from environment variable
    logging.info(f"Next job scheduled at: {schedule.next_run()}")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()