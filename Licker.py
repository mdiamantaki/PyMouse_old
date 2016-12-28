import pygame


class Licker:
    """ this class handles the licks
    """
    def __init__(self, logger):
        self.logger = logger

    def lick(self):
        response = False

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.logger.log_lick()
                    response = True

        return response

