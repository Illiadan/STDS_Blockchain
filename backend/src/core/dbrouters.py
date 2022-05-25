from core.models import CalculationRange

class CalculationRangeDbRouter(object):

    def db_for_read(self, model, **hints):
        if model == CalculationRange:
            return 'memory'
        return None

    def db_for_write(self, model, **hints):
        """ writing SomeModel to otherdb """
        if model == CalculationRange:
            return 'memory'
        return None
