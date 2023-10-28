from threading import Thread
import protocol as net



def main():
    #sender = net.GoBackNSender(20, 0.5)
    #receiver = net.GoBackNReceiver(0.5)

    sender = net.SelectiveRepeatSender(20, 0.5)
    receiver = net.SelectiveReapetReceiver(0.3)

    sender.set_max_messages_num(100)

    net.SlidingWindowProtocol.connect(sender, receiver)

    sender_thread = Thread(target=sender.run)
    receiver_thread = Thread(target=receiver.run)

    sender_thread.start()
    receiver_thread.start()

    sender_thread.join()
    receiver_thread.join()

    return


if __name__ == '__main__':
    main()
