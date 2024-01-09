from threading import Thread
from generals import LoyalGeneral, TraitorGeneral


class GeneralProblemTask:
    def __init__(self, loyal: int, traitor: int) -> None:
        self.loyal_num = loyal
        self.traitor_num  = traitor
        self.generals = \
            [LoyalGeneral(i, self.traitor_num) for i in range(self.loyal_num)] + \
            [TraitorGeneral(self.loyal_num + i, self.traitor_num) for i in range(self.traitor_num)]
        
    def start(self) -> None:
        general_tasks = [Thread(target=general.start, args=(self.generals, )) for general in self.generals]

        for general_task in general_tasks:
            general_task.start()

        for general_task in general_tasks:
            general_task.join()


def main():
    k_loyals = 2
    k_traitors = 2
    
    general_task = GeneralProblemTask(k_loyals, k_traitors)
    general_task.start()


if __name__ == '__main__':
    main()
