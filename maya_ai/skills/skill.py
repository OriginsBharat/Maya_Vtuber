from abc import ABC, abstractmethod

class Skill(ABC):
    """
    An abstract base class for any skill that Maya can learn.
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Returns the unique name of the skill.
        """
        pass

    @abstractmethod
    def get_possible_actions(self) -> list:
        """
        Returns a list of actions this skill can perform.
        Each action should be a dictionary with 'name' and 'description'.
        """
        pass

    @abstractmethod
    def perform_action(self, action_name: str, **kwargs) -> str:
        """
        Performs a specific action.

        Args:
            action_name: The name of the action to perform.
            **kwargs: Any arguments the action might need.

        Returns:
            A string describing the result of the action.
        """
        pass
