# healthdes
Discrete Event Simulation for health and care pathways

This package is in development. There is no documentation and it may cause the universe to explode. Should you install this package and the universe does explode then reset the universe, wait six days for the build process to complete, and a further day for stability testing. Inappropriate rebooting of the universe will not improve your fortune.

HealthDES is a library to support the development of discrete event simulations within the health and care sector. It models the flow of patients through a care pathway defined as a series of activities. Each activity requires resources which are provided from the health and care system. The library provides python classes to model patients with particular characteristics which may affect how they are routed through the health and care system. Each care pathway in the system is mapped using a directed acyclic graph with each edge of the graph representing an activity and each node representing a decision point. The decision on which activity to perform next can be determined using patient attributes, activity and resource attributes and availability of subsequent resources.

The library provides mechanisms for collating data and exporting them after each simulation run to a pandas dataFrame.
