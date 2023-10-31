from __future__ import annotations
from threading import Thread
from typing import List
from matplotlib import pyplot as plt
from enum import Enum
from time import time
import protocol as net
import numpy as np
import os


kMessagesToSend = 100
kThisFilePath = os.path.abspath(__file__)

def img_save_dst() -> str:
    return 'doc\\img\\'


class Statistics(Enum):
    kMessageNum = 0,
    kWorkingTime = 1

    @staticmethod
    def to_str(stat: Statistics) -> str:
        if stat == Statistics.kMessageNum:
            return 'MessageNum'
        elif stat == Statistics.kWorkingTime:
            return 'WorkingTime'
        
        return ''


def run_protocol(sender: net.SlidingWindowSender, receiver: net.SlidingWindowReceiver) -> None:
    sender_thread = Thread(target=sender.run)
    receiver_thread = Thread(target=receiver.run)

    sender_thread.start()
    receiver_thread.start()

    sender_thread.join()
    receiver_thread.join()


def calculate_corruption_rate_dependencies(
        protocol_type: net.Protocol,
        window_size: int,
        timeout: float,
        corruption_rates: List[float],
        stat: Statistics,
        show_plot: bool = True) -> None:
    messages_nums = []
    work_times = []

    for corruption_rate in corruption_rates:
        sender, receiver = net.SlidingWindowProtocol.create_connected(protocol_type, window_size, timeout, corruption_rate)
        sender.set_max_messages_num(kMessagesToSend)

        start_time = time()
        run_protocol(sender, receiver)
        work_time = time() - start_time

        print(f'corruption_rate = {corruption_rate}, message_num = {sender.get_sended_messages_num()}, work_time = {work_time}')
        messages_nums.append(sender.get_sended_messages_num())
        work_times.append(work_time)

    plt.plot(corruption_rates, messages_nums if stat == Statistics.kMessageNum else work_times, label=f'window size = {window_size}')
    if show_plot:
        plt.legend()
        plt.show()


def calculate_window_size_dependencies(
        protocol_type: net.Protocol,
        timeout: float,
        corruption_rate: float,
        window_sizes: List[int],
        stat: Statistics,
        show_plot: bool = True) -> None:
    messages_nums = []
    work_times = []

    for window_size in window_sizes:
        sender, receiver = net.SlidingWindowProtocol.create_connected(protocol_type, window_size, timeout, corruption_rate)
        sender.set_max_messages_num(kMessagesToSend)

        start_time = time()
        run_protocol(sender, receiver)
        work_time = time() - start_time

        print(f'window_size = {window_size}, message_num = {sender.get_sended_messages_num()}, work_time = {work_time}')
        messages_nums.append(sender.get_sended_messages_num())
        work_times.append(work_time)

    plt.plot(window_sizes, messages_nums if stat == Statistics.kMessageNum else work_times, label=f'corruption rate = {corruption_rate}')
    if show_plot:
        plt.legend()
        plt.show()


def calculate_timeout_dependencies(
        protocol_type: net.Protocol,
        window_size: int,
        corruption_rate: float,
        timeouts: List[float],
        stat: Statistics,
        show_plot: bool = True) -> None:
    messages_nums = []
    work_times = []

    for timeout in timeouts:
        sender, receiver = net.SlidingWindowProtocol.create_connected(protocol_type, window_size, timeout, corruption_rate)
        sender.set_max_messages_num(kMessagesToSend)

        start_time = time()
        run_protocol(sender, receiver)
        work_time = time() - start_time

        print(f'window_size = {window_size}, message_num = {sender.get_sended_messages_num()}, work_time = {work_time}')
        messages_nums.append(sender.get_sended_messages_num())
        work_times.append(work_time)

    plt.plot(timeouts, messages_nums if stat == Statistics.kMessageNum else work_times, label=net.Protocol.to_str(protocol_type))
    if show_plot:
        plt.legend()
        plt.show()



def calculate_size_rate_dependencies(
        protocol_type: net.Protocol,
        timeout: float,
        window_sizes: List[int],
        corruption_rates: List[float],
        stat: Statistics) -> None:
    
    for window_size in window_sizes:
        calculate_corruption_rate_dependencies(protocol_type, window_size, timeout, corruption_rates, stat, False)

    plt.legend()
    plt.xlabel('corruption rate')
    plt.ylabel('total messages send' if stat == Statistics.kMessageNum else 'working time (in seconds)')
    plt.title(f'{net.Protocol.to_str(protocol_type)}')
    plt.savefig(f'{img_save_dst()}sizeRate{net.Protocol.to_short_str(protocol_type)}{Statistics.to_str(stat)}.png')
    plt.clf()


def calculate_rate_size_dependencies(
        protocol_type: net.Protocol,
        timeout: float,
        corruption_rates: List[float],
        window_sizes: List[int],
        stat: Statistics) -> None:
    
    for corruption_rate in corruption_rates:
        calculate_window_size_dependencies(protocol_type, timeout, corruption_rate, window_sizes, stat, False)

    plt.legend()
    plt.xlabel('window size')
    plt.ylabel('total messages send' if stat == Statistics.kMessageNum else 'working time (in seconds)')
    plt.title(f'{net.Protocol.to_str(protocol_type)}')
    plt.savefig(f'{img_save_dst()}rateSize{net.Protocol.to_short_str(protocol_type)}{Statistics.to_str(stat)}.png')
    plt.clf()


def calculate_protocol_timeout_dependencies(
        window_size: int,
        corruption_rate: float,
        protocol_types: List[net.Protocol],
        timeouts: List[float],
        stat: Statistics) -> None:
    
    for protocol_type in protocol_types:
        calculate_timeout_dependencies(protocol_type, window_size, corruption_rate, timeouts, stat, False)

    plt.legend()
    plt.xlabel('timeout (in seconds)')
    plt.ylabel('total messages send' if stat == Statistics.kMessageNum else 'working time (in seconds)')
    plt.title('')
    plt.savefig(f'{img_save_dst()}timeouts{Statistics.to_str(stat)}.png')
    plt.clf()


def main():
    corruption_rates = np.linspace(0.0, 0.9, 19)
    window_sizes = [int(x) for x in np.linspace(5, 50, 10)]
    timeouts = np.linspace(0.02, 0.5, 30)

    calculate_size_rate_dependencies(net.Protocol.kSrp, 0.5, [10, 25, 50], corruption_rates, Statistics.kMessageNum)
    calculate_rate_size_dependencies(net.Protocol.kSrp, 0.5, [0.1, 0.25, 0.5], window_sizes, Statistics.kMessageNum)

    calculate_size_rate_dependencies(net.Protocol.kGbn, 0.5, [10, 25, 50], corruption_rates, Statistics.kMessageNum)
    calculate_rate_size_dependencies(net.Protocol.kGbn, 0.5, [0.1, 0.25, 0.5], window_sizes, Statistics.kMessageNum)

    calculate_size_rate_dependencies(net.Protocol.kSrp, 0.5, [10, 25, 50], corruption_rates, Statistics.kWorkingTime)
    calculate_rate_size_dependencies(net.Protocol.kSrp, 0.5, [0.1, 0.25, 0.5], window_sizes, Statistics.kWorkingTime)

    calculate_size_rate_dependencies(net.Protocol.kGbn, 0.5, [10, 25, 50], corruption_rates, Statistics.kWorkingTime)
    calculate_rate_size_dependencies(net.Protocol.kGbn, 0.5, [0.1, 0.25, 0.5], window_sizes, Statistics.kWorkingTime)

    calculate_protocol_timeout_dependencies(10, 0.0, [net.Protocol.kGbn, net.Protocol.kSrp], timeouts, Statistics.kMessageNum)
    calculate_protocol_timeout_dependencies(10, 0.0, [net.Protocol.kGbn, net.Protocol.kSrp], timeouts, Statistics.kWorkingTime)

    return


if __name__ == '__main__':
    main()
