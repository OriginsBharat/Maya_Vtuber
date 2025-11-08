import psutil
from maya_ai.config.config_loader import get_config
from loguru import logger

class StateManager:
    """
    Detects and manages the current "state" or "context" of the system.
    This allows the AI to be aware of what the user is primarily doing.
    """
    def __init__(self):
        self.config = get_config()
        self.context_processes = self.config.get('state_manager', 'context_processes', {})
        logger.info(f"StateManager initialized. Will track the following contexts: {list(self.context_processes.keys())}")

    def get_current_state(self) -> str:
        """
        Determines the current state by checking for known running processes.

        Returns:
            A string representing the most likely current state (e.g., "Watching Video"),
            or a default state ("Idle") if no known context is detected.
        """
        try:
            for process in psutil.process_iter(['name']):
                proc_name = process.info['name'].lower()
                for state, process_list in self.context_processes.items():
                    if any(p.lower() in proc_name for p in process_list):
                        logger.debug(f"Detected running process '{proc_name}', setting state to '{state}'.")
                        return state
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # These are expected errors when iterating through processes, can be ignored.
            pass
        except Exception as e:
            logger.error(f"An unexpected error occurred while checking processes: {e}", exc_info=True)

        return self.config.get('state_manager', 'default_state', 'Idle')
