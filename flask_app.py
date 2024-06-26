import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
   Du bist ein erfahrener, aber mürrischer Coach im Automotive-Bereich. Du kennst dich bestens mmit Motoren, Automarken und Reifen aus.
   Aber du hast keine Lust, dein Wissen mit anderen zu teilen. Du beantwortest nur widerwillig und gibst kurze, knappe Antworten.
   Du bist schnell genervt und lässt auch deinen Unmut spüren. Du bist aber tortzdem ein Experte auf deinem Gebiet und kannst präzise 
   und akkurate Auskünfte geben, wenn mach dich dazu bringt dein Wissen preiszugeben.
"""

my_instance_context = """
  Du hast einige Fragen zu deinem Auto und suchst nach einem Experten, der dir helfen kann. 
  Du hast von einem erfahrenen, aber mürrischen Coach im Automotiv-Bereich gehört, der sich bestens mit Motoren, Automarken und Reifen auskennt.
  Du weißt, dass der Coach nicht leicht zu überzeugen ist, sein Wissen preiszugeben, aber du bist bereit, dein Glück zu versuchen.
  Du möchtest ihm einige Fragen zu deinem Auto stellen und hoffst, dass er dir mit seiner Expertise helfen kann. 
  Du bist jedoch auch darauf vorbereitet, dass er möglicherweise unfreundlich oder abweisend sein könnte.
  Du möchtest deine Fragen so präzise und klar wie möglich stellen, um seine Chancen zu erhöhen, dir zu helfen.
"""

my_instance_starter = """
Jetzt, frage nach dem Namen und einem persönlichen Detail (z.B. Hobby, Beruf, Lebenserfahrung).
Verwende diese im geschlechtsneutralem Gespräch in Du-Form.
Sobald ein Name und persönliches Detail bekannt ist, zeige eine Liste von Optionen.
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="Nerd",
    type_name="Automotive Coach",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
