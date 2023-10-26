var socketio = io('/dashboard')
var $dashboardTodos = document.querySelector('.dashboard-todos')
let state = []

socketio.on('state', (newState) => {
  state = newState
  generateDashboardTable()
})

socketio.on('user-done-todo', ({ name, todo: todoID }) => {
  state = state.map((todo) => {
    if (todo.id !== todoID) return todo
    todo.users.push(name)
    todo.users_finished += 1
    return todo
  })
  generateDashboardTable()
})

function generateDashboardTable() {
  $dashboardTodos.innerHTML = ''
  for (const todo of state) {
    const $row = document.createElement('tr')
    const $name = document.createElement('td')
    const $users = document.createElement('td')
    const $users_finished = document.createElement('td')
    const $users_not_finished = document.createElement('td')
    $name.innerText = todo.name
    $users_finished.innerText = todo.users_finished
    $users_not_finished.innerText = todo.users_not_finished
    for (const user of todo.users) {
      const $name = document.createElement('div')
      $name.innerText = user
      $users.appendChild($name)
    }
    $row.appendChild($name)
    $row.appendChild($users)
    $row.appendChild($users_finished)
    $row.appendChild($users_not_finished)
    $dashboardTodos.appendChild($row)
  }
}
