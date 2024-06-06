class MavlinkConnection:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.connected = True
        print("Connection to flight controller established.")

    def is_connected(self):
        return self.connected

    def send_data(self, data):
        if self.connected:
            print(f"Sending data to flight controller: {data}")
            return True
        else:
            print("Failed to send data: No connection to flight controller.")
            return False