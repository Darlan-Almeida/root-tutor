var socketio = io('/dashboard')
var $dashboardTodos = document.querySelector('.dashboard-todos')
let state = []

socketio.on('state', (newState) => {
  state = newState
  generateDashboardTable()
  generateDashboardGraph()
})

socketio.on('user-done-todo', ({ name , todo: todoID }) => {
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
    $name.innerText = todo.name
    for (const user of todo.users) {
      const $name = document.createElement('div')
      $name.innerText = user
      $users.appendChild($name)
    }
    $row.appendChild($name)
    $row.appendChild($users)
    $dashboardTodos.appendChild($row)

  }
}

function generateDashboardGraph(){
  const data = {
    labels: [], // Nomes das tarefas
    datasets: [
      {
        data: [], // Número de usuários concluídos por tarefa
        backgroundColor: [], // Cores para as fatias do gráfico
      },
    ],
  };

  // Preencher os dados com informações sobre as tarefas
  for (const todo of state) {
    data.labels.push(todo.name);
    data.datasets[0].data.push(todo.users_finished);
    // Defina cores de preenchimento aleatórias para as fatias
    const randomColor = `#${Math.floor(Math.random() * 16777215).toString(16)}`;
    data.datasets[0].backgroundColor.push(randomColor);
  }

  // Criar um contexto para o gráfico no elemento HTML
  const ctx = document.querySelector('.graph').getContext('2d');

  // Criar o gráfico de pizza
  new Chart(ctx, {
    type: 'pie',
    data: data,
  });
}


