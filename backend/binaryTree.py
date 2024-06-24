import json
from collections import deque

class Node:
    def __init__(self, name):
        self.name = name
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"Node({self.name})"

class SequenceNode(Node):
    def __init__(self, name):
        super().__init__(name)

class ParallelNode(Node):
    def __init__(self, name):
        super().__init__(name)

class ConditionNode(Node):
    def __init__(self, name, condition):
        super().__init__(name)
        self.condition = condition

class ActionNode(Node):
    def __init__(self, name, action):
        super().__init__(name)
        self.action = action

def check_equipment_availability(equipment, availability):
    # Placeholder function to simulate equipment availability check
    return all(equip in availability for equip in equipment)

def create_behavior_tree(task_list, equipment_availability):
    root = ParallelNode("Scheduler")
    task_sequence = SequenceNode("Execute all tasks in order")
    root.add_child(task_sequence)

    task_map = {task["taskId"]: task for task in task_list}

    for task in task_list:
        task_node = SequenceNode(f"Task - {task['taskName']} ({task['taskId']})")
        
        for equip in task["equipment"]:
            task_node.add_child(ConditionNode(f"Check Equipment Availability: {equip}", lambda: check_equipment_availability([equip], equipment_availability)))
        
        task_node.add_child(ActionNode(f"Assign Task to {task['assignedTo']}", lambda: print(f"Assign Task {task['taskId']} to {task['assignedTo']}")))
        task_node.add_child(ActionNode(f"{task['description']}", lambda: print(f"Perform Task {task['taskId']}: {task['description']}")))

        if task["dependencies"]:
            for dep in task["dependencies"]:
                task_node.add_child(ConditionNode(f"Check if Task {dep} is complete", lambda: True))  # Simplified condition

        task_sequence.add_child(task_node)

    interrupt_handler = ConditionNode("Check for new urgent tasks", lambda: False)  # Placeholder for checking new tasks
    urgent_task_sequence = SequenceNode("Handle new urgent task")
    interrupt_handler.add_child(urgent_task_sequence)

    urgent_task_sequence.add_child(ConditionNode("Check Equipment Availability: Required equipment for urgent task", lambda: True))  # Simplified condition
    urgent_task_sequence.add_child(ActionNode("Assign urgent task to appropriate personnel", lambda: print("Assign urgent task")))
    urgent_task_sequence.add_child(ActionNode("Perform urgent task", lambda: print("Perform urgent task")))

    root.add_child(interrupt_handler)
    return root

def print_tree(node, indent=0):
    print(' ' * indent + node.name)
    for child in node.children:
        print_tree(child, indent + 4)

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

bt_root = create_behavior_tree(task_list, equipment_availability)
print_tree(bt_root)
