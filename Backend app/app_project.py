from flask import Flask, request, render_template, jsonify
import os
import pickle
import logging
import pandas as pd
import json
from datetime import datetime

app = Flask(__name__)

HISTORY_FILE = './Backend app/static/price_history.json'

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

@app.route('/save_history', methods=['POST'])
def api_save_history():
    try:
        data = request.get_json()
        history = load_history()
        
        # Добавляем новую запись
        history.insert(0, data)
        
        # Сохраняем в файл
        save_history(history)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_history')
def api_get_history():
    try:
        history = load_history()
        return jsonify({'history': history})
    except Exception as e:
        return jsonify({'history': [], 'error': str(e)})


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
    global percentage_of_tags
    model_path = get_latest_model('./models')
    koefs_path = get_latest_model('./koefs')
    if model_path:
        try:
            with open(model_path, 'rb') as file:
                model = pickle.load(file)
            logger.info(f"Модель загружена: {model_path}")

            with open(koefs_path, 'rb') as file:
                percentage_of_tags = pickle.load(file)
            logger.info(f"Коэффициенты загружены: {koefs_path}")

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

    # Подготовка данных о факторах влияния
    factors = [
        {"name": percentage_of_tags[0]["tag"], "value": "", "impact": f"{percentage_of_tags[0]['percent']}%"},
        {"name": percentage_of_tags[1]["tag"], "value": "", "impact": f"{percentage_of_tags[1]['percent']}%"},
        {"name": percentage_of_tags[2]["tag"], "value": "", "impact": f"{percentage_of_tags[2]['percent']}%"},
        {"name": percentage_of_tags[3]["tag"], "value": "", "impact": f"{percentage_of_tags[3]['percent']}%"},
        {"name": percentage_of_tags[4]["tag"], "value": "", "impact": f"{percentage_of_tags[4]['percent']}%"}
    ]

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
            'factors': factors,
            'success': True
        })

if __name__ == '__main__':
    app.run(debug=True, port=8000)
