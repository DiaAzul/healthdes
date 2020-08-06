""" HealthDES - A python library to support discrete event simulation in health and social care """

import simpy
from .Routing import Activity_ID


class DecisionBase:

    # TODO: Need to return a function which includes list of next activities
    def set_next_activity(self, activity):
        return self.get_next_activity

    def get_next_activity(self, person, activity_a):
        """ Dummy method to anchor class """
        return Activity_ID(None, None, None)


class NextActivity(DecisionBase):

    def set_next_activity(next_activity_id):
        pass

    def get_next_activity(self, person, activity_a):

        # TODO: Need to sort routing access
        activity = person.routing.get_activity(activity_a.routing_id)

        # Add this instance to the arguments list
        activity.kwargs['person'] = self

        # Create two communication pipes for bi-directional communication with activity
        activity.kwargs['message_to_activity'] = simpy.Store(self.env)
        activity.kwargs['message_to_person'] = simpy.Store(self.env)

        return activity
