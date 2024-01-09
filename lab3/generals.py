from __future__ import annotations
from typing import List, Dict
from abc import ABC, abstractmethod
from threading import Lock


class General(ABC):
    _global_mutex = Lock()

    def __init__(self, id: int, traitor_num: int) -> None:
        self.id = id
        self.vectors: Dict[General, Dict[General, ]] = {}
        self.other_generals = []
        self.traitor_num = traitor_num

    @abstractmethod
    def send_value(self, other: General) -> None:
        pass

    @abstractmethod
    def send_vector(self, other: General) -> None:
        pass

    def get_value(self, sender: General, val) -> None:
        if self not in self.vectors:
            self.vectors[self] = {}

        assert sender not in self.vectors[self]
        self.vectors[self][sender] = val

    def get_vector(self, sender: General, vector) -> None:
        self.vectors[sender] = vector

    def connect(self, all_generals: List[General]) -> None:
        self.other_generals = [general for general in all_generals if general != self]
        # print(f'num = {len(self.other_generals)} | {self.other_generals}')

    def start(self, all_generals: List[General]) -> None:
        self.connect(all_generals)

        for general in self.other_generals:
            self.send_value(general)

        while self not in self.vectors:
            pass

        while len(self.vectors[self]) < len(self.other_generals):
            pass

        # with General._global_mutex:
        #     print(f'general {self.id} collect first vector')
        #     for val in self.vectors[self].values():
        #         print(val, end=', ')  
        #     print()

        for general in self.other_generals:
            self.send_vector(general)

        while len(self.vectors) < len(all_generals):
            pass

        # with General._global_mutex:
        #     if self.id == 1 or self.id == 7:
        #         print(f'general id = {self.id}')
        #         for k in self.vectors:
        #             print(f'recieved vector from general {k.id}: ', end=': ')

        #             for v in self.vectors[k].values():
        #                 print(v, end=', ')

        #             print()

        result = {}

        for cur_general in all_generals:
            values = []
            unique_values = set()
            # print(f'recieved for general {cur_general.id}')
            for general in all_generals:
                if cur_general == general:
                    continue

                values.append(self.vectors[general][cur_general])
                unique_values.add(self.vectors[general][cur_general])

            max_unique_val_couter = 0
            determined_val = -1
            for unique_val in unique_values:
                unique_val_couter = 0

                for val in values:
                    unique_val_couter += (unique_val == val)

                if unique_val_couter > max_unique_val_couter:
                    determined_val = unique_val
                    max_unique_val_couter = unique_val_couter

            if max_unique_val_couter < (len(self.other_generals) - self.traitor_num):
                determined_val = None

            result[cur_general] = determined_val

            # print(values)
            # print(f'got for general {cur_general.id} = {determined_val}')

        with General._global_mutex:
            print(f'resulted vector for general {self.id}')
            vec = [v for v in result.values()]
            print(vec)


class LoyalGeneral(General):
    def __init__(self, id: int, traitor_num: int) -> None:
        super().__init__(id, traitor_num)

    def send_value(self, other: General) -> None:
        other.get_value(self, self.id)
    
    def send_vector(self, other: General) -> None:
        other.get_vector(self, self.vectors[self])


class TraitorGeneral(General):
    def __init__(self, id: int, traitor_num: int) -> None:
        super().__init__(id, traitor_num)

    def send_value(self, other: General) -> None:
        other.get_value(self, f'traitor_{other.id}')

    def send_vector(self, other: General) -> None:
        traitor_vector = {}

        for k, v in zip(self.vectors[self].keys(), self.vectors[self].values()):
            traitor_vector[k] = f'traitor_{other.id}_{v}'

        other.get_vector(self, traitor_vector)
    