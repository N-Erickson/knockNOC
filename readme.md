# knockNOC

knockNOC is a ping-based monitoring solution that does just what it says: pings endpoints and logs their response. It has a modifiable set of alerting metrics and is able to send alerts for non-response to a host of popular platforms.

## Features

- Monitor multiple endpoints (URLs or IP addresses)
- Customizable themes with a cyberpunk aesthetic
- Real-time status updates
- Configurable alerting system
- RESTful API for ping data
- Dockerized for easy deployment

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/N-Erickson/knockNOC.git
cd knockNOC
```

Modify the config.yaml file to add your endpoints and configure alerting (see Configuration section for details).
```bash
nano config.yaml
```
Build the Docker image:

```bash
docker-compose build
```

Start the application:
```bash
docker-compose up
```
Access the dashboard at http://localhost:5000

## Configuration
Edit the config.yaml file to customize your endpoints and alerting settings. The file structure is as follows:
```yaml
endpoints:
  - url: https://example.com
    display_name: Example Site
  - url: 192.168.1.1
    display_name: Local Router

ping_frequency: 60  # in seconds

alerting:
  enabled: true
  consecutive_failures_threshold: 3
  cooldown_duration: 300  # in seconds
  pagerduty:
    enabled: false
    api_key: YOUR_PAGERDUTY_API_KEY
    service_id: YOUR_SERVICE_ID
  opsgenie:
    enabled: false
    api_key: YOUR_OPSGENIE_API_KEY
  slack:
    enabled: false
    webhook_url: YOUR_SLACK_WEBHOOK_URL
  telegram:
    enabled: false
    bot_token: YOUR_TELEGRAM_BOT_TOKEN
    chat_id: YOUR_TELEGRAM_CHAT_ID
  discord:
    enabled: false
    webhook_url: YOUR_DISCORD_WEBHOOK_URL
```

## Alerting Configuration

enabled: Set to true to enable alerting, false to disable.

consecutive_failures_threshold: Number of consecutive failures before an alert is triggered.

cooldown_duration: Time (in seconds) to wait before sending another alert for the same endpoint.

Each alerting service (PagerDuty, OpsGenie, Slack, Telegram, Discord) can be individually enabled or disabled.

Provide the necessary API keys or webhook URLs for the services you enable.

## API
knockNOC provides a RESTful API for accessing ping data:

Endpoint: http://localhost:5000/api/pings
Method: GET
Response: JSON array of endpoint statuses and recent pings

## Development
To run the application in development mode:

Install Python dependencies:

```bash
pip install -r requirements.txt
```
Install Node.js dependencies:

```bash
cd frontend
npm install
```
Run the Flask development server:

```bash 
python3 run.py
```
In another terminal, run the Vue.js development server:
```bash
cd frontend
npm run serve
```
Access the application at http://localhost:5000

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
## License

## Docker Image 
```bash
docker pull ghcr.io/n-erickson/knocknoc:main
docker run -p 5000:5000 ghcr.io/n-erickson/knocknoc:main
```
