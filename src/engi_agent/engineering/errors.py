"""Engineering infeasibility is distinct from an execution or provider error."""


class EngineeringFailure(ValueError):
    """Valid inputs and calculations cannot produce a feasible beam scheme."""
