# AppInsights on-premises

[![Travis CI status](https://api.travis-ci.org/CatalystCode/appinsights-on-premises.svg?branch=master)](https://travis-ci.org/CatalystCode/appinsights-on-premises)

## What's this?

This repository contains a server that's API compatible with [Azure Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
but that stores the telemetry in a database. This enables developers to use Application Insights client SDKs but
keep all data on-premises.

## Usage

```bash
# run the database and appinsights server
docker-compose up --build -d

# initialize the database and register a client
docker-compose exec app python -m app.tools.create_db
ikey="$(docker-compose exec app python -m app.tools.register_client)"

# send sample telemetry to the appinsights server
docker-compose exec app python -m app.tools.generate_telemetry --ikey "${ikey}"
```
