define include_dot_env_file
    $(eval include ${PWD}/.env)
endef

env_setup:
	cp .env.example .env
up:
	${call include_dot_env_file} @docker compose -f ${PWD}/docker-compose.yaml -p ${BILLML_DOCKER_COMPOSE_NAME} up -d
down:
	${call include_dot_env_file} @docker compose -f ${PWD}/docker-compose.yaml -p ${BILLML_DOCKER_COMPOSE_NAME} down
up_dev:
	${call include_dot_env_file} @docker compose -f ${PWD}/docker-compose.yaml -f ${PWD}/docker-compose.dev.yaml -p ${BILLML_DOCKER_COMPOSE_NAME} up -d
down_dev:
	${call include_dot_env_file} @docker compose -f ${PWD}/docker-compose.yaml -f ${PWD}/docker-compose.dev.yaml -p ${BILLML_DOCKER_COMPOSE_NAME} down
