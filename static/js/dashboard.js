var socketio = io('/dashboard')
var $dashboardTodos = document.querySelector('.dashboard-todos')

socketio.on('user-doing-todo', (todos) => {
  generateDashboardTable(todos)
})

socketio.on('user-done-todo', (todos) => {
  generateDashboardTable(todos)
})

function generateDashboardTable(todos) {
  $dashboardTodos.innerHTML = ''
  for (var todo of todos) {
    var $row = document.createElement('tr')
    var $name = document.createElement('td')
    var $users = document.createElement('td')
    var $users_finished = document.createElement('td')
    var $users_not_finished = document.createElement('td')
    var $users_name_not_finished = document.createElement('td')
    $name.innerText = todo.name
    $users.innerText = todo.users
    $users_finished.innerText = todo.users_finished
    $users_not_finished.innerText = todo.users_not_finished
    $users_name_not_finished.innerText = todo.users_name_not_finished

    $row.appendChild($name)
    $row.appendChild($users)
    $row.appendChild($users_finished)
    $row.appendChild($users_not_finished)
    $row.appendChild($users_name_not_finished)
    $dashboardTodos.appendChild($row)
  }
}

let currentSlide = 1

function setSlide(slideNum) {
  setPage(currentSlide)
  socketio.emit('set-slide', slideNum)
}

socketio.on('set-slide', setSlide)

function firstSlide() {
  currentSlide = 1
  setSlide(currentSlide)
}

function prevSlide() {
  if (currentSlide <= 1) return
  currentSlide -= 1
  setSlide(currentSlide)
}

function nextSlide() {
  if (currentSlide >= pageCount) return
  currentSlide += 1
  setSlide(currentSlide)
}

function lastSlide() {
  currentSlide = pageCount
  setSlide(currentSlide)
}