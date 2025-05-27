from flask import Flask, request, render_template, jsonify
import os
import pickle
import logging
import pandas as pd
import json

app = Flask(__name__)

# --- Логирование (по желанию, можно убрать) ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Загрузка последней модели ---
def get_latest_model(directory):
    """Находит последнюю обученную модель""" #
    try:
        files = [f for f in os.listdir(directory) if f.endswith('.pkl')]
        latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(directory, x)))
        return os.path.join(directory, latest_file)
    except Exception as e:
        logger.error(f"Ошибка поиска модели: {e}")
        return None

model = None

def load_model():
    global model
    model_path = get_latest_model('./models')
    if model_path:
        try:
            with open(model_path, 'rb') as file:
                model = pickle.load(file)
            logger.info(f"Модель загружена: {model_path}")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            model = None
    else:
        logger.error("Модель не найдена в ./models")

# --- Загрузка модели при старте ---
load_model()

@app.route('/')
def index():
    return render_template('website.html')

@app.route('/apply', methods=['POST'])
def apply():
    data = request.get_json()
    print("Получены данные из формы:", data)

    product = data.get('product')
    category = data.get('category')
    stock = int(data.get('stock'))
    demand = data.get('demand')
    dayType = data.get('dayType')
    dayTime = data.get('dayTime')

    # Обработка продукта
    with open('./Backend app/static/goods.json', encoding='utf-8') as f:
        goods_data = json.load(f)
        product = goods_data['uniques'].index(str(product))

    # Обработка категории
    with open('./Backend app/static/categories.json', encoding='utf-8') as f:
        categories_data = json.load(f)
        category = categories_data['uniques'].index(str(category))

    # обработка спроса
    if demand == "Низкий":
        demand = 0
    elif demand == "Средний":
        demand = 1
    else:
        demand = 2

    # Обработка дня недели
    if dayType == "Будний":
        dayType = 0
    else:
        dayType = 1

    
    

    input_data = {
            'Товар': [product],
            'Категория': [category],
            'Остаток': [stock],
            'Тип дня': [dayType],
            'Спрос': [demand]
    }

    input_df = pd.DataFrame(input_data)


    print(input_df)

    prediction = int(model.predict(input_df).round(0))

    print(prediction)


    # Пример использования модели (если она нужна)
    # if model is not None:
    #     prediction = model.predict(...)
    #     return jsonify({'result': str(prediction)})
    # else:
    #     return jsonify({'result': 'Модель не загружена'})

    # Пока просто склеиваем все значения в строку
    #result = ' '.join(str(v) for v in data.values())
    return jsonify({
            'result': f"{prediction} ₽",
            'success': True
        })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
