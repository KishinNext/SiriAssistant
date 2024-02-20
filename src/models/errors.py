import traceback


class Missing(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.traceback = traceback.format_exc()


class Duplicate(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.traceback = traceback.format_exc()
