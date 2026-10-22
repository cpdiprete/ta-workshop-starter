document.addEventListener('DOMContentLoaded', fetchTasks);

async function fetchTasks() {
    const response = await fetch('/api/tasks');
    const tasks = await response.json();
    const taskList = document.getElementById('task-list');
    taskList.innerHTML = '';

    tasks.forEach(task => {
        const priority = ['Low', 'Medium', 'High'].includes(task.priority)
            ? task.priority
            : 'Medium';
        const li = document.createElement('li');
        const title = document.createElement('span');
        const priorityLabel = document.createElement('span');
        const deleteButton = document.createElement('button');

        title.textContent = task.title;
        priorityLabel.textContent = priority;
        priorityLabel.className = `priority priority-${priority.toLowerCase()}`;
        deleteButton.textContent = 'Delete';
        deleteButton.className = 'delete-btn';
        deleteButton.addEventListener('click', () => deleteTask(task.id));

        const taskDetails = document.createElement('span');
        taskDetails.className = 'task-details';
        taskDetails.append(title, priorityLabel);
        li.append(taskDetails, deleteButton);
        taskList.appendChild(li);
    });
}

async function addTask() {
    const titleInput = document.getElementById('task-title');
    const priorityInput = document.getElementById('task-priority');
    const title = titleInput.value.trim();

    if (!title) return;

    await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            title,
            priority: priorityInput.value
        })
    });

    titleInput.value = '';
    priorityInput.value = 'Medium';
    fetchTasks();
}

async function deleteTask(id) {
    await fetch(`/api/tasks/${id}`, {
        method: 'DELETE'
    });
    fetchTasks();
}
