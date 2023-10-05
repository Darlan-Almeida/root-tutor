from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase


app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)


roomID = 'versionamento321'
rooms = {}
rooms[roomID] = { "members": 0, "messages":[] }

@app.route("/", methods=["POST", "GET"])
def home():
    global roomID

    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Por favor, digite seu nome", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Por favor, digite o código da sala", code=code, name=name)

        if code not in rooms:
            return render_template("home.html", error="Código da sala incorreto", code=code, name=name)

        session["room"] = roomID
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

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
    rooms[room]["members"] += 1

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