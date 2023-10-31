from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Tuple
from numpy import random as rnd
from time import time, sleep


def get_current_time() -> float:
    return time()


class Protocol(Enum):
    kGbn = 0,
    kSrp = 1

    @staticmethod
    def to_str(protocol: Protocol) -> str:
        if protocol == Protocol.kGbn:
            return 'Go-Back-N'
        elif protocol == Protocol.kSrp:
            return 'Selective Repeat'
        
        return ''
    
    @staticmethod
    def to_short_str(protocol: Protocol) -> str:
        if protocol == Protocol.kGbn:
            return 'GBN'
        elif protocol == Protocol.kSrp:
            return 'SRP'
        
        return ''

class MsgCode(Enum):
    kSuccess = 0,
    kFail = 1


class Message:
    def __init__(self, id: int, code: MsgCode, data) -> None:
        self.id = id
        self.code = code
        self.data = data


class SlidingWindowProtocol(ABC):
    @staticmethod
    def connect(sender: SlidingWindowSender, receiver: SlidingWindowReceiver) -> None:
        sender.connect(receiver)
        receiver.connect(sender)

    def create_connected(
            type: Protocol,
            window_size: int,
            timeout: float,
            corruption_rate: float) -> Tuple[SlidingWindowSender, SlidingWindowReceiver]:
        sender: SlidingWindowSender = None
        receiver: SlidingWindowReceiver = None

        if type == Protocol.kGbn:
            sender = GoBackNSender(window_size, timeout)
            receiver = GoBackNReceiver(corruption_rate)
        elif type == Protocol.kSrp:
            sender = SelectiveRepeatSender(window_size, timeout)
            receiver = SelectiveReapetReceiver(corruption_rate)
        else:
            assert False
        
        SlidingWindowProtocol.connect(sender, receiver)
        return sender, receiver

    def __init__(self) -> None:
        super().__init__()
        self.message_queue: List[Message] = []

    def get_message(self, message: Message) -> None:
        self.message_queue.append(message)

    @abstractmethod
    def run(self) -> None:
        pass


class SlidingWindowSender(SlidingWindowProtocol):
    def __init__(self, window_size: int, timeout_time: float) -> None:
        super().__init__()
        self.window_size = window_size
        self.receiver: SlidingWindowReceiver = None
        self.timeout_time = timeout_time
        self.max_messages_num = 100
        self.finished = False
        self.message_counter = 0

    def connect(self, receiver: SlidingWindowReceiver) -> None:
        assert receiver is not None
        self.receiver = receiver

    def set_max_messages_num(self, messages_num: int) -> None:
        assert messages_num > 0
        self.max_messages_num = messages_num

    def send_message_to_receiver(self, message: Message) -> None:
        self.message_counter += 1
        self.receiver.get_message(message)

    def is_finished(self) -> bool:
        return self.finished
    
    def get_sended_messages_num(self) -> int:
        return self.message_counter


class SlidingWindowReceiver(SlidingWindowProtocol):
    def __init__(self, corruption_rate: float) -> None:
        super().__init__()
        self.sender: SlidingWindowSender = None
        self.corruption_rate = max(min(corruption_rate, 1.0), 0.0)
        self.rnd = rnd.default_rng()

    def connect(self, sender: SlidingWindowSender) -> None:
        assert sender is not None
        self.sender = sender

    def prepare_answer(self, message_id: int) -> Message:
        corruption_rnd = self.rnd.uniform(0.0, 1.0)

        if corruption_rnd < self.corruption_rate:
            # corrupted
            return Message(message_id, MsgCode.kFail, None)

        # success
        return Message(message_id, MsgCode.kSuccess, None)
            

class GoBackNSender(SlidingWindowSender):
    def __init__(self, window_size: int, timeout_time: float) -> None:
        super().__init__(window_size, timeout_time)
        self.send_base = 0
        self.send_base_time = get_current_time()
        self.send_next = 0
        self.message_id = 0
        self.waiting_message_id = 0
        self.dummy_data = 'go back n sender data'

    def run(self) -> None:
        #print('sender start work')

        while self.send_base < self.max_messages_num:
            handle_error = False

            if (self.send_next - self.send_base < self.window_size) and (self.send_next < self.max_messages_num):
                send_message = Message(self.message_id, MsgCode.kSuccess, self.dummy_data)
                self.send_message_to_receiver(send_message)
        
                self.send_base_time = get_current_time()
                self.send_next += 1
                self.message_id += 1
                # print(f'sender send id {send_message.id}')
            
            if self.remove_outdated_messages() > 0:
                #print(f'message info, id = {self.message_queue[0].id}, waiting = {self.waiting_message_id}')

                if self.message_queue[0].id == self.waiting_message_id and self.message_queue[0].code == MsgCode.kSuccess:
                    self.send_base += 1
                    self.waiting_message_id += 1
                    del self.message_queue[0]
                    #print(f'sender move window, new base {self.send_base}')
                else:
                    handle_error = True

            if handle_error or self.time_since_base_send() > self.timeout_time:
                #print(f'moved back to {self.send_next - self.send_base}')
                self.send_next = self.send_base
                self.waiting_message_id = self.message_id

        self.finished = True
        #print(f'GBN total sended: {self.message_counter}')

    def remove_outdated_messages(self) -> int:
        timouted_messages = 0
        queue_size = len(self.message_queue)

        if queue_size > 0:
            while timouted_messages < queue_size and self.message_queue[timouted_messages].id < self.waiting_message_id:
                timouted_messages += 1

            if timouted_messages > 0:
                #print(f'outdated removed: {timouted_messages}')
                del self.message_queue[0:timouted_messages]
                #print(f'head = {self.message_queue[0].id if len(self.message_queue) > 0 else -1}, wating = {self.waiting_message_id}')

        return queue_size - timouted_messages

    def time_since_base_send(self) -> float:
        return get_current_time() - self.send_base_time
    

class GoBackNReceiver(SlidingWindowReceiver):
    def __init__(self, corruption_rate: float) -> None:
        super().__init__(corruption_rate)
        self.last_received = 0

    def run(self) -> None:
        #print('receiver start work')

        while not self.sender.is_finished():
            if len(self.message_queue) > 0:
                current_message = self.message_queue[0]

                send_message = self.prepare_answer(current_message.id)
                self.sender.get_message(send_message)

                del self.message_queue[0]
                # print(f'receiver receive={current_message.id}')


class SelectiveRepeatSender(SlidingWindowSender):
    class MessageNode:
        def __init__(self, send_time: float, message: Message) -> None:
            self.send_time = send_time
            self.message = message

    def __init__(self, window_size: int, timeout_time: float) -> None:
        super().__init__(window_size, timeout_time)
        self.last_approved = 0
        self.send_next = 0
        self.message_nodes: Dict[int, SelectiveRepeatSender.MessageNode] = {}
        self.dummy_data = 'selective repeat dummy data'

    def run(self) -> None:
        while self.finished == False:
            queue_size = len(self.message_queue)
            while queue_size > 0:
                message = self.message_queue[0]
                self.last_approved = max(self.last_approved, message.data)

                if self.last_approved >= self.max_messages_num - 1:
                    self.finished = True
                    break

                if message.id in self.message_nodes:
                    if message.code == MsgCode.kSuccess:
                        del self.message_nodes[message.id]
                    else:
                        self.send_message_to_receiver(self.message_nodes[message.id].message)
                        self.message_nodes[message.id].send_time = get_current_time()

                del self.message_queue[0]
                queue_size -= 1

            if len(self.message_nodes) < self.window_size and self.send_next < self.max_messages_num:
                send_message = Message(self.send_next, MsgCode.kSuccess, self.dummy_data)

                self.send_message_to_receiver(send_message)
                self.message_nodes[self.send_next] =  SelectiveRepeatSender.MessageNode(get_current_time(), send_message)

                self.send_next += 1

            for message_node_idx in self.message_nodes:
                message_node = self.message_nodes[message_node_idx]

                if self.is_outdated(message_node.send_time):
                    self.send_message_to_receiver(message_node.message)
                    self.message_nodes[message_node.message.id].send_time = get_current_time()
                    #print(f'repeat outdated {message_node.message.id}')

        #print(f'SRP total sended: {self.message_counter}')

    def is_outdated(self, send_time: float) -> bool:
        #print(f'current = {get_current_time()}, send = {send_time}')
        return get_current_time() - send_time > self.timeout_time


class SelectiveReapetReceiver(SlidingWindowReceiver):
    def __init__(self, corruption_rate: float) -> None:
        super().__init__(corruption_rate)
        self.last_received = -1
        self.received: List[int] = []

    def run(self) -> None:
        info_send_time = get_current_time()

        while not self.sender.is_finished():
            self.resolve_last_received()

            if len(self.message_queue) > 0:
                current_message = self.message_queue[0]

                send_message = self.prepare_answer(current_message.id)
                send_message.data = self.last_received
                self.sender.get_message(send_message)

                if send_message.code == MsgCode.kSuccess:
                    self.received.append(send_message.id)

                del self.message_queue[0]

            elif get_current_time() - info_send_time > 0.01: # exta safe
                info_send_time = get_current_time()
                self.sender.get_message(Message(-1, MsgCode.kSuccess, self.last_received))

    def resolve_last_received(self) -> None:
        i = 0
        while i < len(self.received):
            if self.received[i] <= self.last_received:
                del self.received[i]
                i -= 1

            elif self.received[i] == self.last_received + 1:
                self.last_received += 1

            i += 1
    