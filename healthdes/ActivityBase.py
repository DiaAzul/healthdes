""" HealthDES - A python library to support discrete event simulation in health and social care """

import yaml
import inspect
import sys

from typing import (
    TYPE_CHECKING,
    ClassVar,
    ContextManager,
    Generic,
    MutableSequence,
    Optional,
    Type,
    TypeVar,
    Union,
)


class ActivityBase():
    """Person's activity within the system, models interaction between people and environment """

    # The following dictionary defines the state diagram for the control loop
    state_diagram = yaml.load(sys.intern("""
    init:
      initialise:
        next_state: initialised
        function: initialise
        success_message: initialised
    initialised:
      seize_resources:
        next_state: resources_seized
        function: seize_resources
        success_message: resources_seized
      start:
        next_state: running
        function: seize_resources_and_run
        success_message: completed
    resources_seized:
      start:
        next_state: completed
        function: execute
        success_message: completed
    completed:
      release_resources:
        next_state: stopped
        function: release_resources
        success_message: resources_released
      end:
        next_state: ended
        function: release_resources_and_end
        success_message: ended
    stopped:
      end:
        next_state: ended
        function: end
        success_message: ended
    """), Loader=yaml.SafeLoader)

    def __init__(self, simulation_params, **kwargs) -> None:
        """Create a new activity

        Arguments:
            simulation_params {dictionary} -- keyword arguments for the simulation
            kwargs {dictionary} -- Keyword arguments for the activity
        """
        self.env = simulation_params.get('simpy_env', None)
        self.dc = simulation_params.get('data_collector', None)
        self.time_interval = simulation_params.get('time_interval', None)

        self.person = kwargs['person']
        self.message_to_activity = kwargs['message_to_activity']
        self.message_to_person = kwargs['message_to_person']

        self.unpack_parameters(**kwargs)

    def unpack_parameters(self, **kwargs) -> None:
        pass

    def run(self) -> None:
        """Run the event loop for the activity

        The event loop dispatches events in response to communication from the person class
        """
        function_dict = {
            'initialise': self.initialise,
            'seize_resources_and_execute': self.seize_resources_and_execute,
            'seize_resources': self.seize_resources,
            'execute': self.execute,
            'release_resources_and_end': self.release_resources_and_end,
            'release_resources': self.release_resources,
            'end': self.end
        }

        state = 'init'

        finished = False
        while not finished:
            # set an event flag to mark end of activity and call the activity class
            received_message = yield self.message_to_activity.get()

            actions = ActivityBase.state_diagram.get(state, 'NoState') \
                                                .get(received_message, 'NoMessage')
            if actions == 'NoState':
                raise ValueError('Activity state error')
            if actions == 'NoMessage':
                raise ValueError('Activity received message error')

            next_state = actions['next_state']
            action = actions['function']
            success_message = actions['success_message']

            if not function_dict.get(action, None):
                raise ValueError(f'Activity function {action} missing')

            # Check whether subclassed method is a generator, which requires
            # different calling pattern
            if inspect.isgeneratorfunction(function_dict.get(action)):
                for result in function_dict.get(action)():
                    pass
            else:
                function_dict.get(action)()

            state = next_state

            self.message_to_person.put(success_message)

            finished = True if state == 'ended' else finished

    def nop(self) -> None:
        pass

    def initialise(self) -> None:
        pass

    def seize_resources_and_execute(self) -> None:
        self.seize_resources()
        self.execute()

    def seize_resources(self) -> None:
        pass

    def execute(self) -> None:
        pass

    def release_resources_and_end(self) -> None:
        self.release_resources()
        self.end()

    def release_resources(self) -> None:
        pass

    def end(self) -> None:
        pass
