import random
from operator import attrgetter

COUNTER_NUM = 9
CALL_WAITING_TIME = 30
MAX_TIME = 0xffffffff

pre_waiting_time = 15 * 60  # 取号在上班之前开始的时间
pre_client_num_expectation = 30  # 等待人数期望值

# 队列池
client_pools = []
# 假设均匀分布
service_time_length = (5 * 60, 10 * 60, 15 * 60, 20 * 60)
service_speed = 9 / (sum(service_time_length) // len(service_time_length) + 30)


def get_time_via_sec(seconds):
    '''
    格式化打印时间
    '''
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return ("%02d:%02d:%02d" % (h, m, s))


class process_motor(list):

    def __init__(self, total_time_length):
        self.total_time_length = total_time_length
        self.time_left = total_time_length
        self.start_time = 7 * 60 * 60 + 45 * 60
        self.current_time = self.start_time
        self.check_points = []

    def process_one_shot(self):
        # print(len(self))
        for process in self:
            if process.enabled:
                process.update()
        self.current_time += 1

    def process(self):
        for i in range(self.total_time_length):
            if self.time_left > 20 * 60:
                if generate_client_by_chance():
                    counters.alloc_counters(client_pools)
            for process in self:
                if process.enabled:
                    process.update()
            self.time_left -= 1
            self.current_time += 1
            self.supervise()

    def get_time_via_sec(self):
        '''
        格式化时间
        '''
        seconds = self.current_time
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return ("%02d:%02d:%02d" % (h, m, s))

    def set_supervise_check_point(self, *time):
        self.check_points = list(sorted(time))

    def supervise(self):
        try:
            if self.current_time == self.start_time + self.check_points[0]:
                self.check_points.pop(0)
                print(summary())
                input('press enter to continue...')
        except IndexError:
            pass


motor = process_motor(8 * 60 * 60)


class process:
    '''
    随时间变化的类
    '''

    def __init__(self, enabled=True):
        self.enabled = enabled
        motor.append(self)

    def update(self):
        pass

    def destroy(self):
        motor.remove(self)


class client_pool(list):
    '''
    一个队列
    '''

    def __init__(self, *, name='default_pool', priority=0):
        self.pool_name = name
        self.priority = priority
        self.current_number = 0
        self.past_clients = []
        client_pools.append(self)

    def get_new_service_number(self):
        self.current_number += 1
        serial = "%04d" % self.current_number
        return self.pool_name + serial

    def current_pool_total_waiting_time(self):
        time = [x.waiting_time for x in self]
        return sum(time)

    @property
    def pool_priority(self):
        return self.priority

    def __str__(self):
        result_str = self.pool_name + ":\n"
        for c in self:
            result_str += (str(c) + "\n")
        result_str += "clients serviced:%d\n" % len(self.past_clients)
        result_str += "average waiting time:%fs\n" % self.get_average_waiting_time()
        return result_str

    def get_average_waiting_time(self):
        '''
        得到已经服务的客户的平均等待时长
        '''
        total_waiting_time = [
            x.waiting_time for x in self.past_clients] + [x.waiting_time for x in self]
        return sum(total_waiting_time) / len(total_waiting_time)


corporate_pool = client_pool(name="C", priority=2)  # corporate account
vip_pool = client_pool(name="V", priority=1)        # vip account
private_pool = client_pool(name="P")       # personal account


class client(process):
    '''
    客户
    '''

    def __init__(self, pool, service_time):
        super(client, self).__init__()
        self.waiting_time = 0
        self.service_time = service_time
        if isinstance(pool, client_pool) != True:
            raise TypeError("not a clinet_pool")
        self.pool = pool
        self.serial = pool.get_new_service_number()
        print(motor.get_time_via_sec() + " " +
              "%s comes in queue" % self.serial)
        pool.append(self)

    def __str__(self):
        return self.serial + " " + "%ds" % self.service_time

    def update(self):
        self.waiting_time += 1

    def destroy(self):
        super(client, self).destroy()
        self.pool.past_clients.append(self)


def generate_pre_waiting_client():
    chance_per_sec = pre_client_num_expectation / pre_waiting_time
    for i in range(pre_waiting_time):
        seed = random.random()
        if seed <= chance_per_sec:
            client(random.choice(client_pools),
                   random.choice(service_time_length))
        motor.process_one_shot()


def generate_client_by_chance():
    chance_per_sec = service_speed
    seed = random.random()
    if seed <= chance_per_sec:
        client(random.choice(client_pools), random.choice(service_time_length))
        return True
    return False


class counter(process):
    '''
    Which service clients
    '''

    def __init__(self, id_number, *, enabled=True):
        super(counter, self).__init__(enabled=enabled)
        self.id = id_number
        self.current_client = None
        self.time_left = 0

    def service_next_client(self, new_client):
        if isinstance(new_client, client) != True:
            raise TypeError('not a client')
        self.current_client = new_client
        self.time_left = self.current_client.service_time + 30
        new_client.destroy()
        print(motor.get_time_via_sec() + " " + '%s is on service at %s' %
              (str(new_client), self.id))

    def update(self):
        self.time_left -= 1
        if self.time_left <= 0:
            try:
                self.service_next_client(self.current_pool.pop(0))
            except IndexError:
                if self.time_left == 0:
                    current_index = client_pools.index(self.current_pool)
                    while True:
                        try:
                            current_index -= 1
                            self.set_current_pool(
                                client_pools[current_index])
                            try:
                                self.service_next_client(
                                    self.current_pool.pop(0))
                                break
                            except IndexError:
                                continue
                        except IndexError:
                            print('counter %s no client to service' % self.id)

    def set_current_pool(self, pool):
        if isinstance(pool, client_pool) != True:
            raise TypeError('not a pool')
        self.current_pool = pool


class bank(list):
    def __init__(self):
        for i in range(COUNTER_NUM):
            self.append(counter(str(i + 1), enabled=False))

    def get_next_service_time(self, *, pool=None):
        '''
        返回最近的下一个柜台服务完成的时间
        '''
        if pool == None:
            each_time_left = [x.time_left for x in self]
        else:
            each_time_left = [
                x.time_left for x in self and x.current_pool == pool]

        return min(each_time_left)

    def check_pool_on_service_state(self, pool):
        '''
        检查是否存在柜台为该队列服务
        '''
        if isinstance(pool, client_pool) != True:
            raise TypeError('not a client_pool')
        for c in self:
            try:
                if c.current_client.pool == pool:
                    return True
            except AttributeError:
                continue
        return False

    def set_business(self, state):
        '''
        设置银行的营业状态
        '''
        if isinstance(state, bool) != True:
            raise TypeError('state not a bool')
        for c in self:
            c.enabled = state

    def alloc_counters(self, pools):
        '''
        分配柜台给不同的客户队列
        '''
        num_of_pools = len(client_pools)
        try:
            getattr(self, 'allocated')
            while True:
                for i in range(num_of_pools - 1):
                    if self.__expected_average_waiting_time(pools[i]) > self.__expected_average_waiting_time(pools[i + 1]):
                        try:
                            for j in range(1, len(pools)):
                                if len(pools[(i + j) % num_of_pools]) > 0 and self.__num_of_counter_service_pool(pools[(i + j) % num_of_pools]) <= 1:
                                    continue
                                self.__realloc_pool(
                                    pools[(i + j) % num_of_pools], pools[i])
                                break
                        except IndexError:
                            print('allocation failed:no avaliable counter')
                            raise
                        continue
                break
        except AttributeError:
            print('init bank counter allocation...')
            self.allocated = True
            counter_index = 0
            for pool in client_pools:
                for counter_index in range(counter_index, counter_index + COUNTER_NUM // num_of_pools):
                    self[counter_index].set_current_pool(pool)
                    counter_index += 1
            self.alloc_counters(client_pools)

    def __num_of_counter_service_pool(self, pool):
        '''
        返回当前为pool服务的柜台数量
        '''
        counter_list = [x for x in self if x.current_pool == pool]
        return len(counter_list)

    def __realloc_pool(self, original_pool, new_pool):
        for counter in self:
            if counter.current_pool == original_pool:
                counter.current_pool = new_pool
                break

    def __expected_average_waiting_time(self, pool):
        '''
        根据当前状况获得期望的等待时间
        '''
        try:
            getattr(self, 'allocated')
        except AttributeError:
            print('counter not allocated')
            raise

        #print([x.current_pool.pool_name for x in self])

        if len(pool) == 0:
            return 0

        counters_time_left = [
            x.time_left for x in self if x.current_pool == pool]
        # 获取柜台剩余服务时间列表
        clients_service_time = [x.service_time for x in pool]
        clients_waiting_time = [0 for x in pool]  # 客户已经等待的时间
        #start_time = 0
        total_waiting_time = 0
        for client in pool:
            try:
                min_waiting_time = min(counters_time_left)
            except ValueError:
                if len(pool) > 0:
                    return MAX_TIME
                else:
                    raise
            '''
            for time in counters_time_left:
                time -= min_waiting_time
            '''
            counters_time_left = [
                x - min_waiting_time for x in counters_time_left]
            '''
            for time in clients_waiting_time:
                time += min_waiting_time
            '''
            clients_waiting_time = [
                x + min_waiting_time for x in clients_waiting_time]
            for i in range(len(counters_time_left)):
                if counters_time_left[i] <= 0:
                    # print('pop')
                    counters_time_left[i] += clients_service_time.pop(0) + 30
                    break
            total_waiting_time += clients_waiting_time.pop(0)
        #print(pool.pool_name + str(total_waiting_time))
        return total_waiting_time / len(pool)


def summary():
    result_str = "-----------check summary-----------\n"
    for pool in client_pools:
        result_str += str(pool)

    total_clients_serviced = sum([len(x.past_clients) for x in client_pools])
    all_clients_serviced = []
    for c_p in client_pools:
        all_clients_serviced += c_p.past_clients
    average_waiting_time = sum(
        [x.waiting_time for x in all_clients_serviced]) / len(all_clients_serviced)
    return result_str + "%d clients serviced, with average waiting time %fs" % (total_clients_serviced, average_waiting_time)


counters = bank()

client_pools.sort(key=attrgetter('priority'), reverse=True)


def choose_next_client():
    '''
    How to choose next client?
    '''
    for pool in client_pools:
        if counters.check_pool_on_service_state(pool) != True and len(pool) > 0:
            return pool.pop(0)  # 每个有人的队列至少有一个窗口

    pools = list(filter(lambda x: len(x) != 0, client_pools))
    return pools[0].pop(0)
    '''
    return random.choice(pools).pop(0)
    '''


def test():
    generate_pre_waiting_client()
    counters.alloc_counters(client_pools)
    counters.set_business(True)
    for pool in client_pools:
        print(pool)
    '''
    motor.set_supervise_check_point(
        int(input('enter a check point in second:')))
    '''
    motor.process()

    print(summary())


test()
