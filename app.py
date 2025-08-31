from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import csv
import requests

app = Flask(__name__)
CORS(app)

# =================== Gluten CSV Load ===================
gluten_db = {}

def load_csv():
    global gluten_db
    try:
        with open("product.csv", newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                barcode = row['Barcode'].strip()
                result = "✅ Gluten-Free" if row['Gluten-Free'].strip().lower() == "true" else "❌ Contains Gluten"
                gluten_db[barcode] = f"{result} - {row['Product Name']}"
        print("✅ Product CSV loaded successfully!")
    except Exception as e:
        print("❌ Error loading product CSV:", e)

load_csv()

# =================== Chatbot CSV Load ===================
chat_responses = {}

def load_chat_csv():
    try:
        with open("chat_data.csv", newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                question = row["question"].strip().lower()
                answer = row["answer"].strip()
                chat_responses[question] = answer
        print("✅ Chat data loaded!")
    except Exception as e:
        print("❌ Error loading chat CSV:", e)

load_chat_csv()

# =================== Routes ===================








@app.route('/')
def home():
    return render_template('index.html')

@app.route('/diet')
def diet():
    return render_template('diet.html')

@app.route('/tests')
def test():
    return render_template('test.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/celiac')
def show_celiac():
    return render_template('celiac.html')

@app.route('/scan')
def scan():
    return render_template('scanner.html')

@app.route('/chat')
def chat_ui():
    return render_template('chat.html')

@app.route('/chat/message', methods=['POST'])
def chat_message():
    data = request.get_json()
    user_message = data.get('message', '').lower()

    for key in chat_responses:
        if key in user_message:
            return jsonify({'reply': chat_responses[key]})
    
    return jsonify({'reply': "⚠️ Sorry, I don’t understand. Please ask about symptoms, diet, gluten, etc."})

@app.route('/gluten_info')
def gluten_info():
    return render_template('gluten_info.html')


@app.route('/nearby_stores')
def nearby_stores():
    return render_template('nearby_stores.html')

@app.route('/recipes')
def recipes():
    return render_template('recipes.html')

@app.route('/myths')
def myths():
    return render_template('myths.html')

@app.route('/symptom_checker')
def symptoms_page():
    return render_template('symptom_checker.html')



@app.route('/weekly_diet')
def weekly_diet():
    return render_template('weekly_diet.html')

@app.route("/diet-form")
def diet_form():
    return render_template("diet-form.html")

@app.route('/check_barcode', methods=['POST'])
def check_barcode():
    data = request.get_json()
    barcode = data.get('barcode')
    result = gluten_db.get(barcode, "❓ Gluten info not found for this product.")
    return jsonify({"result": result})



@app.route('/analyze_symptoms', methods=['POST'])
def analyze_symptoms():
    data = request.get_json()

    illness = data.get('illness', '').lower()
    symptoms = data.get('symptoms', '').lower()
    duration = data.get('duration', '').lower()
    diet = data.get('diet', '').lower()
    period = data.get('period', '')

    reply = ""

    if 'bloating' in symptoms or 'gas' in symptoms:
        reply += "💨 You may be experiencing digestive discomfort. Avoid gluten and dairy temporarily.\n"

    if 'diarrhea' in symptoms or 'loose motion' in symptoms:
        reply += "🚽 Diarrhea can be a symptom of gluten intolerance. Consider a gluten-free diet.\n"

    if 'fatigue' in symptoms:
        reply += "😴 Fatigue is common in Celiac patients due to poor absorption. Get your iron and B12 levels checked.\n"

    if 'skin rash' in symptoms or 'itching' in symptoms:
        reply += "🤕 This could be dermatitis herpetiformis – a skin condition linked with gluten.\n"

    if not reply:
        reply = "📋 Based on your symptoms, it's recommended to consult a gastroenterologist for deeper evaluation."

    return jsonify({'reply': reply})


@app.route("/generate-diet", methods=["POST"])
def generate_diet():
    user_data = request.form.to_dict()

    name = user_data.get("name")
    diet_type = user_data.get("diet_type")

    if diet_type == "Vegetarian":
        breakfast = ["Poha", "Oats", "Upma", "Idli", "Fruits", "Smoothie", "Besan Chilla"]
        lunch = ["Dal Rice", "Paratha", "Khichdi", "Pulao", "Paneer Bowl", "Veg Thali", "Stuffed Capsicum"]
        dinner = ["Moong Dosa", "Kadhi", "Veg Soup", "Roti Sabzi", "Quinoa", "Paneer Tikka", "Mushroom Curry"]
    elif diet_type == "Non-Vegetarian":
        breakfast = ["Eggs", "Oats Omelette", "Smoothie", "Rice Upma", "Chicken Sandwich", "Boiled Eggs", "Egg Bhurji"]
        lunch = ["Chicken Curry", "Fish Rice", "Egg Fried Rice", "Dal Chicken", "Mutton Rice", "Keema Wrap", "Grilled Breast"]
        dinner = ["Grilled Chicken", "Fish Tikka", "Egg Curry", "Soup", "Veg + Chicken", "Paneer Sabzi", "Roti + Curry"]
    else:
        breakfast = ["Tofu Scramble", "Oats with Almond Milk", "Chia Pudding", "Fruit Bowl", "Sweet Potato", "Rice Idli", "Smoothie"]
        lunch = ["Soy Dal Rice", "Vegan Bowl", "Veg Khichdi", "Tofu Curry", "Millet Roti", "Stew", "Salad"]
        dinner = ["Vegan Wrap", "Pumpkin Soup", "Tofu Bowl", "Chickpea Curry", "Rice Soup", "Stuffed Veggies", "Veg Stew"]

    weekly_plan = []
    for i in range(7):
        weekly_plan.append({
            "day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i],
            "breakfast": breakfast[i],
            "lunch": lunch[i],
            "dinner": dinner[i],
            "snack": "Roasted Nuts / Juice"
        })

    return render_template("weekly_diet.html", weekly_plan=weekly_plan, name=name)

@app.route('/recipe/pancakes')
def pancakes_recipe():
    return render_template('recipes/pancakes.html')

@app.route('/recipe/zucchini-pasta')
def zucchini_pasta():
    return render_template('recipes/zucchini_pasta.html')

@app.route('/recipe/quinoa-soup')
def quinoa_soup():
    return render_template('recipes/quinoa_soup.html')

@app.route('/recipe/chickpea-wrap')
def chickpea_wrap():
    return render_template('recipes/chickpea-wrap.html')

@app.route('/recipe/quinoa-bowl')
def quinoa_bowl():
    return render_template('recipes/quinoa-bowl.html')

@app.route('/recipe/gluten-free-pizza')
def gluten_free_pizza():
    return render_template('recipes/gluten-free-pizza.html')




if __name__ == '__main__':
    app.run(debug=True)

