class AbortLawError(Exception):
    """
    Custom exception to make sure that own exception types are
    caught by the Law's execution.
    """


class PreconditionFailedError(Exception):
    """
    Custom exception representing a failed precondition. In case a
    precondition failed, there is no need to raise an error and report
    the rule as a failure. The precondition is for checking that a rule
    should or shouldn't run; not for breaking the execution.
    """
