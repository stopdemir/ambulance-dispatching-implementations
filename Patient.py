class Patient:
    def __init__(self, id, location, priority):
        self.id = id
        self.location = location
        self.priority = priority
        self.arrival_time = 0.0
    
    def __repr__(self):
        return f"Customer {self.id} at {self.location} (Priority: {self.priority})"
    
    