import random
from operator import attrgetter

COUNTER_NUM = 9
CALL_WAITING_TIME = 30

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

    def process_one_shot(self):
        # print(len(self))
        for process in self:
            if process.enabled:
                process.update()
        self.current_time += 1

    def process(self):
        for i in range(self.total_time_length):
            if self.time_left > 20 * 60:
                generate_client_by_chance()
            for process in self:
                if process.enabled:
                    process.update()
            self.time_left -= 1
            self.current_time += 1

    def get_time_via_sec(self):
        '''
        格式化时间
        '''
        seconds = self.current_time
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return ("%02d:%02d:%02d" % (h, m, s))


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
        print(motor.get_time_via_sec() + " " +'%s is on service at %s' % (str(new_client), self.id))

    def update(self):
        self.time_left -= 1
        if self.time_left <= 0:
            try:
                self.service_next_client(choose_next_client())
            except IndexError:
                if self.time_left == 0:
                    print('counter %s no client to service' % self.id)


class bank(list):
    def __init__(self):
        for i in range(COUNTER_NUM):
            self.append(counter(str(i + 1), enabled=False))

    def get_next_service_time(self):
        '''
        返回最近的下一个柜台服务完成的时间
        '''
        each_time_left = [x.time_left for x in self]
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
    counters.set_business(True)
    for pool in client_pools:
        print(pool)

    motor.process()

    for pool in client_pools:
        print(pool)


test()
