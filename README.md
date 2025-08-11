# ambulance-dispatching-implementations

The repository covers ambulance dispatching 

- simulation implementation
- relative value iteration implementation
- lp modeling implementation 


## Simulation Implementation

runnder.ipynb --> this is a jupyter notebook file in which user can run the simulation

Simulation.py --> this is the most critical file and class in this project. We initialize most of the attributes such as which dispatch policy will be used, what the size of the grid world will be, etc.. After generating patients and ambulances, we run the simulation model in this class.

Patient.py --> patients are the entities which move withing the simulation. In this file, a class named Patient is created

Ambulance.py --> this is for creating a class named Ambulance. Some attributes are defined in the class to gather the required statistics of the service providers.

helper_functions.py --> some simple transformation and data generation functions such as coordinate to index, index to coordinate, or manhattan distance calculator


## Relative Value Iteration Implementation

## LP Modeling Implementation