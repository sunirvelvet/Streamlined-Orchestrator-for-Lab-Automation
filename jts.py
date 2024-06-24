import json
import processscheduler as ps
from itertools import combinations
from datetime import datetime, timezone
import matplotlib.pyplot as plt
import streamlit as st
from io import BytesIO

# Initialize session state
if 'tasks' not in st.session_state:
    st.session_state.tasks = []

if 'task_counter' not in st.session_state:
    st.session_state.task_counter = 0

# Example initial JSON input
initial_json_input = '''
{
  "scheduler": {
    "tasks": [
      {
        "taskId": "T001",
        "taskName": "Sample Preparation",
        "description": "Prepare samples for analysis",
        "startTime": "2024-06-23T09:00:00Z",
        "endTime": "2024-06-23T10:00:00Z",
        "equipment": ["Centrifuge", "Pipette"],
        "assignedTo": "John Doe",
        "priority": "High",
        "dependencies": []
      },
      {
        "taskId": "T002",
        "taskName": "DNA Extraction",
        "description": "Extract DNA from samples",
        "startTime": "2024-06-23T10:30:00Z",
        "endTime": "2024-06-23T12:00:00Z",
        "equipment": ["DNA Extractor", "PCR Machine"],
        "assignedTo": "Jane Smith",
        "priority": "Medium",
        "dependencies": ["T001"]
      }
    ],
    "equipmentAvailability": {
      "Centrifuge": [
        {
          "availableFrom": "2024-06-23T09:00:00Z",
          "availableTo": "2024-06-23T12:00:00Z"
        }
      ],
      "Pipette": [
        {
          "availableFrom": "2024-06-23T09:00:00Z",
          "availableTo": "2024-06-23T10:00:00Z"
        }
      ],
      "DNA Extractor": [
        {
          "availableFrom": "2024-06-23T10:30:00Z",
          "availableTo": "2024-06-23T12:00:00Z"
        }
      ],
      "PCR Machine": [
        {
          "availableFrom": "2024-06-23T10:30:00Z",
          "availableTo": "2024-06-23T14:30:00Z"
        }
      ],
      "Computer": [
        {
          "availableFrom": "2024-06-23T09:00:00Z",
          "availableTo": "2024-06-23T17:00:00Z"
        }
      ],
      "Data Analysis Software": [
        {
          "availableFrom": "2024-06-23T15:00:00Z",
          "availableTo": "2024-06-23T17:00:00Z"
        }
      ]
    }
  }
}
'''

# Load initial tasks from JSON
initial_data = json.loads(initial_json_input)
if 'initialized' not in st.session_state:
    st.session_state.tasks = initial_data['scheduler']['tasks']
    st.session_state.initialized = True

# Function to render Gantt chart
def render_gantt_chart(tasks):
    task_list = tasks
    equipment_availability = initial_data['scheduler']['equipmentAvailability']

    flow_shop_problem = ps.SchedulingProblem(name="FlowShop")
    workers = {equip: ps.Worker(name=equip) for equip in equipment_availability.keys()}
    tasks_ps = {}

    for task in task_list:
        task_id = task['taskId']
        start_time = datetime.fromisoformat(task['startTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
        end_time = datetime.fromisoformat(task['endTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
        duration = int((end_time - start_time).total_seconds() / 3600)  # Convert duration to integer
        tasks_ps[task_id] = ps.FixedDurationTask(name=task['taskName'], duration=duration)
        for equip in task['equipment']:
            tasks_ps[task_id].add_required_resource(workers[equip])

    base_date = datetime(2024, 6, 23, tzinfo=timezone.utc)
    for task in task_list:
        start_time = datetime.fromisoformat(task['startTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
        start_time_offset = int((start_time - base_date).total_seconds() / 3600)  # Convert start_time to integer
        ps.TaskStartAfter(task=tasks_ps[task['taskId']], value=start_time_offset)

    for task in task_list:
        for dep in task['dependencies']:
            ps.TaskPrecedence(task_before=tasks_ps[dep], task_after=tasks_ps[task['taskId']])

    makespan_obj = ps.ObjectiveMinimizeMakespan()
    solver = ps.SchedulingSolver(problem=flow_shop_problem)
    solution = solver.solve()

    if solution is None:
        st.error("No feasible solution found for the given tasks.")
        return None

    fig, ax = plt.subplots(figsize=(10, 5))
    ps.render_gantt_matplotlib(solution, render_mode="Resource")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf

# Interface to add a new task
st.sidebar.header("Add New Task")
with st.sidebar.form("new_task_form"):
    task_name = st.text_input("Task Name")
    task_description = st.text_area("Description")
    task_start_time = st.text_input("Start Time (YYYY-MM-DDTHH:MM:SSZ)")
    task_end_time = st.text_input("End Time (YYYY-MM-DDTHH:MM:SSZ)")
    task_equipment = st.text_input("Equipment (comma-separated)")
    task_assigned_to = st.text_input("Assigned To")
    task_priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    task_dependencies = st.text_input("Dependencies (comma-separated task IDs)")
    submit_button = st.form_submit_button(label="Add Task")

    if submit_button:
        new_task_id = f"T{st.session_state.task_counter + 1:03d}"
        new_task = {
            "taskId": new_task_id,
            "taskName": task_name,
            "description": task_description,
            "startTime": task_start_time,
            "endTime": task_end_time,
            "equipment": [equip.strip() for equip in task_equipment.split(",")],
            "assignedTo": task_assigned_to,
            "priority": task_priority,
            "dependencies": [dep.strip() for dep in task_dependencies.split(",") if dep.strip()]
        }
        st.session_state.tasks.append(new_task)
        st.session_state.task_counter += 1
        st.success(f"Task {new_task_id} added successfully!")

# Interface to delete a task
st.sidebar.header("Delete Task")
task_to_delete = st.sidebar.selectbox("Select Task to Delete", [task['taskId'] for task in st.session_state.tasks])
delete_button = st.sidebar.button("Delete Task")

if delete_button:
    st.session_state.tasks = [task for task in st.session_state.tasks if task['taskId'] != task_to_delete]
    st.success(f"Task {task_to_delete} deleted successfully!")

# Display tasks and Gantt chart
st.header("Task List")
st.write(st.session_state.tasks)

st.header("Gantt Chart")
gantt_chart = render_gantt_chart(st.session_state.tasks)
if gantt_chart:
    st.image(gantt_chart)
