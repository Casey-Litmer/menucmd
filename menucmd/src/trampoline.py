

class TrampolineRunner:
    def __init__(self):
        self.results = []

    def run(self, start_callable):
        call = start_callable
        while isinstance(call, tuple) and call[0] == '__next__':
            _, func, args = call
            result = func(*args)
            self.results.append(result)
            call = result if isinstance(result, tuple) else None
        return result
    