import pandas as pd
from sqlalchemy import create_engine
from airflow.models.dag import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.hooks.base import BaseHook
import pendulum
import logging

# Создание подключения к БД через Airflow Hook
def get_postgres_engine():
    connection = BaseHook.get_connection('postgres_default')
    engine = create_engine(f'postgresql://{connection.login}:{connection.password}@{connection.host}:{connection.port}/{connection.schema}')
    return engine

def ids3_table_dates(**kwargs):
    # Подключение к БД
    engine = get_postgres_engine()

    query = """
        SELECT
            *
        FROM
            public.ids3_table_dates;
    """
    df = pd.read_sql(query, engine)
    
    # Обработка данных
    data = df.copy()
    data = data.loc[:, ~(data.apply(lambda col: all(val == "0 мм" for val in col), axis=0))]
    data['Дата_Время'] = pd.to_datetime(data['Дата'] + ' ' + data['Время'])
    data.drop(['Дата', 'Время'], axis=1, inplace=True)
    
    for col in data.columns:
        if data[col].dtype == 'object' and col != 'Дата_Время' and data[col].str.contains('мм').any():
            data[col] = data[col].str.replace(' мм', '').str.replace(',', '.').astype('float')
    
    data['Канал 1 - Процент выполнения програ'] = data['Канал 1 - Процент выполнения програ'].str.replace('%', '').astype('float') / 100
    
    time_columns = [
        'Моточасы - Время работы ядра (всего',
        'Моточасы - Время работы ядра (текущ',
        'Канал 1 - Время работы канала (всего',
        'Канал 1 - Время работы канала (текущ',
        'Канал 1 - Время работы программы'
    ]
    
    for col in time_columns:
        if col in data.columns:
            try:
                data[col] = pd.to_timedelta(data[col], errors='coerce')
                data[col] = data[col].dt.total_seconds()
            except Exception as e:
                logging.error(f"Error processing column {col}: {e}")
    
    column_renames = {
        'Моточасы - Время работы ядра (всего': 'core_time_total',
        'Моточасы - Время работы ядра (текущ': 'core_time_current',
        'Моточасы - Количество перезапуско': 'core_restarts',
        'Моточасы - Количество каналов': 'core_channels',
        'Канал 1 - Время работы канала (всего': 'channel1_time_total',
        'Канал 1 - Время работы канала (текущ': 'channel1_time_current',
        'Канал 1 - Статус канала': 'channel1_status',
        'Канал 1 - Режим канала': 'channel1_mode',
        'Канал 1 - Время работы программы': 'channel1_program_time',
        'Канал 1 - Процент выполнения програ': 'channel1_progress',
        'Канал 1 - Программа': 'channel1_program',
        'Оси Канала 1 - Перемещение по оси X': 'axis1_move_x',
        'Оси Канала 1 - Перемещение по оси Y': 'axis1_move_y',
        'Оси Канала 1 - Перемещение по оси Z': 'axis1_move_z',
        'Оси Канала 1 - Перемещение по оси B': 'axis1_move_b',
        'Оси Канала 1 - Перемещение по оси C': 'axis1_move_c',
        'Оси Канала 1 - Перемещение по оси S': 'axis1_move_s',
        'Оси Канала 1 - Перемещение по оси S2': 'axis1_move_s2',
        'Дата_Время': 'datetime'
    }
    
    data.rename(columns=column_renames, inplace=True)
    
    column_to_integer = ['core_channels', 'core_restarts']
    for col in column_to_integer:
        if col in data.columns:
            data[col] = data[col].astype('int')
    
    # Сохранение данных обратно в БД
    data.to_sql('ids3_table', engine, if_exists='replace', index=False)

# Определение DAG
with DAG(
    dag_id="ids3_table_dates",
    start_date=pendulum.datetime(2024, 10, 1, tz="Europe/Moscow"),
    schedule_interval='0 * * * *',
    catchup=False,
    tags=["ids_table"],
) as dag:
    start = EmptyOperator(task_id="start")

    process_data = PythonOperator(
        task_id="process_ids3_table_dates",
        python_callable=ids3_table_dates,
        provide_context=True,
    )

    end = EmptyOperator(task_id="end")

    # Задаем порядок выполнения задач
    start >> process_data >> end
