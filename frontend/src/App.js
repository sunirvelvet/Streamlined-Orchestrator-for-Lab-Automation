import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import Plot from 'react-plotly.js';
import './App.css';

const socket = io('http://localhost:5000');

function App() {
  const [tasks, setTasks] = useState({});
  const [chartData, setChartData] = useState([]);
  const [newTask, setNewTask] = useState({
    taskId: '',
    taskName: '',
    description: '',
    startTime: '',
    endTime: '',
    equipment: '',
    assignedTo: '',
    priority: 'Medium',
    dependencies: ''
  });

  useEffect(() => {
    socket.on('connect', () => {
      console.log('Connected to server');
    });

    socket.on('tasks', (tasks) => {
      console.log('Received tasks:', tasks);
      setTasks(tasks);
      updateChart(tasks);
    });

    socket.on('task_added', ({ task_id, task }) => {
      console.log('Task added via socket:', task_id, task);
      setTasks((prevTasks) => {
        const newTasks = { ...prevTasks, [task_id]: task };
        updateChart(newTasks);
        return newTasks;
      });
    });

    socket.on('task_deleted', ({ task_id }) => {
      console.log('Task deleted via socket:', task_id);
      setTasks((prevTasks) => {
        const newTasks = { ...prevTasks };
        delete newTasks[task_id];
        updateChart(newTasks);
        return newTasks;
      });
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  const addTask = (task) => {
    console.log('Adding task:', task);
    fetch('http://localhost:5000/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(task)
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Task added:', data);
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  };

  const deleteTask = (task_id) => {
    fetch(`http://localhost:5000/tasks/${task_id}`, {
      method: 'DELETE'
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log('Task deleted:', data);
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  };

  const updateChart = (tasks) => {
    console.log('Updating chart with tasks:', tasks);
    const newChartData = Object.values(tasks).map(task => ({
      x: [task.startTime, task.endTime],
      y: [task.taskName, task.taskName],
      type: 'scatter',
      mode: 'lines',
      name: task.taskName,
    }));
    setChartData(newChartData);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewTask((prevTask) => ({ ...prevTask, [name]: value }));
  };

  const handleAddTask = () => {
    console.log('Form data:', newTask);
    addTask(newTask);
    setNewTask({
      taskId: '',
      taskName: '',
      description: '',
      startTime: '',
      endTime: '',
      equipment: '',
      assignedTo: '',
      priority: 'Medium',
      dependencies: ''
    });
  };

  return (
    <div className="App container">
      <div className="form-container">
        <h1>Real-Time Scheduler</h1>
        <div>
          <h2>Add Task</h2>
          <form>
            <input name="taskId" value={newTask.taskId} onChange={handleInputChange} placeholder="Task ID" />
            <input name="taskName" value={newTask.taskName} onChange={handleInputChange} placeholder="Task Name" />
            <input name="description" value={newTask.description} onChange={handleInputChange} placeholder="Description" />
            <input name="startTime" value={newTask.startTime} onChange={handleInputChange} placeholder="Start Time (ISO format)" />
            <input name="endTime" value={newTask.endTime} onChange={handleInputChange} placeholder="End Time (ISO format)" />
            <input name="equipment" value={newTask.equipment} onChange={handleInputChange} placeholder="Equipment" />
            <input name="assignedTo" value={newTask.assignedTo} onChange={handleInputChange} placeholder="Assigned To" />
            <select name="priority" value={newTask.priority} onChange={handleInputChange}>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
            <input name="dependencies" value={newTask.dependencies} onChange={handleInputChange} placeholder="Dependencies (comma separated)" />
            <button type="button" onClick={handleAddTask}>Add Task</button>
          </form>
        </div>
        <div>
          <h2>Delete Task</h2>
          <select onChange={(e) => deleteTask(e.target.value)}>
            <option value="">Select Task to Delete</option>
            {Object.keys(tasks).map(task_id => (
              <option key={task_id} value={task_id}>
                {tasks[task_id].taskName}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="chart-container">
        <Plot
          data={chartData}
          layout={{
            title: 'Task Schedule',
            xaxis: { title: 'Time' },
            yaxis: { title: 'Tasks' },
          }}
        />
      </div>
    </div>
  );
}

export default App;
