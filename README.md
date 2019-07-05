# AppInsights on-premises

[![Travis CI status](https://api.travis-ci.org/c-w/appinsights-on-premises.svg?branch=master)](https://travis-ci.org/c-w/appinsights-on-premises)
[![DockerHub tag](https://images.microbadger.com/badges/version/cwolff/appinsights-on-premises.svg)](https://hub.docker.com/r/cwolff/appinsights-on-premises/tags)

## What's this?

This repository contains a service that's API compatible with [Azure AppInsights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
but that stores the telemetry in a database. This enables developers to use AppInsights client SDKs but
keep all data on-premises.

## Setup

To run the service, execute the following commands:

```bash
# run the database and appinsights server
make build start

# send sample telemetry to the appinsights server
make tests
```

## Usage

To integrate an application that uses the AppInsights client SDK with the service, the only necessary change
is to point the client SDK to the service's telemetry endpoint. For example, when using the Python [AppInsights SDK](https://github.com/Microsoft/ApplicationInsights-Python):

```python
from applicationinsights import TelemetryClient
from applicationinsights.channel import AsynchronousQueue, AsynchronousSender, TelemetryChannel

# define the endpoint of the service and an instrumentation key registered with the service
endpoint = 'http://localhost:8000/'
ikey = '553161ed-0c6b-41a8-973e-77a411391be5'

# point the telemetry client to the custom endpoint
client = TelemetryClient(ikey, TelemetryChannel(queue=AsynchronousQueue(AsynchronousSender(endpoint))))

# now use the telemetry client as normal, e.g.:
client.track_event('my_event', {'some_property': 'a value'})
```
