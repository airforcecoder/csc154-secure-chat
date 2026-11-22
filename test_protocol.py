
# test_protocol.py
# CSC 154
# Tests the JSON message protocol

import socket
import unittest

from protocol import send_json, receive_json


class TestProtocol(unittest.TestCase):

    def setUp(self):
        # Create two connected sockets for testing
        self.sender, self.receiver = socket.socketpair()

        # Make a reader that can read one line at a time
        self.reader = self.receiver.makefile("rb")

    def tearDown(self):
        # Close everything after each test
        self.reader.close()
        self.sender.close()
        self.receiver.close()

    def test_normal_message(self):
        # Send a regular JSON message
        message = {"type": "register", "username": "Alice"}

        send_json(self.sender, message)
        result = receive_json(self.reader)

        self.assertEqual(result, message)

    def test_multiple_messages(self):
        # TCP can deliver multiple messages together
        send_json(self.sender, {"type": "users_request"})
        send_json(self.sender, {"type": "quit"})

        first = receive_json(self.reader)
        second = receive_json(self.reader)

        self.assertEqual(first["type"], "users_request")
        self.assertEqual(second["type"], "quit")

    def test_message_in_parts(self):
        # TCP can also deliver a message in separate pieces
        self.sender.sendall(b'{"type": "reg')
        self.sender.sendall(b'ister", "username": "Bob"}\n')

        result = receive_json(self.reader)

        self.assertEqual(result["username"], "Bob")

    def test_invalid_json(self):
        # The receiver should reject invalid JSON
        self.sender.sendall(b"not valid json\n")

        with self.assertRaises(ValueError):
            receive_json(self.reader)

    def test_missing_type(self):
        # Every message needs a type field
        with self.assertRaises(ValueError):
            send_json(self.sender, {"username": "Alice"})

    def test_disconnection(self):
        # Closing the sender should return None
        self.sender.close()

        result = receive_json(self.reader)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
