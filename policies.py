import random
from helper_functions import GridHelper

################### DISPATCH CLOSEST AMBULANCE POLICY ##################
def dispatch_closest_ambulance(grid_size, available_ambulances, customer_location):
    grid_object = GridHelper(n=grid_size[0]) # this is necessary to use the GridHelper class for distance calculations
    
    if not available_ambulances:
            return None

    best_ambulance = None
    min_travel_time = float('inf')

    for amb in available_ambulances:
        travel_time = grid_object.calculate_manhattan_distance(amb.location, customer_location)
        if travel_time < min_travel_time:
            min_travel_time = travel_time
            best_ambulance = amb
            
    return best_ambulance


#################### DISPATCH RANDOM AMBULANCE POLICY ################### 
def dispatch_random_ambulance(grid_size, available_ambulances, customer_location):
    if not available_ambulances:
        return None
    return random.choice(available_ambulances)













##################### DISPATCH HIGH PRIORITY FIRST POLICY ################### not working currently
def dispatch_high_priority_first(available_ambulances, customer_location, current_time):
    """
    This policy would ideally prioritize high-priority customers from a queue.
    However, as per the paper's assumption 6: "There is a zero-length queue for customers."
    This means customers are either served immediately or lost.
    Therefore, in this current simulation structure, this policy will behave
    like dispatch_closest_ambulance as it simply dispatches to the arriving customer.
    To truly implement priority, a customer queue would be needed in the Simulation class.
    Args:
        available_ambulances (list): List of available Ambulance objects.
        customer_location (tuple): (row, col) of the customer.
        current_time (float): Current simulation time. (Not used in this policy, but kept for signature consistency)
    Returns:
        Ambulance: The chosen Ambulance object, or None if no suitable ambulance is found.
    """
    # For now, if a customer arrives and an ambulance is free, dispatch the closest.
    # This function would need to be re-evaluated if a customer queue is introduced.
    return dispatch_closest_ambulance(available_ambulances, customer_location, current_time)