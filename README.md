# KnockNOC

KnockNOC is a network monitoring application that pings endpoints (IP addresses or URLs) at regular intervals to check their availability. It tracks the response time and status of each endpoint and provides a web interface to view the monitoring results.

## Features

- Ping IP addresses and URLs to check their availability
- Track response time and status of each endpoint
- Web interface to view monitoring results
- Alerting via PagerDuty, OpsGenie, Slack, Telegram, and Discord
- Configuration through YAML file

## Installation

To install and run KnockNOC locally, follow these steps:

Prereq:
- Install Python
- Install Pip

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/knocknoc.git
   cd knocknoc

2. (optional)Create a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate

3. Install the required dependencies:

    ```bash
    pip install -r requirements.txt

4. Configure the application:

Open the config.yaml file and customize the configuration according to your needs. Add the endpoints you want to monitor and configure alerting options if desired.

5. Run the application

    ```bash
    python app.py

6. The application will start running on http://localhost:5000.






<img width="1491" alt="Screen Shot 2023-06-17 at 11 43 18 PM" src="https://github.com/N-Erickson/knockNOC/assets/16261609/5c098ad7-17e9-459c-b5c8-9502695f4263">
