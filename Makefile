start:
	docker-compose up -d

build:
	docker-compose up --build -d

stop:
	docker-compose stop

down:
	docker-compose down

test:
	docker-compose exec -it app pytest