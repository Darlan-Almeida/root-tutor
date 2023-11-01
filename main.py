from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit


app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)


roomID = 'versionamento321'
rooms = {}
rooms[roomID] = { "members": 0, "messages":[], "users":[], "doneTodos": {} }

todos = [
    { "id": "instalar-git", "name": "Instalar Git" , "users": [] , "users_finished" : 0 , "users_not_finished" : 0, "users_name_not_finished": []},
    { "id": "clonar-repo", "name": "Clonar repositório", "users": [] , "users_finished" : 0 , "users_not_finished" : 0 , "users_name_not_finished": []}
]


@app.route("/", methods=["POST", "GET"])
def home():
    global roomID

    users = rooms[roomID]["users"]
    doneTodos = rooms[roomID]["doneTodos"]

    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)

        if not name:
            return render_template("home.html", error="Por favor, digite seu nome", code=code, name=name)
        if join != False and not code:
            return render_template("home.html", error="Por favor, digite o código da sala", code=code, name=name)

        if code not in rooms:
            return render_template("home.html", error="Código da sala incorreto", code=code, name=name)
        if name.lower() in users:
            return render_template("home.html", error="Esse nome de usuário já existe", code=code, name=name)
        
        for todo in todos:
            todo["users_name_not_finished"].append(name.lower())
        
        users.append(name.lower())
        doneTodos[name] = []

        session["room"] = roomID
        session["name"] = name

        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    global roomID
    global todos
    room = session.get("room")
    name = session.get('name')
    messages = rooms[room]["messages"]

    if room is None or session.get("name") is None or room not in rooms or name not in rooms[roomID]["doneTodos"]:
        return redirect(url_for("home"))

    doneTodos = rooms[roomID]["doneTodos"][name]

    for todo in todos:
        todo["users_not_finished"] += 1

    socketio.emit('user-doing-todo', todos, namespace=f'/dashboard')


    return render_template("room.html", code=room, messages=rooms[room]["messages"], todos=todos, doneTodos=doneTodos)

@app.route('/check/<todoID>')
def check(todoID):
    # TODO: verificar se há nome
    # TODO: validar Todo concluída
    # TODO: evitar Todos concluídas repetidas


    global roomID
    global todos
    global rooms
    global room

    name = session.get('name')
    room = session.get("room")
    members = rooms[room]["members"]

    doneTodos = rooms[roomID]["doneTodos"][name]
    doneTodos.append(todoID)

    for todo in todos:
        if todo["id"] == todoID:
            todo["users"].append(name)
            todo[ "users_name_not_finished"].remove(name)
            todo["users_finished"] += 1
            todo["users_not_finished"] -= 1
            print(todo["users_not_finished"])
            break

    todo = next(todo for todo in todos if todo["id"] == todoID)
    content = {
        "name": session.get("name"),
        "todo": todo['id'],
    }
    socketio.emit('user-done-todo', todos, namespace=f'/dashboard')



    return 'OK'


@app.route('/dashboard/<room_id>')
def dashboard(room_id):

    if room_id in rooms:
        global todos
        return render_template("dashboard.html" , todos=todos)
    else:
        return render_template("error.html") 

@socketio.on("message")
def message(data):
    room = session.get("room")
    messages = rooms[room]["messages"]
    

    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    messages.append(content)

    last_user = messages[-1]["name"]
    last_message = messages[-1]["message"]
    
    if(last_user == "administrator" and last_message[0:9] == "HELPE AI:"):
        content = {
        "name": "Eisten IA",
        "message": "Resposta da IA"
    }
        send(content, to=room)
        messages.append(content)

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "🚪 Entrou na sala"}, to=room)
    rooms[room]["members"] += 1

@socketio.on("connect", namespace="/dashboard")
def connect(auth):
    global todos
    emit('state', todos)

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1

    send({"name": name, "message": "🚪 Saiu da sala"}, to=room)




if __name__ == "__main__":
    socketio.run(app, debug=True)