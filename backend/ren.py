import json
import processscheduler as ps
from itertools import combinations
from datetime import datetime, timezone
import matplotlib.pyplot as plt

# Example JSON input
json_input = '''
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
      },
      {
        "taskId": "T003",
        "taskName": "PCR Amplification",
        "description": "Amplify DNA samples using PCR",
        "startTime": "2024-06-23T13:00:00Z",
        "endTime": "2024-06-23T14:30:00Z",
        "equipment": ["PCR Machine"],
        "assignedTo": "Jane Smith",
        "priority": "Medium",
        "dependencies": ["T002"]
      },
      {
        "taskId": "T004",
        "taskName": "Data Analysis",
        "description": "Analyze PCR results",
        "startTime": "2024-06-23T15:00:00Z",
        "endTime": "2024-06-23T17:00:00Z",
        "equipment": ["Computer", "Data Analysis Software"],
        "assignedTo": "John Doe",
        "priority": "Low",
        "dependencies": ["T003"]
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

data = json.loads(json_input)
task_list = data['scheduler']['tasks']
equipment_availability = data['scheduler']['equipmentAvailability']

### Create the scheduling problem
flow_shop_problem = ps.SchedulingProblem(name="FlowShop")

### Create the equipment (workers)
workers = {equip: ps.Worker(name=equip) for equip in equipment_availability.keys()}

### Create tasks and assign resources
tasks = {}
for task in task_list:
    task_id = task['taskId']
    start_time = datetime.fromisoformat(task['startTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
    end_time = datetime.fromisoformat(task['endTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
    duration = int((end_time - start_time).total_seconds() / 3600)  # Convert duration to integer
    tasks[task_id] = ps.FixedDurationTask(name=task['taskName'], duration=duration)
    for equip in task['equipment']:
        tasks[task_id].add_required_resource(workers[equip])

### Constraint: release dates (start times)
base_date = datetime(2024, 6, 23, tzinfo=timezone.utc)
for task in task_list:
    start_time = datetime.fromisoformat(task['startTime'].replace('Z', '+00:00')).astimezone(timezone.utc)
    start_time_offset = int((start_time - base_date).total_seconds() / 3600)  # Convert start_time to integer
    ps.TaskStartAfter(task=tasks[task['taskId']], value=start_time_offset)

### Constraint: dependencies (precedences)
for task in task_list:
    for dep in task['dependencies']:
        ps.TaskPrecedence(task_before=tasks[dep], task_after=tasks[task['taskId']])

### Add a makespan objective
makespan_obj = ps.ObjectiveMinimizeMakespan()

### Solve and render the Gantt chart
solver = ps.SchedulingSolver(problem=flow_shop_problem)
solution = solver.solve()
ps.render_gantt_matplotlib(solution, fig_size=(10, 5), render_mode="Resource")
