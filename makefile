.EXPORT_ALL_VARIABLES:

APPINSIGHTS_INSTRUMENTATIONKEY ?= 553161ed-0c6b-41a8-973e-77a411391be5
BACKEND ?= postgres

docker_compose := docker-compose -f compose/app.yml -f compose/backends/$(BACKEND).yml

build:
	$(docker_compose) pull --ignore-pull-failures
	$(docker_compose) build

start:
	$(docker_compose) up -d

stop:
	$(docker_compose) down --volumes --remove-orphans

tests:
	$(docker_compose) run app python -m app.tools.generate_telemetry --ikey "$(APPINSIGHTS_INSTRUMENTATIONKEY)"

logs:
	$(docker_compose) logs -f

release:
	@docker login --username "$(DOCKER_USER)" --password "$(DOCKER_PASSWORD)"
	docker push "$(DOCKER_IMAGE)"
