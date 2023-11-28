from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit
from connect.chatgpt_connect import ChatGPTConnect

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

# Salas
rooms = {}

# ID da sala
roomID = "versionamento321"

# Cria a sala
rooms[roomID] = {
    "members": 0,
    "messages": [],
    "users": [],
    "done_todos": {},
    "current_slide": 1,
}

# Tarefas
todos = [
    {"id": "instalar-git", "name": "Instalar Git"},
    {"id": "clonar-repo", "name": "Clonar repositório"},
]

# Cria os parâmetros das tarefas
for todo in todos:
    # Nomes dos usuários que terminaram as tarefas
    todo["users_name_finished"] = []
    # Quantidade de usuários que terminaram as tarefas
    todo["users_finished"] = 0
    # Quantidade de usuários que NÃO terminaram as tarefas
    todo["users_not_finished"] = 0
    # Nomes dos usuários que NÃO terminaram as tarefas
    todo["users_name_not_finished"] = []


#######################################
# Rotas
#######################################

# Página inicial
@app.route("/", methods=["POST", "GET"])
def home():
    global roomID

    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)

        # Verifica se o nome foi digitado
        if not name:
            return render_template(
                "home.html", error="Por favor, digite seu nome", code=code, name=name
            )

        # Verifica se o código foi digitado
        if join != False and not code:
            return render_template(
                "home.html",
                error="Por favor, digite o código da sala",
                code=code,
                name=name,
            )

        # Verifica se o código da sala existe
        if code not in rooms:
            return render_template(
                "home.html", error="Código da sala incorreto", code=code, name=name
            )

        users = rooms[code]["users"]
        done_todos = rooms[code]["done_todos"]

        # Verifica se o nome de usuário existe
        if name.lower() in users:
            return render_template(
                "home.html",
                error="Esse nome de usuário já existe",
                code=code,
                name=name,
            )

        # Adiciona o usuário à sala e cria a lista de tarefas concluídas dele
        users.append(name.lower())
        done_todos[name] = []

        # Adiciona o usuário a cada tarefa como não finalizado
        for todo in todos:
            todo["users_name_not_finished"].append(name.lower())
            todo["users_not_finished"] += 1

        # Define a sala e o nome do usuário na sessão
        session["room"] = roomID
        session["name"] = name

        # Redireciona para a sala
        return redirect(url_for("room"))

    return render_template("home.html")


# Sala
@app.route("/room")
def room():
    global todos

    room = session.get("room")
    name = session.get("name")

    # Redireciona para a página inicial caso o usuário não exista
    if (
        room is None
        or name is None
        or room not in rooms
        or name not in rooms[room]["done_todos"]
    ):
        return redirect(url_for("home"))

    messages = rooms[room]["messages"]
    done_todos = rooms[room]["done_todos"][name]

    # Atualiza o dashboard
    socketio.emit("user-doing-todo", todos, namespace="/dashboard")

    return render_template(
        "room.html",
        code=room,
        messages=messages,
        todos=todos,
        done_todos=done_todos,
    )


# Marca uma tarefa como concluída
@app.route("/check/<todoID>")
def check(todoID):
    global todos, rooms

    name = session.get("name")
    room = session.get("room")
    done_todos = rooms[room]["done_todos"][name]

    # Adiciona a tarefa como concluída na lista do usuário
    done_todos.append(todoID)

    # Marca a tarefa como concluída pelo usuário na lista da sala
    for todo in todos:
        if todo["id"] == todoID:
            todo["users_name_finished"].append(name)
            todo["users_name_not_finished"].remove(name.lower())
            todo["users_finished"] += 1
            todo["users_not_finished"] -= 1
            break

    # Atualiza o dashboard
    socketio.emit("user-doing-todo", todos, namespace="/dashboard")

    return "OK"


# Dashboard
@app.route("/dashboard/<room_id>")
def dashboard(room_id):
    global todos

    # Retorna o dashboard referente ao código da sala, caso não exista, retorna um erro
    if room_id in rooms:
        return render_template("dashboard.html", todos=todos)
    else:
        return render_template("error.html")


#######################################
# SocketIO (usuário)
#######################################

# Quando o usuário conectar
@socketio.on("connect")
def connect():
    room = session.get("room")
    name = session.get("name")

    # Se o nome ou o código da sala não foram especificados, encerra a conexão
    if not room or not name:
        return

    # Entra na sala
    join_room(room)

    # Envia uma mensagem para todos informando que o usuário entrou na sala
    send({"name": name, "message": "🚪 Entrou na sala"}, to=room)

    # Envia a informação do slide atual
    socketio.emit("set-slide", rooms[room]["current_slide"])

    # Incrementa o número de membros da sala
    rooms[room]["members"] += 1


# Quando o usuário desconectar
@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")

    # Remove o usuário da sala
    leave_room(room)

    # Diminui o número de membros da sala
    if room in rooms:
        rooms[room]["members"] -= 1

    # Envia uma mensagem para todos informando que o usuário saiu da sala
    send({"name": name, "message": "🚪 Saiu da sala"}, to=room)


# Quando o usuário enviar uma mensagem
@socketio.on("message")
def message(data):
    name = session.get("name")
    room = session.get("room")
    messages = rooms[room]["messages"]

    # Se o código da sala não foi especificado, encerra a conexão
    if room not in rooms:
        return

    # Envia a mensagem para todos
    message = data["data"]
    content = {"name": name, "message": message}
    send(content, to=room)
    messages.append(content)

    # Verifica se a mensagem vêm do administrador e quer que a IA responda
    ia_key = "HELP AI:"
    if name == "administrator" and message.startswith(ia_key):
        connect_ia = ChatGPTConnect()
        response = connect_ia.response_message(message[len(ia_key)::])

        # Envia a resposta para todos
        content = {"name": "Eisten IA", "message": response}
        send(content, to=room)
        messages.append(content)


#######################################
# SocketIO (administrador)
#######################################

# Quando o administrador conectar
@socketio.on("connect", namespace="/dashboard")
def connect():
    global todos, roomID

    # Envia as informações das tarefas e do slide atual para o dashboard
    socketio.emit("user-doing-todo", todos, namespace="/dashboard")
    socketio.emit("set-slide", rooms[roomID]["current_slide"], namespace="/dashboard")


# Muda o slide
@socketio.on("set-slide", "/dashboard")
def set_slide(slide_no):
    global roomID

    rooms[roomID]["current_slide"] = slide_no
    socketio.emit("set-slide", slide_no)


if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True, host='0.0.0.0')
