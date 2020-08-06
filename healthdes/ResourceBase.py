""" HealthDES - A python library to support discrete event simulation in health and social care """


class ResourceBase:

    # TODO: Build out the do and query functions for person, activity and resource objects.
    # Need to create dictionary of actions and parameters.
    # Subclassing allows dictionary of actions/ activities to be extended.
    # Need to provide error checking if actions/ parameters not in dictionary.
    def do(self, action, **kwargs):
        """ Perform an action on the person """
        pass

    def query(self, param):
        """ Get a parameter from the person."""
        pass
