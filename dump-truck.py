import random
import pandas as pd
import numpy as np

# Set random seed for reproducibility.
random.seed(42)
rng = np.random.default_rng(42)

# Define the probabilistic distributions.
def get_loading_time():
    #return random.choice([2, 3, 4])
    # distribusi normal
    mean = 3
    std_dev = 1
    return rng.normal(mean, std_dev)

def get_weighing_time():
    return random.choice([1, 2])


def get_travel_time():
    #return random.choice(list(range(8, 16)))
    mean = 12
    std_dev = 1
    return rng.normal(mean, std_dev)


def get_initial_arrival_times():
    #arrival_times = random.sample(range(0, 9), 6)
    arrival_times = [0 * 6]
    trucks = ['DT1', 'DT2', 'DT3', 'DT4', 'DT5', 'DT6']
    return dict(zip(trucks, sorted(arrival_times)))


# Initialize variables.
num_trucks = 6
trucks = ['DT1', 'DT2', 'DT3', 'DT4', 'DT5', 'DT6']
arrival_times = get_initial_arrival_times()
events = []
time = 0

# State variables.
loader_queue = []
weigh_queue = []
loader_busy_until = [0, 0]  # Two loaders.
weigher_busy_until = 0
cumulative_loading_time = 0
cumulative_weighing_time = 0

# Truck status dictionaries.
truck_next_available_time = {truck: 0 for truck in trucks}
truck_cycle = {truck: 0 for truck in trucks}  # Counts the number of cycles completed.

# Event list.
event_list = []

# Schedule initial arrival events.
for truck, arrival_time in arrival_times.items():
    event_list.append({
        'Time': arrival_time,
        'Event': 'Arrival at Loading Queue',
        'Truck ID': truck
    })

running_time = 0
# Simulation loop.
while len(event_list) > 0 and time < 100:  # Arbitrary simulation end time.
    # Sort events by time.
    event_list.sort(key=lambda x: x['Time'])
    # Get next event.
    event = event_list.pop(0)
    running_time = time = event['Time']
    truck_id = event['Truck ID']
    event_type = event['Event']

    if event_type == 'Arrival at Loading Queue':
        # Truck arrives at loading queue.
        loader_queue.append(truck_id)
        # Check for available loader.
        for i in range(len(loader_busy_until)):
            if loader_busy_until[i] <= time:
                if loader_queue:
                    next_truck = loader_queue.pop(0)
                    loading_time = get_loading_time()
                    loader_busy_until[i] = time + loading_time
                    cumulative_loading_time += loading_time
                    event_list.append({
                        'Time': loader_busy_until[i],
                        'Event': 'Loading Ends',
                        'Truck ID': next_truck,
                        'Loader ID': i
                    })
                    break  # Loader assigned.
    elif event_type == 'Loading Ends':
        # Truck finished loading, move to weighing queue.
        weigh_queue.append(truck_id)
        # Check if weigher is available.
        if weigher_busy_until <= time and weigh_queue:
            next_truck = weigh_queue.pop(0)
            weighing_time = get_weighing_time()
            weigher_busy_until = time + weighing_time
            cumulative_weighing_time += weighing_time
            event_list.append({
                'Time': weigher_busy_until,
                'Event': 'Weighing Ends',
                'Truck ID': next_truck
            })
    elif event_type == 'Weighing Ends':
        # Truck finished weighing, schedule return after travel time.
        travel_time = get_travel_time()
        next_arrival_time = time + travel_time
        truck_next_available_time[truck_id] = next_arrival_time
        truck_cycle[truck_id] += 1
        event_list.append({
            'Time': next_arrival_time,
            'Event': 'Arrival at Loading Queue',
            'Truck ID': truck_id
        })
        # Check if another truck is waiting in the weigh queue.
        if weigh_queue and weigher_busy_until <= time:
            next_truck = weigh_queue.pop(0)
            weighing_time = get_weighing_time()
            weigher_busy_until = time + weighing_time
            cumulative_weighing_time += weighing_time
            event_list.append({
                'Time': weigher_busy_until,
                'Event': 'Weighing Ends',
                'Truck ID': next_truck
            })
    # Record event.
    events.append({
        'Time': time,
        'Event': event_type,
        'Truck ID': truck_id,
        'Arrival Time': arrival_times.get(truck_id, ''),
        'Loading Start': time if event_type == 'Loading Ends' else '',
        'Loading End': loader_busy_until[0] if event_type == 'Loading Ends' else '',
        'Weighing Start': time if event_type == 'Weighing Ends' else '',
        'Weighing End': weigher_busy_until if event_type == 'Weighing Ends' else '',
        'Travel Time': travel_time if event_type == 'Weighing Ends' else '',
        'Cumulative Loading Time': cumulative_loading_time,
        'Cumulative Weighing Time': cumulative_weighing_time,
        'Loader Queue Length': len(loader_queue),
        'Weigh Queue Length': len(weigh_queue),
    })

# Create DataFrame for better display.
df = pd.DataFrame(events)

# Clean up DataFrame for display.
df = df[['Time', 'Event', 'Truck ID', 'Arrival Time', 'Loading Start', 'Loading End',
         'Weighing Start', 'Weighing End', 'Travel Time', 'Cumulative Loading Time',
         'Cumulative Weighing Time', 'Loader Queue Length', 'Weigh Queue Length']]

# Convert empty strings to None.
df.replace('', None, inplace=True)

# Display the table.
print(df.to_string(index=False))

print("Loader utils", loading_time / 2.0 / running_time)
print("Scale utils", weighing_time / running_time)