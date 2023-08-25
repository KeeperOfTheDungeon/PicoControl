from RoboControl.Robot.Component.Actor.Led.LedSet import LedSet
from RoboControl.Robot.Component.ComponentSet import ComponentSet

#unused
class PicoLedSet(ComponentSet):
	def __init__(self, components, protocol):
        pass
    
    
    def process():
        for component in self._component_list:
            component.process()
        
    
"""		actors = list()

		for component in components:
			actor = PicoLed(component)
			actors.append(actor)
		
		super().__init__(actors)
"""