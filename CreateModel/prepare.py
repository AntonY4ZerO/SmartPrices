# Импорт для prepare_data
from sklearn.model_selection import train_test_split
import datetime
import os
import pandas as pd
import logging
from category_encoders import TargetEncoder
import json
import numpy as np

# Создание логера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/project.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def Prepare_data(output_dir='data/prepared', input_dir='data/raw', filename='Shop_prices.csv'):
    df = pd.read_csv(input_dir+"/"+filename)
    
    # Обработка "Тип дня"
    df['Тип дня'], uniques = pd.factorize(df['Тип дня'])

    # Обработка "Спрос"
    df['Спрос'] = df['Спрос'].apply(
    lambda x: 0 if x < 10 else (1 if x < 45 else 2)
)
    # Обработка "Категория"
    #df = pd.get_dummies(df, columns=['Категория'], prefix='кат')
    labels_cat, uniques_cat = pd.factorize(df['Категория'])

    result_cat = {
        "labels": np.unique(labels_cat).tolist(),  # Преобразуем numpy-массив в список
        "uniques": uniques_cat.tolist() # То же для уникальных значений
    }

    #print(df['Товар'].unique())

    # Обработка "Товар"
    labels, uniques = pd.factorize(df['Товар'])

    result = {
        "labels": np.unique(labels).tolist(),  # Преобразуем numpy-массив в список
        "uniques": uniques.tolist() # То же для уникальных значений
    }

    with open('./Backend app/static/goods.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4) 

    with open('./Backend app/static/categories.json', 'w', encoding='utf-8') as f:
        json.dump(result_cat, f, ensure_ascii=False, indent=4) 

    df['Товар'] = labels
    df['Категория'] = labels_cat

    print(df)

    return df




Prepare_data()