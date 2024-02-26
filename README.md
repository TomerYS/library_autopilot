# University Room Reservation Automation

This Python script automates the process of reserving rooms through a university's scheduling system using Selenium WebDriver. It is designed to log into the system, select available rooms from a predefined list, and schedule reservations on a weekly basis. The script utilizes headless Chrome for web scraping and interaction, making it suitable for running on servers or any headless environment.

## Features

- **Automated Login**: Logs into the scheduling system using credentials stored in environment variables.
- **Room Selection and Reservation**: Automatically selects rooms from a predefined list and reserves them.
- **Scheduling**: Utilizes the `schedule` library to run room reservation jobs at specified times.
- **Logging**: Logs activities and errors for monitoring and debugging purposes.

## Requirements

- Python 3.x
- Selenium WebDriver
- Chrome WebDriver installed and accessible in your system's PATH or specified directly in the script.
- Schedule library for task scheduling.

## Setup

1. **Install Dependencies**: Install the required Python libraries using pip:

   ```sh
   pip install selenium schedule


2. **Chrome WebDriver**: Ensure you have Chrome WebDriver installed and it's placed in your system's PATH or specify its path in the `CHROME_PATH` variable in the script.

3. **Environment Variables**: 
      Set the following environment variables for your system:
- `ROOM_RESERVATION_USERNAME`: Your scheduling system username.
- `ROOM_RESERVATION_PASSWORD`: Your scheduling system password.

## Usage

1. Update the `ROOM_LIST` in the script with the IDs of the rooms you wish to reserve.
2. Optionally, adjust the scheduled time for the reservation task in the `schedule_and_run_jobs` function.
3. Execute the script:

```bash
python script.py
```

The script will automatically log into the scheduling system, attempt to reserve rooms based on the predefined list, and log the outcome. It will continue to run, executing the reservation task weekly at the specified time. This automation helps in efficiently managing room reservations without manual intervention, ensuring you always have a room booked for your needs.

## Logging

The script logs its operations to `room_reservation.log`, including login attempts, room reservation attempts, and scheduling details. This log file is invaluable for troubleshooting or monitoring the script's activity, providing a clear record of actions taken and any errors encountered.

## Customization

You can customize the script by modifying the `ROOM_LIST`, scheduling times, or adding additional logic for room selection based on availability or other criteria. This flexibility allows the script to be adapted to various scheduling systems or preferences, making it a versatile tool for automated room reservations.

- To change the list of rooms the script attempts to reserve, edit the `ROOM_LIST` variable with the desired room IDs.
- To adjust when the reservation tasks are scheduled, modify the scheduling parameters in the `schedule_and_run_jobs` function. For example, you can change `.every().wednesday.at("15:58")` to another day or time that suits your schedule.

## Disclaimer

This script is provided "as is" for educational and automation purposes. Users should ensure they have the right to automate interactions with their university's scheduling system before use. The developers of this script assume no responsibility for any misuse or for any consequences resulting from the use of this tool. It's important to use automation tools responsibly and in accordance with the terms of service of the systems they interact with.
