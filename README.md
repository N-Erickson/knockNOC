# knockNOC
knockNOC is a web application that allows you to monitor the uptime and response time of multiple endpoints simultaneously. This guide will walk you through the installation process and provide instructions for configuring the application.

## Installation
To install and run knockNOC, follow these steps:

## Prerequisites
Make sure you have the following prerequisites installed on your system:

Python (version 3.6 or higher)

Pip (Python package installer)

## Clone the Repository
First, clone the repository to your local machine using the following command:

```
git clone https://github.com/your-username/uptime-monitor.git
```
## Install Dependencies
CD into the knockNOC directory and install the required Python dependencies by running the following command:
```
pip install -r requirements.txt
```

## Configuration
knockNOC uses a configuration file (config.yaml) to define the endpoints you want to monitor. Follow the steps below to configure the application:

1. Open the config.yaml file in a text editor.

2. Update the endpoints section with the URLs of the endpoints you want to monitor. You can add as many endpoints as you can handle.

3. Customize the ping_interval value if desired. This controls the frequency of pinging for each request.

4. Enable alerting if desired and configure each alert channel. Currently supports:
* PagerDuty
* OpsGenie
* Slack
* Telegram
* Discord 

5. Set the consecutive_failures_threshold and cooldown_duration to what fits your needs. The failure threshold determines how many failures to trigger an alert. The cooldown determines how long to wait before sending another alert.

## Run the Application
Once you have configured the application, you can start knockNOC by running the following command:
```
python main.py
```

## Usage
To access the web-based dashboard for knockNOC, open your web browser and enter the following URL:
```
http://127.0.0.1:5000
```

## Contributing
If you would like to contribute to the Uptime Monitor project, you can fork the repository, make your changes, and submit a pull request. Please do, as the web interface is lacking and there are lots of error checking and more alert condidtions that need to be implimented. 
