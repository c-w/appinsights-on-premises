# AppInsights on-premises

[![Travis CI status](https://api.travis-ci.org/CatalystCode/appinsights-on-premises.svg?branch=master)](https://travis-ci.org/CatalystCode/appinsights-on-premises)

## What's this?

This repository contains a server that's API compatible with [Azure Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
but that stores the telemetry in a database. This enables developers to use Application Insights client SDKs but
keep all data on-premises.

## Usage

```bash
# prepare the containers
docker-compose build

# run the database
docker-compose up -d postgres

# initialize the database (can be run only once)
docker-compose run app app.tools.create_db

# run the appinsights server
docker-compose up -d app

# register a client
ikey="$(docker-compose run app app.tools.register_client)"

# send sample telemetry to the appinsights server
docker-compose run app app.tools.generate_telemetry --ikey "${ikey}"
```
