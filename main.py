from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO, emit


app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)


roomID = 'versionamento321'
rooms = {}
rooms[roomID] = { "members": 0, "messages":[], "users":[], "doneTodos": {} }

todos = [
    { "id": "instalar-git", "name": "Instalar Git" , "users": [] , "users_finished" : 0},
    { "id": "clonar-repo", "name": "Clonar repositório", "users": [] , "users_finished" : 0 },
    {"id": "comitar-repo", "name": "Clonar repositório", "users": [] , "users_finished" : 0 }
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

    if room is None or session.get("name") is None or room not in rooms or name not in rooms[roomID]["doneTodos"]:
        return redirect(url_for("home"))

    doneTodos = rooms[roomID]["doneTodos"][name]

    print(doneTodos)

    return render_template("room.html", code=room, messages=rooms[room]["messages"], todos=todos, doneTodos=doneTodos)

@app.route('/check/<todoID>')
def check(todoID):


    global roomID
    global todos


    name = session.get('name')

    doneTodos = rooms[roomID]["doneTodos"][name]
    doneTodos.append(todoID)

    for todo in todos:
        if todo["id"] == todoID:
            todo["users"].append(name)
            todo["users_finished"] += 1
            print(todo["users"])
            break

    todo = next(todo for todo in todos if todo["id"] == todoID)
    content = {
        "name": session.get("name"),
        "todo": todo['id'],
        "users_finished": todo["users_finished"]
    }
    socketio.emit('user-done-todo', content, namespace=f'/dashboard')
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
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)

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
    #rooms[room]["members"] += 1

@socketio.on("connect", namespace="/dashboard")
def connect(auth):
    global todos
    print("Administrador conectado")
    emit('state', todos)

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        # if rooms[room]["members"] <= 0:
        #     del rooms[room]
    
    send({"name": name, "message": "🚪 Saiu da sala"}, to=room)


#rota em que será implementada o passo a passo do tutorial
@app.route("/tutor")
def tutor():
    return render_template("tutor.html")

if __name__ == "__main__":
    socketio.run(app, debug=True)