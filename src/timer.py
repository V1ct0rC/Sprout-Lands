import pygame

class Timer:
    """
    Timer class to be used in the game. It can be used to delay an action or to measure the time between two events.
    """
    def __init__(self, duration, function=None):
        self.duration = duration
        self.time_0 = 0
        self.active = False
        
        # If a function is given, it will be executed when the timer is done
        self.function = function
        
    def activate(self):
        """
        Activate the timer.
        """
        self.active = True
        self.time_0 = pygame.time.get_ticks()  # Get the current time in milliseconds
        
    def deactivate(self):
        """
        Deactivate the timer.
        """
        self.active = False
        self.time_0 = 0
        
    def update(self):
        """
        Update the timer.
        """
        time = pygame.time.get_ticks()  # Get the current time in milliseconds
        if time - self.time_0 >= self.duration:
            if self.function is not None and self.time_0 != 0:  # If a function is given, execute it
                self.function()
                
            self.deactivate()