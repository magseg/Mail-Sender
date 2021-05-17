class Command(object):
    def execute(self):
        self.validate()
        return self.execute_validated()

    def validate(self):
        raise NotImplementedError()

    def execute_validated(self):
        raise NotImplementedError()
