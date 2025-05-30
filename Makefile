.PHONY: download-data unzip-data prepare-data build up local-run-with-data local-run-download-data docker-run-with-data docker-run-with-hub-image docker-run-download-data docker-run-download-data-with-hub-image down clean

# Загрузка датасета с Kaggle
download-data:
	@echo "Загрузка датасета..."
	@mkdir -p data/
	@curl -L -o data/global-daily-climate-data.zip https://www.kaggle.com/api/v1/datasets/download/guillemservera/global-daily-climate-data
	@echo "Датасет загружен в data/global-daily-climate-data.zip"

# Распаковка датасета
unzip-data:
	@echo "Распаковка датасета..."
	@if [ ! -f data/global-daily-climate-data.zip ]; then echo "Ошибка: data/global-daily-climate-data.zip не найден"; exit 1; fi
	@unzip -o data/global-daily-climate-data.zip -d data/
	@rm data/global-daily-climate-data.zip
	@echo "Датасет распакован в data/"

# Подготовка данных (создание SQLite базы)
prepare-data:
	@echo "Подготовка данных..."
	@if [ -f data/db.sqlite ]; then echo "База данных data/db.sqlite уже существует, пропускаем создание"; else python src/data_loaders.py; fi
	@echo "Данные подготовлены, база данных в data/db.sqlite"

# Сборка Docker-образа
build:
	@echo "Сборка Docker-образа..."
	@docker compose build
	@echo "Образ собран"

# Запуск Docker-контейнера
up:
	@echo "Запуск приложения в Docker..."
	@docker compose up -d
	@echo "Приложение запущено на http://localhost:8501"

# Локальный запуск с готовыми данными
local-run-with-data:
	@echo "Установка зависимостей..."
	@pip install -r requirements.txt
	@echo "Запуск приложения локально..."
	@streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0
	@echo "Приложение запущено на http://localhost:8501"

# Локальный запуск с загрузкой данных
local-run-download-data: download-data unzip-data prepare-data local-run-with-data

# Docker-запуск с готовыми данными и локальной сборкой
docker-run-with-data: build up

# Docker-запуск с готовыми данными и образом из Docker Hub
docker-run-with-hub-image:
	@echo "Скачивание образа из Docker Hub..."
	@docker pull nikkizav/sber_test-task-app:latest
	@echo "Запуск приложения с образом из Docker Hub..."
	@docker run -d -p 8501:8501 -v $(pwd)/data:/app/data nikkizav/sber_test-task-app:latest
	@echo "Приложение запущено на http://localhost:8501"

# Docker-запуск с загрузкой данных и локальной сборкой
docker-run-download-data: download-data unzip-data prepare-data build up

# Docker-запуск с загрузкой данных и образом из Docker Hub
docker-run-download-data-with-hub-image: download-data unzip-data prepare-data
	@echo "Скачивание образа из Docker Hub..."
	@docker pull nikkizav/sber_test-task-app:latest
	@echo "Запуск приложения с образом из Docker Hub..."
	@docker run -d -p 8501:8501 -v $(pwd)/data:/app/data nikkizav/sber_test-task-app:latest
	@echo "Приложение запущено на http://localhost:8501"

# Остановка приложения
down:
	@echo "Остановка приложения..."
	@docker compose down
	@echo "Приложение остановлено"

# Полная очистка
clean:
	@echo "Очистка..."
	@docker compose down -v
	@echo "Очистка завершена"
