from enum import Enum


class Method(Enum):
    BRUTE_FORCE = 'brute_force'
    NEAREST_NEIGHBOUR = 'nearest_neighbour'

    def label(self) -> str:
        """
        Return label name of the method.
        Returns:
            the method name without the underscore
        """
        return self.name.replace("_", " ").lower()
