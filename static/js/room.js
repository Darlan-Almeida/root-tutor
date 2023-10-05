var socketio = io()

const messages = document.getElementById('messages')
const message = document.getElementById('message')

const createMessage = (name, msg) => {
  const content = `
  <div class="message-content">
      <strong class="name">${escapeHTML(name)}</strong>
      <div class="msg">${escapeHTML(msg)}</div>
      <div class="time">
          ${new Date().toLocaleString()}
      </div>
  </div>
  `
  messages.innerHTML += content
  scrollBottom()
}

const scrollBottom = () => {
  messages.scrollTo({ left: 0, top: messages.scrollHeight, behavior: 'smooth' })
}

socketio.on('message', (data) => {
  createMessage(data.name, data.message)
})

message.addEventListener('keyup', (e) => {
  if (e.key === 'Enter') sendMessage()
})

const sendMessage = () => {
  if (message.value == '') return
  socketio.emit('message', { data: message.value })
  message.value = ''
}

document.addEventListener('load', scrollBottom)

// Escapa caracteres do HTML
function escapeHTML(html) {
  return html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

const $todos = document.querySelectorAll('.todo')
for (const $todo of $todos) {
  $todo.addEventListener('click', checkTodo)
}

function checkTodo(e) {
  const id = e.target.dataset.id
  let url = '/check/' + id
  if (e.target.classList.contains('done')) {
    url = '/uncheck/' + id
  }
  e.target.classList.toggle('done')

  fetch(url)
}
