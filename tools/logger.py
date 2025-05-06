class Logger():
    def __init__(self, edition):
        self.edition = edition
        self.path = f"./logs/execution_{edition}.log"

    def write(self, message_arr):
        with open(self.path, "a") as f:
            for message in message_arr:
                f.write(f"{message}\n")
