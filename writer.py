import datetime as dt
from threading import Thread, Semaphore

class Writer:
    def __init__(self, file_name, separator = ',') -> None:
        self.semaphore = Semaphore()
        self.xs = list()
        self.ys = list()
        self.separator = separator
        self.file = open(file_name, "w")
        self.file.write('Time,Fx,Fy,Fz\n')
        self.file.close()
        self.file = open(file_name, "a")

    def update(self, xs, ys) -> None:
        # Add x and y to lists
        self.xs = xs
        self.ys = ys
        self.semaphore.release()

    def run_thread(self) -> None:
        while True:
            try:
                self.semaphore.acquire()
                for x, ys in zip(self.xs, self.ys):
                    line = str(x) + self.separator + self.separator.join(map(str, ys)) + '\n'
                    self.file.write(line)
                    self.file.flush()
            except KeyboardInterrupt as e:
                print("Writer interrupted by user.")
                self.file.close()
                break
            except Exception as e:
                self.file.close()
                exit(1)

    def run(self) -> None:
        self.thread = Thread(None, self.run_thread, 'WriterThread', [])
        self.thread.start()

    def wait(self) -> None:
        self.thread.join()

if __name__ == '__main__':
    writer = Writer('test.csv')
    writer.run()
    writer.wait()