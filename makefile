.EXPORT_ALL_VARIABLES:

BACKEND ?= postgres
IKEY1 ?= 553161ed-0c6b-41a8-973e-77a411391be5
IKEY2 ?= c3dd7bdf-b6eb-4b72-868b-64d5ccb3b4f7
APPINSIGHTS_INSTRUMENTATIONKEY := $(IKEY1),$(IKEY2)

docker_compose := docker-compose -f compose/app.yml -f compose/backends/$(BACKEND).yml

build:
	$(docker_compose) pull --ignore-pull-failures
	$(docker_compose) build

start:
	$(docker_compose) up -d

stop:
	$(docker_compose) down --volumes --remove-orphans

tests:
	$(docker_compose) run app python -m app.tools.generate_telemetry --ikey "$(IKEY1)"
	$(docker_compose) run app python -m app.tools.generate_telemetry --ikey "$(IKEY2)"

logs:
	$(docker_compose) logs -f

release:
	@docker login --username "$(DOCKER_USER)" --password "$(DOCKER_PASSWORD)"
	docker push "$(DOCKER_IMAGE)"
