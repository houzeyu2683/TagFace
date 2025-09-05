import concurrent.futures
# import sys

class Operation:

    def __init__(self, core: int) -> None:
        self.core = core
        return

    def activatePipeline(
        self, 
        queue: list, 
        function: object, 
        parameter: dict
    ) -> bool:
        total = len(queue)
        try:
            Pool = concurrent.futures.ProcessPoolExecutor
            with Pool(self.core) as job:
                work = []
                iteration = queue
                for item in iteration:
                    if(parameter=={}):
                        work += [job.submit(function, item)]
                        continue
                    # argument = dict(parameter)
                    work += [job.submit(function, item, **parameter)]
                    continue
                _ = iteration
                assert total == len(work)
                iteration = concurrent.futures.as_completed(work)
                for task in iteration:
                    _ = getattr(task, 'result')()
                    continue
                _ = iteration
                pass
            _ = job
            return(True)
        except:
            job.shutdown(wait=True, cancel_futures=True)
            pass
        _ = job
        return(True)

    pass