from modules.case.data_objects import Expected, Operator
class DummyExpected(Expected):
    def __init__(self, status_code=200, payload=None):
        operators = Operator.from_dict(payload)
        super().__init__(status_code=status_code, operator=operators)

    def __eq__(self, other):
        return self.expected.get("payload") == other

