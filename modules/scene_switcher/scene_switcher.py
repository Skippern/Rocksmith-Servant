from utils import logger


class SceneSwitcher:
    def __init__(self, config_data):
        """
        Scene Switcher
        """
        self.enabled = config_data.scene_switcher.enabled
        pass

    def run(self):
        if self.enabled:
            # TODO create main method and call it from here like other
            logger.warning("TODO Scene switcher!")
