################################### LIBRARIES ###################################
import random
import heapq
import numpy as np

from Ambulance import Ambulance
from Patient import Patient

from helper_functions import GridHelper

class Simulation:
    ############################ CONSTRUCTOR / INITIALIZATION OF ATTRIBUTES ###################
    def __init__(self, grid_size, ambu_locations, arr_rate, sim_duration, no_service_cells, dispatch_function, policy_name="Generic Policy"):
        self.grid_size = grid_size
        self.ambulances = [Ambulance(i, loc) for i, loc in enumerate(ambu_locations)]
        self.arr_rate = arr_rate
        self.sim_duration = sim_duration
        self.no_service_cells = no_service_cells
        self.dispatch_function = dispatch_function # Injected dispatch function
        self.policy_name = policy_name # Store policy name for results

        self.current_time = 0.0
        self.event_queue = []  # (time, event_type, data)
        self.patient_id_counter = 0

        self.patients_lost = 0
        self.total_patients_arrived = 0

        # Statistics
        self.ambulance_total_busy_time = [0.0] * len(self.ambulances)
        self.ambulance_service_times = [[] for _ in range(len(self.ambulances))]
        
        # initialize the grid helper
        self.grid_helper = GridHelper(n=grid_size[0]) 
        
        self._initialize_simulation()
        
    ############################# INITIALIZATION OF SIMULATION ########################
    def _initialize_simulation(self):
        # Schedule the first patient arrival
        self._schedule_next_arrival()
    ############################## SCHEDULING NEXT ARRIVAL ############################
    def _schedule_next_arrival(self):
        time_to_next_arrival = random.expovariate(self.arr_rate)
        arrival_time = self.current_time + time_to_next_arrival
        heapq.heappush(self.event_queue, (arrival_time, "patient_ARRIVAL", None))
    
    ############################ GENERATE (PATIENT LOCATION AND PRIORITY) AND (AMBULANCE SERVICE TIME) ############################
    # You may wanna modify this part also considering the predetermined probability values that show customer arrivals from each cell
    def _generate_patient_location(self):
        # there is a possibility that a patient arrives in cell where no service is available
        while True:
            row = random.randint(0, self.grid_size[0] - 1)
            col = random.randint(0, self.grid_size[1] - 1)
            location = (row, col)
            if location not in self.no_service_cells:
                return location

    # this part also needs to modified according to the predetermined priority values of each cell
    def _generate_patient_priority(self):
        # For simplicity, assume 50/50 chance for H/L priority
        return 'H' if random.random() < 0.5 else 'L'
    
    # you may wanna focus on this part, especially usage of different mean for service time distribution for different location and ambulance location pairs
    def _generate_service_time(self, ambulance_location, patient_location):
        base_service_rate = 0.5 # Example: 2 hours average service time (1/0.5)
        travel_time = self.grid_helper.calculate_manhattan_distance(ambulance_location, patient_location)
        
        # A simple model: service time = travel_time + exponential_processing_time
        processing_time = random.expovariate(base_service_rate)
        return travel_time + processing_time
    

    ############################ EVENT HANDLERS ############################
    def handle_patient_arrival(self):
        self.total_patients_arrived += 1
        patient_location = self._generate_patient_location()
        patient_priority = self._generate_patient_priority()
        patient = Patient(self.patient_id_counter, patient_location, patient_priority)
        patient.arrival_time = self.current_time
        self.patient_id_counter += 1

        available_ambulances = [amb for amb in self.ambulances if not amb.is_busy]

        # This is where the chosen dispatch policy is applied!
        chosen_ambulance = self.dispatch_function(self.grid_size, available_ambulances, patient_location)
        
        # if at least one ambulance is available
        if chosen_ambulance:
            chosen_ambulance.is_busy = True
            chosen_ambulance.current_patient_location = patient_location
            
            service_time = self._generate_service_time(chosen_ambulance.location, patient_location)
            
            # Schedule ambulance completion event
            completion_time = self.current_time + service_time
            heapq.heappush(self.event_queue, (completion_time, "AMBULANCE_COMPLETION", chosen_ambulance.id))

            # Record busy time and service time for statistics
            self.ambulance_total_busy_time[chosen_ambulance.id] += service_time
            self.ambulance_service_times[chosen_ambulance.id].append(service_time)

        else: # No available ambulance
            self.patients_lost += 1
            # print(f"Time {self.current_time:.2f}: patient {patient.id} lost (no available ambulances).")

        self._schedule_next_arrival()

    def handle_ambulance_completion(self, ambulance_id):
        ambulance = self.ambulances[ambulance_id]
        ambulance.is_busy = False
        ambulance.current_patient_location = None
    
    ################################# RUN SIMULATION ############################
    def run(self):
        while self.event_queue and self.current_time < self.sim_duration:
            event_time, event_type, event_data = heapq.heappop(self.event_queue)

            if event_time > self.sim_duration:
                break # Stop if the next event is beyond simulation duration

            self.current_time = event_time

            if event_type == "patient_ARRIVAL":
                self.handle_patient_arrival()
            elif event_type == "AMBULANCE_COMPLETION":
                self.handle_ambulance_completion(event_data)

        return self._get_results()

    def _get_results(self):
        results = {
            "policy_name": self.policy_name,
            "total_simulation_time": self.sim_duration,
            "total_patients_arrived": self.total_patients_arrived,
            "patients_lost": self.patients_lost,
            "patient_loss_rate": self.patients_lost / self.total_patients_arrived if self.total_patients_arrived > 0 else 0,
            "ambulance_stats": []
        }

        for i, amb in enumerate(self.ambulances):
            avg_service_time = sum(self.ambulance_service_times[i]) / len(self.ambulance_service_times[i]) if self.ambulance_service_times[i] else 0
            utilization = (self.ambulance_total_busy_time[i] / self.sim_duration) * 100
            
            results["ambulance_stats"].append({
                "ambulance_id": amb.id,
                "location": amb.location,
                "total_busy_time": self.ambulance_total_busy_time[i],
                "average_service_time": avg_service_time,
                "utilization": utilization
            })
        return results