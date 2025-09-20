
# Micro E-commerce Platform

![Архитектура](docs/architecture.png)

## Описание

Микросервисная e-commerce платформа на FastAPI, PostgreSQL, Docker, gRPC, Redis, Prometheus, Grafana и GraphQL Gateway.

### Основные возможности

- Регистрация и аутентификация пользователей (JWT, роли user/admin)
- CRUD для пользователей и товаров
- Оформление и оплата заказов (асинхронно)
- Кэширование товаров (Redis)
- gRPC между Orders и Products
- GraphQL API Gateway для клиентов
- Rate limiting (slowapi)
- Мониторинг (Prometheus, Grafana)
- Документация OpenAPI/Swagger для каждого сервиса

## Архитектура

- **Users Service** — пользователи, аутентификация, роли (FastAPI + PostgreSQL)
- **Products Service** — товары, кэширование, gRPC сервер (FastAPI + PostgreSQL + Redis)
- **Orders Service** — оформление заказов, gRPC клиент (FastAPI + PostgreSQL)
- **Payments Service** — эмуляция оплаты, интеграция с Orders (FastAPI + PostgreSQL)
- **Gateway Service** — GraphQL API для клиентов (Ariadne + FastAPI)
- **PostgreSQL** — отдельная БД для каждого сервиса
- **Redis** — кэш продуктов
- **Prometheus & Grafana** — мониторинг и визуализация

## Быстрый старт

```bash
git clone https://github.com/your-org/micro-ecommerce-platform.git
cd micro-ecommerce-platform
docker-compose up --build
```

- Swagger UI:  
	- http://localhost:8001/docs (Users)  
	- http://localhost:8002/docs (Products)  
	- http://localhost:8003/docs (Orders)  
	- http://localhost:8004/docs (Payments)
- GraphQL Playground: http://localhost:8080/graphql
- Grafana: http://localhost:3000 (логин/пароль: admin/admin)
- Prometheus: http://localhost:9090

## Автоматическое заполнение тестовыми данными

Для быстрой проверки работы платформы используйте:

```bash
python3 fill_test_data.py
```

Скрипт создаёт пользователя, товар, заказ и платёж через API всех сервисов.

## Примеры GraphQL-запросов

```graphql
query {
	products(limit: 5) {
		id
		name
		price
	}
	product(id: 1) {
		name
		description
		price
		stock
	}
}
```

## Тестирование

Для каждого сервиса доступны unit-тесты:

```bash
docker-compose exec users_service pytest
docker-compose exec products_service pytest
docker-compose exec orders_service pytest
docker-compose exec payments_service pytest
```

## Мониторинг

- Метрики Prometheus доступны по `/metrics` у каждого сервиса
- Grafana дашборды для анализа нагрузки и ошибок

## CI/CD

- GitHub Actions: линтеры, тесты, сборка Docker-образов

---

**Файл архитектуры:**  
Схема архитектуры находится в `docs/architecture.png`.  
PlantUML-исходник — `architecture.puml`.

---