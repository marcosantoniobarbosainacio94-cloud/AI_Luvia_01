import os
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "minha-senha-secreta")   # <-- nova variável

conversas = {}

SYSTEM_PROMPT = {
    "role": "system",
    "content": "Você é a Luvia, uma assistente pessoal simpática, proativa e muito organizada. Responda sempre em português do Brasil."
}

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # Proteção: exige o token na requisição
    token = request.headers.get("X-Auth-Token")
    if token != SECRET_TOKEN:
        abort(403, description="Acesso negado. Token inválido.")

    data = request.get_json()
    user_msg = data.get("message", "")
    session_id = data.get("session_id", "default")
    
    if session_id not in conversas:
        conversas[session_id] = [SYSTEM_PROMPT]
    
    conversas[session_id].append({"role": "user", "content": user_msg})
    
    try:
        params = {
            "model": MODEL,
            "messages": conversas[session_id],
            "max_tokens": 4000
        }
        if MODEL != "deepseek-reasoner":
            params["temperature"] = 0.7
        
        response = client.chat.completions.create(**params)
        assistant_msg = response.choices[0].message.content
    except Exception as e:
        print("ERRO NA API:", str(e))
        return jsonify({"error": str(e)}), 500
    
    conversas[session_id].append({"role": "assistant", "content": assistant_msg})
    return jsonify({"response": assistant_msg})

@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)