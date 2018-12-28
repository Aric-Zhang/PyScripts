from operator import attrgetter
import random
import unittest


def choice_by_weight(list_to_choose, *, key=attrgetter('weight')):
    """
    根据权重返回容器中的随机对象
    :param list_to_choose: 容器
    :param key: 计算权重的函数
    :return:
    """
    weight_list = [key(x) for x in list_to_choose]
    total_weight = sum(weight_list)
    random_seed = random.uniform(0, total_weight)
    current_sum = 0
    for element in list_to_choose:
        next_sum = current_sum + element.weight
        if current_sum <= random_seed < next_sum:
            return element
        current_sum = next_sum
    return list_to_choose[-1]


class Singleton(object):
    """
    单例模式的装饰器
    :param cls:
    :return:
    """
    _instance = {}

    def __init__(self, cls):
        self.cls = cls

    def __call__(self, *args, **kwargs):
        if self.cls not in Singleton._instance:
            Singleton._instance[self.cls] = self.cls(*args, **kwargs)
        return Singleton._instance[self.cls]


class SingletonCls(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                SingletonCls, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_time_via_sec(seconds):
    """
    格式化打印时间
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


print('bank_test')

service_time_list = [5 * 60, 10 * 60, 15 * 60, 20 * 60]  # 所有的服务类型的时长

TIME_GAP = 30  # 三十秒的服务时间间隔
MAX_TIME = 0xffffffff
SERVICE_WINDOWS_COUNT = 9  # 九个窗口
CUSTOMER_WAITING_COUNT_EXPECTATION = 30  # 正在等待的客户数期望值，同时为初始状态
TOTAL_TIME_LENGTH = 8 * 60 * 60  # 八小时服务时长
AVERAGE_SERVICE_SPEED = (sum(service_time_list) / len(service_time_list) +
                         TIME_GAP) / SERVICE_WINDOWS_COUNT  # 银行平均服务完成一个客户所需的时间


class ProcessObject:
    """
    随时间推移而变化的所有对象父类
    应包含有计时成员，期望在时间结束后触发事件
    """

    def __init__(self, time_left=None):
        # 如果time_left为None表明没有下次callback的倒计时
        if not isinstance(time_left, int) and time_left is not None:
            raise TypeError("time_left not a int or none type")
        self.timeLeft = time_left

        MainLoop().register_object(self)  # 将自身注册进主消息循环

    def update(self, time):
        pass

    def callback(self):
        pass


class Customer(ProcessObject):

    # 客户的类

    def __init__(self, serial, service_time):
        super(Customer, self).__init__()
        self.serial = serial  # the serial number of this customer
        self.serviceTime = service_time  # the service time length
        self.waitingTime = 0

    def update(self, time):
        self.waitingTime += time


class CustomerQueue(list):
    """
    客户队列
    """

    def __init__(self, *, name='Default', priority=0, weight=1.0):
        super(CustomerQueue, self).__init__()
        self.name = name
        self.priority = priority
        self.currentCustomerNumber = 0
        self.weight = weight
        self.served = []
        if weight <= 0:
            raise ValueError('weight less than 1, must be a normal')

    def add_random_customer(self):
        """
        添加随机时长的客户到队列中
        :return: Customer
        """
        self.currentCustomerNumber += 1
        new_customer = Customer(
            self.name + "%04d" % self.currentCustomerNumber, random.choice(service_time_list))
        self.append(new_customer)
        print('%s:push +%s' %
              (get_time_via_sec(MainLoop().time_processed()), new_customer.serial))

    def pop_customer(self):
        """
        推出最前端的客户，并将其从MainLoop中解除注册
        :return:
        """
        customer = self.pop(0)
        MainLoop().unregister_object(customer)
        print('%s:pop +%s' %
              (get_time_via_sec(MainLoop().time_processed()), customer.serial))
        self.served.append(customer)
        return customer

    @property
    def average_waiting_time(self):
        """
        平均等待时间
        :return:
        """
        if len(self.served) == 0:
            return MAX_TIME
        return sum([x.waitingTime for x in self.served]) / len(self.served)


class CustomerPool(list, ProcessObject, metaclass=SingletonCls):
    """
    所有客户队列的对象池。
    list中元素为CustomerQueue队列
    """

    def __init__(self):
        super(CustomerPool, self).__init__()
        super(list, self).__init__(self.__next_customer_time_countdown)
        self.append(CustomerQueue(name='对公客户', priority=3, weight=2))
        self.append(CustomerQueue(name='VIP客户', priority=2, weight=3))
        self.append(CustomerQueue(name='私人客户', priority=1, weight=4))
        self.sort(key=attrgetter('priority'),
                  reverse=True)            # 按优先级降序排序

        self.timeLeft = 0

    def init_pre_waiting_clients(self):
        """
        生成初始的等待客户
        :return:
        """
        for i in range(CUSTOMER_WAITING_COUNT_EXPECTATION):
            self.get_random_customer()

    def get_random_customer(self):
        """
        生成一个随机的客户，通过调用其所有子顾客队列的生成方法的方式，并返回这个客户
        :return:
        """
        choice_by_weight(self).add_random_customer()
        Bank().new_customer_event()

    def update(self, time):
        """
        在更新时每次达到时限时生成新顾客
        :param time:
        :return:
        """
        self.timeLeft -= time

    def callback(self):
        self.get_random_customer()
        self.timeLeft = self.__next_customer_time_countdown
        Bank().init_windows_allocation()
        pass

    def __repr__(self):
        return "Customer Queues"

    @property
    def top_priority_queue_available(self):
        """
        返回优先级最高的不为空的队列。若不存在则返回空。
        :return:
        """
        for queue in self:
            if len(queue) > 0:
                return queue
        return None

    @property
    def __next_customer_time_countdown(self):
        """
        得到下一个客户到来的时间
        :return:
        """
        return int(AVERAGE_SERVICE_SPEED)


class MainLoop(metaclass=SingletonCls):
    """
    最外层消息循环
    """

    def __init__(self):
        self.object_list = []
        self.enabled = True
        self.runner = None

    def register_object(self, obj):
        """
        将对象注册进事件列表
        :param obj:被注册对象
        :return: obj是否已经存在，如已经存在则注册失败，返回False，否则返回True
        """
        if not isinstance(obj, ProcessObject):
            raise TypeError('not a ProcessObject registering')
        if obj not in self.object_list:
            self.object_list.append(obj)
            return True
        return False

    def unregister_object(self, obj):
        """
        将已注册的对象取消注册
        :param obj:已注册对象
        :return:
        """
        self.object_list.remove(obj)

    @property
    def most_recent_obj(self):
        most_recent_obj = None
        for obj in self.object_list:
            if obj.timeLeft is not None and most_recent_obj is None:
                most_recent_obj = obj
            elif obj.timeLeft is not None and most_recent_obj is not None:
                if 0 <= obj.timeLeft < most_recent_obj.timeLeft:
                    most_recent_obj = obj
            else:
                continue
        return most_recent_obj

    def run(self):
        self.runner = Runner()
        print(self.runner)
        while self.enabled:
            most_recent_obj = self.most_recent_obj
            time_leap = most_recent_obj.timeLeft
            for obj in self.object_list:
                obj.update(time_leap)
                # if obj.timeLeft == 0:
            most_recent_obj.callback()

    def time_processed(self):
        """
        已经经过的时间
        :return:
        """
        if self.runner is None:
            return 0
        return TOTAL_TIME_LENGTH - self.runner.timeLeft


class Runner(ProcessObject):
    """
    计时器
    """

    def __init__(self):
        super(Runner, self).__init__()
        self.timeLeft = TOTAL_TIME_LENGTH

    def update(self, time):
        self.timeLeft -= time

    def callback(self):
        MainLoop().enabled = False
        self.__summary()

    def __str__(self):
        summary_str = "%s:\n-----SUMMARY-----\n" % get_time_via_sec(
            MainLoop().time_processed())
        for queue in CustomerPool():
            summary_str += "%s:%ds " % (queue.name,
                                        Bank().expected_average_waiting_time(queue))
        summary_str += "\n"
        for queue in CustomerPool():
            summary_str += "%s:%ds " % (queue.name, queue.average_waiting_time)
        summary_str += "\n" + str([x.current_queue.name for x in Bank()])
        return summary_str

    def __summary(self):
        print(self)


class ServiceWindow(ProcessObject):
    def __init__(self, serial):
        super(ServiceWindow, self).__init__()
        self.serial = serial
        self.timeLeft = 0
        self.current_queue = None

    def update(self, time):
        self.timeLeft -= time

    def callback(self):
        """
        窗口服务下一个客户
        若当前列为空则获取一个新的列
        若新的列不存在则timeLeft为负值
        :return:
        """
        try:
            self.serve_next_customer()
        except IndexError:
            self.current_queue = CustomerPool().top_priority_queue_available
            if self.current_queue is None:
                self.timeLeft = -1
            else:
                self.serve_next_customer()
        except AttributeError:
            self.current_queue = CustomerPool().top_priority_queue_available
            if self.current_queue is None:
                self.timeLeft = -1
            else:
                self.serve_next_customer()

    def serve_next_customer(self):
        self.timeLeft = self.current_queue.pop_customer().serviceTime + TIME_GAP


class Bank(list, metaclass=SingletonCls):
    """
    银行类，包含所有的服务窗口
    """

    def __init__(self, num_of_service_windows=SERVICE_WINDOWS_COUNT):
        super(Bank, self).__init__()
        self.numOfServiceWindows = num_of_service_windows
        for window_serial in range(num_of_service_windows):
            self.append(ServiceWindow(window_serial))

    def init_windows_allocation(self):
        pool = CustomerPool()
        for window in self:
            for queue in pool:
                if self.window_num_for_queue(queue) < queue.weight:
                    window.current_queue = queue
                    break

    def window_num_for_queue(self, queue):
        """
        返回银行为某一队列分配的窗口数
        :param queue:
        :return:
        """
        if not isinstance(queue, CustomerQueue):
            raise TypeError('not a CustomerQueue being checking number')
        return len([x for x in self if x.current_queue == queue])

    def new_customer_event(self):
        for window in self:
            if window.timeLeft < 0:
                window.callback()
                return

    def expected_average_waiting_time(self, queue):
        """
        :param queue: 客户队列
        :return:平均每个客户的剩余等待时间
        """
        customer_service_time_list = [x.serviceTime for x in queue]
        counter_time_list = [
            x.timeLeft for x in self if x.current_queue == queue]
        if len(counter_time_list) == 0:
            return MAX_TIME
        if len(customer_service_time_list) == 0:
            return 0
        total_waiting_time = 0
        waiting_time = 0
        for customer_waiting_time in customer_service_time_list:
            min_waiting_time = min(counter_time_list)
            counter_time_list = [
                x - min_waiting_time for x in counter_time_list]
            for i in range(len(counter_time_list)):
                if counter_time_list[i] <= 0:
                    counter_time_list[i] = customer_waiting_time
                    break
            waiting_time += min_waiting_time
            total_waiting_time += waiting_time
        return total_waiting_time / len(customer_service_time_list)


class Test(unittest.TestCase):

    def test_main_loop(self):
        CustomerPool().init_pre_waiting_clients()
        Bank().init_windows_allocation()
        for queue in CustomerPool():
            print(Bank().expected_average_waiting_time(queue))
        MainLoop().run()

if __name__ == '__main__':
    unittest.main()
