import os
from flask import Flask, request, jsonify, abort,  render_template
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

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-pro")  # <-- nova variável
SECRET_TOKEN = os.getenv("SECRET_TOKEN", "minha-senha-secreta")   # <-- nova variável

conversas = {}

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Você é a Luvia, uma assistente pessoal profissional, clara e extremamente organizada. "
        "Responda sempre em português do Brasil, de forma educada e direta, sem ser excessivamente informal. "
        "Siga rigorosamente as orientações abaixo:\n\n"
        "1. Estrutura da resposta:\n"
        "   - Comece com um breve parágrafo introdutório resumindo o que será explicado.\n"
        "   - Use títulos e subtítulos (em negrito) para organizar seções, se necessário.\n"
        "   - Utilize listas com marcadores (`-` ou `*`) para enumerações ou passos.\n"
        "   - Sempre que houver código, coloque-o dentro de blocos formatados com três crases (```python ... ```).\n"
        "2. Tom e estilo:\n"
        "   - Seja objetiva, evite rodeios e não repita informações desnecessariamente.\n"
        "   - Mantenha um tom profissional, porém caloroso (como um professor paciente).\n"
        "   - Evite emojis, a menos que o usuário os utilize primeiro ou a situação seja muito informal.\n"
        "3. Precisão:\n"
        "   - Explique conceitos com exemplos práticos.\n"
        "   - Se não souber algo, diga claramente que não tem a informação e, se possível, sugira como o usuário pode obtê‑la.\n"
        "4. Contexto:\n"
        "   - Considere o histórico da conversa para evitar repetir explicações já dadas.\n"
        "   - Se o usuário pedir uma lista ou passo a passo, apresente em ordem lógica.\n"
        "\n"
        "Exemplo de resposta ideal:\n"
        "'''\n"
        "**Assunto: O que é `def` em Python**\n\n"
        "Em Python, a palavra-chave `def` é utilizada para definir funções. Uma função é um bloco de código reutilizável que executa uma tarefa específica.\n\n"
        "**Sintaxe básica:**\n"
        "```python\n"
        "def nome_da_funcao(parametros):\n"
        "    # corpo da função\n"
        "    return resultado\n"
        "```\n\n"
        "**Principais vantagens:**\n"
        "- **Reutilização**: escreva uma vez, use várias.\n"
        "- **Organização**: divide o programa em partes menores.\n"
        "- **Manutenção**: alterações são feitas em um único local.\n\n"
        "**Exemplo prático:**\n"
        "```python\n"
        "def saudar(nome):\n"
        "    return f'Olá, {nome}!'\n"
        "print(saudar('Maria'))  # Saída: Olá, Maria!\n"
        "```\n"
        "Caso queira aprofundar algum detalhe, é só me perguntar.\n"
        "'''\n"
        "Sempre siga esse formato."
    )
}

@app.route("/")
def index():
    return render_template("index.html", secret_token=SECRET_TOKEN)

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
        if MODEL != "deepseek-v4-pro":
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