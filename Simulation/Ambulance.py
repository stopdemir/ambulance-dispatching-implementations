class Ambulance:
    def __init__(self, id, location):
        self.id = id
        self.location = location
        self.is_busy = False
        self.current_patient_location = None
        self.time_busy_total = 0.0
        self.service_times = []
    
    def __repr__(self):
        return f"Ambulance {self.id} at {self.location} (Busy: {self.is_busy})"
    
    