# Проект [Сбор и анализ производственных данных] 
## Работали студенты: Аверкина Д.С., Тишининова В.И., Антипов И.А., Глазков О.И.

Ссылка на презентацию: https://disk.yandex.ru/d/zsBmfDxCD9utvA

### Описание файлов:

1. **ids3_dag.py**:
   - Скрипт DAG для Apache Airflow, который обрабатывает данные из таблицы `ids3_table_dates` в базе данных PostgreSQL.
   - Выполняет очистку, преобразование данных (форматирование дат, обработка строковых значений) и сохраняет результат в таблице `ids3_table`.

2. **ids5_dag.py**:
   - Скрипт DAG для Apache Airflow, аналогичный `ids3_dag.py`, но предназначен для работы с таблицами `ids5_table_dates` и `ids5_table_dates_with_error`.
   - Консолидирует данные из двух таблиц, выполняет их обработку (включая обработку ошибок) и сохраняет в таблицу `ids5_table`.

3. **json_parser_ids3.ipynb**:
   - Jupyter Notebook для парсинга JSON-данных - источник `ids3`.

4. **json_praser_ids5.ipynb**:
   - Jupyter Notebook для парсинга JSON-данных - источник `ids5`.

5. **create_dashboard.ipynb**:
   - Jupyter Notebook для тестирования и анализа содержимого - заготовка для основных обработчиков

6. **node-red-compose.yml**:
   - Конфигурация Docker Compose для запуска Node-RED.

7. **sensor_data.zip**:
   - Полный дамп БД (структура и данные).
