PYTHON = pipenv run python

MANAGE = $(PYTHON) src/manage.py

GREEN = \033[0;32m
RED = \033[0;31m
YELLOW = \033[1;33m
NC = \033[0m 

.PHONY: help runserver migrate makemigrations superuser tests celery celery-beat

help:
	@echo "$(YELLOW)Available targets:$(NC)"
	@echo "  $(GREEN)runserver$(NC)      - Start Django development server"
	@echo "  $(GREEN)migrate$(NC)        - Apply database migrations"
	@echo "  $(GREEN)makemigrations$(NC) - Create new migrations"
	@echo "  $(GREEN)superuser$(NC)      - Create superuser"
	@echo "  $(GREEN)tests$(NC)          - Run pytest tests"
	@echo "  $(GREEN)celery$(NC)         - Run celery worker"
	@echo "  $(GREEN)celery-beat$(NC)    - Run celery beat"

runserver:
	@echo "$(GREEN)Starting development server...$(NC)"
	$(MANAGE) runserver

makemigrations:
	@echo "$(GREEN)Creating migrations...$(NC)"
	$(MANAGE) makemigrations

migrate:
	@echo "$(GREEN)Applying migrations...$(NC)"
	$(MANAGE) migrate

superuser:
	@echo "$(GREEN)Creating superuser...$(NC)"
	$(MANAGE) createsuperuser

tests:
	@echo "$(GREEN)Running tests...$(NC)"
	pipenv run pytest src -v

celery:
	@echo "$(GREEN)Starting Celery worker...$(NC)"
	cd src && pipenv run celery -A core worker -l info

celery-beat:
	@echo "$(GREEN)Starting Celery beat...$(NC)"
	cd src && pipenv run celery -A core beat -l info
