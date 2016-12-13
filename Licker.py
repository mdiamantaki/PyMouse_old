import pygame

class Licker:
    """ this class handles the licks
    """

    def lick(self):
        response = False

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    response = True

        return response

