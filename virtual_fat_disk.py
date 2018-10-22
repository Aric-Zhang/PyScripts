#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'a virtual_fat16_disk module'

__author__ = 'Aric Zhang'

NULL = 0
FAT_16_SECTOR_SIZE = 4 * 1024  # 4KB大小的扇区
FAT_16_LOCATION_SIZE = 4  # 4B大小的列表项
FAT_16_EOF = int.from_bytes((0xff).to_bytes(
    1, byteorder='big') * FAT_16_LOCATION_SIZE, byteorder='big')  # 根据列表项大小确定EOF
INVALID_INDEX = -1

import os
import json


def create_disk(name, size=1024 * 1024):
    try:
        with open('%s.txt' % name, 'rb') as f:
            print('disk name %s already exists.' % name)
            return False
    except FileNotFoundError:
        with open('%s.txt' % name, 'x') as f:
            print('new disk %s created.' % name)
            f = open('%s.txt' % name, 'rb+')
            null_content = (0).to_bytes(size, byteorder='big')
            f.write(null_content)
            f.seek(0, 0)
            return True

    #f = open('%s.txt' % name, 'rb+')
    # return f


def open_disk(name, mode='rb+'):
    f = open('%s.txt' % name, mode)
    return f

# 一次加载全部的文件


def load_file_once(path):
    with open(path, 'rb') as f:
        bytes_content = f.read()
        return bytes_content

# 根据扇区大小逐步加载文件


def load_file_by_sector_size(path):
    with open(path, 'rb') as f:
        size = os.path.getsize(path)
        times = size // FAT_16_SECTOR_SIZE
        if(times % FAT_16_SECTOR_SIZE) > 0:
            times += 1
        for i in range(0, times):
            bytes_content = f.read(FAT_16_SECTOR_SIZE)
            yield bytes_content


def get_root_dir():
    pass

# 每次返回一个扇区大小的bytes


def sector_generator_from_bytes(bytes_content):
    while len(bytes_content) > FAT_16_SECTOR_SIZE:
        yield bytes_content[:FAT_16_SECTOR_SIZE]
        bytes_content = bytes_content[:FAT_16_SECTOR_SIZE - 1:-1][::-1]
    yield bytes_content


class vir_disk(object):
    def __init__(self, path, size=1024 * 1024):
        self.__path = path
        if create_disk(self.__path, size):
            self.alloc_fat()
            self.alloc_root_dir()
            print('Done')
        else:
            self.num_of_indexes = self.get_num_of_indexes()

    def __getattr__(self, attr):
        if attr == 'num_of_indexes':
            self.num_of_indexes = get_num_of_indexes()
            return self.num_of_indexes

    def get_file(self):
        return open_disk(self.__path)

    # 从文件中读取硬盘的index总数
    def get_num_of_indexes(self):
        with self.__read_file() as f:
            return int.from_bytes(f.read(FAT_16_LOCATION_SIZE), byteorder='big')

    # 私有的只读打开文件方法
    def __read_file(self):
        return open_disk(self.__path, 'rb')

    # 分配FAT表
    def alloc_fat(self):
        size = os.path.getsize(self.__path + '.txt')
        print('disk_part_alloc:' + str(size) + ' B')
        num_of_sectors = size // FAT_16_SECTOR_SIZE
        index_per_sector = FAT_16_SECTOR_SIZE // FAT_16_LOCATION_SIZE
        num_of_index_sector = 1
        while num_of_index_sector + num_of_index_sector * index_per_sector < num_of_sectors - 1:
            num_of_index_sector += 1
        print('num of index sector:' + str(num_of_index_sector))
        num_of_indexes = num_of_sectors - num_of_index_sector - 1
        print('num of sectors:' + str(num_of_sectors))
        print('num of indexes:' + str(num_of_indexes))
        with self.get_file() as f:
            f.write((num_of_indexes).to_bytes(
                FAT_16_LOCATION_SIZE, byteorder='big'))
            f.seek(0, 0)
            self.num_of_indexes = num_of_indexes
            print("recorded num of indexes:" +
                  str(int.from_bytes(f.read(FAT_16_LOCATION_SIZE), byteorder='big')))

    # 打印FAT表
    def brief_fat(self, min=0, max=256):
        with self.__read_file() as f:
            num_of_indexes = int.from_bytes(
                f.read(FAT_16_LOCATION_SIZE), byteorder='big')
            if max > num_of_indexes:
                max = num_of_indexes
            for i in range(min, max):
                print('%08x' % self.get_next_index(f, i), end=' ')
            print()

    # 打印文件信息
    def breif_loacations_by_filename(self, filename):
        inode = self.__get_inode_by_filename(filename)
        size = inode['size']
        loc_list = []
        index = inode['first_index']
        with self.__read_file() as f:
            while index != FAT_16_EOF:
                loc_list.append(index)
                index = self.get_next_index(f, index)
        print('filename:%s' % filename)
        print('size:%d' % size + " B")
        print('alloc:')
        for loc in loc_list:
            print(loc, end=' ')
        print('\n----------')

        # 初始化根目录表
    def alloc_root_dir(self):
        root_dict = {'root': 0}
        self.__modify_root_dir(root_dict)
        with self.get_file() as f:
            self.write_next_index(f, 0, FAT_16_EOF)

    # 获取根目录表(仅当前0号扇区)
    def get_root_dir(self):
        with self.__read_file() as f:
            bytes_content = b''
            index = 0
            while index != FAT_16_EOF:
                # print(index)
                bytes_content += self.read_via_index(index)
                index = self.get_next_index(f, index)
            json_str = bytes_content.decode('utf-8').strip(chr(0))
            # print(json_str)
            root_dict = json.loads(json_str)
        return root_dict

    # 获取根目录文件名
    def list_root_dir(self):
        root_dict = self.get_root_dir()
        root_dict.pop('root')
        dir_list = [x for x in root_dict]
        return dir_list

    # 私有，根据一个新的root_dict覆盖原有根目录
    def __modify_root_dir(self, root_dict):
        json_str = json.dumps(root_dict)
        bytes_content = json_str.encode('utf-8')

        self.write_to_disk(bytes_content, 0, clean_sector=True)
        print('root dir modified')
        '''
        with self.get_file() as f:
            self.__clear_sector_via_index(f, 0)
            self.__write_content_via_index(f, 0, bytes_content)
            self.write_next_index(f, 0, FAT_16_EOF)
        '''

    # 根据文件名删除一个文件
    def delete_file_by_name(self, filename):
        if isinstance(filename, str) != True:
            raise TypeError('filename is not a valid string!')
        root_dict = self.get_root_dir()
        try:
            inode = self.__get_inode_by_filename(filename)
            print('deleting %s' % filename)
            first_index = inode['first_index']
            with self.get_file() as f:
                self.__erase_rear_index(f, first_index)
                root_dict.pop(filename)
            self.__modify_root_dir(root_dict)
        except KeyError:
            print('Cannot find %s' % filename)

    # 根据文件名和内容写入文件
    def write_new_file(self, filename, bytes_content):
        print('writing %s' % filename)
        if isinstance(filename, str) != True:
            raise TypeError('filename is not a valid string!')
        root_dict = self.get_root_dir()
        try:
            inode = root_dict[filename]
            print('filename already exists!')
        except KeyError:
            size = len(bytes_content)
            avaliable_storage = self.get_avaliable_storage()
            if size > avaliable_storage:
                raise ValueError('Too large file!')
            first_index = self.write_to_disk(bytes_content)
            inode = {'first_index': first_index, 'size': size}
            inode_json = json.dumps(inode)
            root_dict[filename] = inode_json
            self.__modify_root_dir(root_dict)

    # 提取文件
    def extract_file_to_bytes(self, filename):
        if isinstance(filename, str) != True:
            raise TypeError('filename is not a valid string!')
        root_dict = self.get_root_dir()
        try:
            inode = self.__get_inode_by_filename(filename)
            bytes_content = b''
            index = inode['first_index']
            size = inode['size']
            with self.get_file() as f:
                next_index = self.get_next_index(f, index)
                while(next_index != FAT_16_EOF):
                    bytes_content += self.__read_bytes_via_index(f, index)
                    index = next_index
                    next_index = self.get_next_index(f, index)
                spared_size = size % FAT_16_SECTOR_SIZE
                last_bytes = self.__read_bytes_via_index(f, index)
                bytes_content += last_bytes[:spared_size]
            return bytes_content
        except KeyError:
            print('Cannot find %s' % filename)

    # 覆盖一个已存在的文件
    def cover_old_file(self, filename, bytes_content):
        if isinstance(filename, str) != True:
            raise TypeError('filename is not a valid string!')
        root_dict = self.get_root_dir()
        try:
            inode = self.__get_inode_by_filename(filename)
            first_index = inode['first_index']
            new_size = len(bytes_content)
            self.write_to_disk(bytes_content, first_index)
            inode['size'] = new_size
            inode_json = json.dumps(inode)
            root_dict[filename] = inode_json
            self.__modify_root_dir(root_dict)
            return inode
        except KeyError:
            print('Cannot find %s' % filename)
            raise

    # 得到文件的inode节点
    def __get_inode_by_filename(self, filename):
        if isinstance(filename, str) != True:
            raise TypeError('filename is not a valid string!')
        root_dict = self.get_root_dir()
        try:
            inode_json = root_dict[filename]
            return json.loads(inode_json)
        except KeyError:
            print('Cannot find %s' % filename)
            raise

    # 清除末尾多余的index部分
    def __erase_rear_index(self, f, beginning_index):
        index = beginning_index

        if beginning_index == FAT_16_EOF:
            return

        next_index = self.get_next_index(f, index)
        while next_index != FAT_16_EOF:
            self.write_next_index(f, index, 0)
            index = next_index
            next_index = self.get_next_index(f, index)
        self.write_next_index(f, index, 0)

    # 把bytes写入虚拟硬盘的合适位置,返回第一个扇区index
    def write_to_disk(self, bytes_content, beginning_index=INVALID_INDEX, *, clean_sector=False):
        with self.get_file() as f:
            num_of_indexes = int.from_bytes(
                f.read(FAT_16_LOCATION_SIZE), byteorder='big')
            #print('indexs num read:' + str(num_of_indexes))
            num_of_index_sector = self.__get_num_of_index_sector()
            #print('calculated num of index sectors:' + str(num_of_index_sector))
            # 获取可写的位置，加上一个boot sector

            f.seek(FAT_16_SECTOR_SIZE, 0)

            if beginning_index == INVALID_INDEX:
                index = 0
            else:
                index = beginning_index
                next_index = beginning_index
            prev_index = -1

            generator = sector_generator_from_bytes(bytes_content)
            for sector_content in generator:
                if beginning_index != INVALID_INDEX:
                    if next_index == INVALID_INDEX:
                        next_index = beginning_index
                    if next_index == FAT_16_EOF:
                        beginning_index = INVALID_INDEX
                        next_index = 0
                        prev_index = index
                    index = next_index
                    next_index = self.get_next_index(f, index)

                while beginning_index == INVALID_INDEX and (self.get_next_index(f, index) != NULL or index == prev_index):
                    index += 1
                    if index >= num_of_indexes:
                        raise ValueError('No spared space!')

                if(prev_index != -1):
                    self.write_next_index(f, prev_index, index)
                else:
                    first_index = index

                print("index:%d" % index, end=" ")

                print(self.get_next_index(f, index))
                if clean_sector:
                    self.__clear_sector_via_index(f, index)
                self.__write_content_via_index(f, index, sector_content)
                prev_index = index
            self.write_next_index(f, index, FAT_16_EOF)

            if beginning_index != INVALID_INDEX:
                self.__erase_rear_index(f, next_index)

        return first_index

    # 将下一个地址的序号写进当前地址
    def write_next_index(self, f, current_index, next_index):
        if current_index > self.num_of_indexes:
            raise ValueError('index out of range')
        f.seek(FAT_16_SECTOR_SIZE + current_index * FAT_16_LOCATION_SIZE, 0)
        f.write((next_index).to_bytes(FAT_16_LOCATION_SIZE, byteorder='big'))

    # 从特定地址取出下一个地址
    def get_next_index(self, f, current_index):
        if current_index > self.num_of_indexes:
            raise ValueError('index out of range:%d' % current_index)
        f.seek(FAT_16_SECTOR_SIZE + current_index * FAT_16_LOCATION_SIZE, 0)
        return int.from_bytes(f.read(FAT_16_LOCATION_SIZE), byteorder='big')

    # index of index
    # 返回本虚拟硬盘的FAT表占用的sector数
    def __get_num_of_index_sector(self):
        with self.__read_file() as f:
            num_of_indexes = int.from_bytes(
                f.read(FAT_16_LOCATION_SIZE), byteorder='big')
            num_of_index_sector = num_of_indexes * FAT_16_LOCATION_SIZE // FAT_16_SECTOR_SIZE
            if((num_of_indexes * FAT_16_LOCATION_SIZE) % FAT_16_SECTOR_SIZE > 0):
                num_of_index_sector += 1
        return num_of_index_sector

    # 通过index将文件指针移到固定位置
    def seek_via_index(self, f, index):
        num_of_index_sector = self.__get_num_of_index_sector()
        pos = (num_of_index_sector + 1) * \
            FAT_16_SECTOR_SIZE + index * FAT_16_SECTOR_SIZE
        f.seek(pos, 0)

    # 获取空余簇数
    def __get_num_of_avaliable_sectors(self, f):
        num_of_indexes = int.from_bytes(
            f.read(FAT_16_LOCATION_SIZE), byteorder='big')
        avaliable_num = 0
        for i in range(0, num_of_indexes):
            if self.get_next_index(f, i) == 0:
                avaliable_num += 1
        return avaliable_num

    # 获取所有的index状态
    def get_sector_state(self):
        num_of_indexes = self.num_of_indexes
        state_list = [-2]
        for i in range(self.__get_num_of_index_sector()):
            state_list.append(-1)
        with self.__read_file() as f:
            for i in range(0, num_of_indexes):
                state_list.append(self.get_next_index(f, i))
        return state_list

    # 获取剩余字节数
    def get_avaliable_storage(self):
        with self.__read_file() as f:
            return self.__get_num_of_avaliable_sectors(f) * FAT_16_SECTOR_SIZE

    # 从一个index指示的位置返回读取的文件
    def read_via_index(self, index):
        with self.__read_file() as f:
            '''
            num_of_index_sector = self.__get_num_of_index_sector()
            first_writable_pos = (num_of_index_sector + 1) * FAT_16_SECTOR_SIZE
            f.seek(first_writable_pos, 0)
            '''
            self.seek_via_index(f, index)
            return f.read(FAT_16_SECTOR_SIZE)

    # 从一个index指示的位置返回读取的bytes，需要提供文件指针
    def __read_bytes_via_index(self, f, index):
        self.seek_via_index(f, index)
        return f.read(FAT_16_SECTOR_SIZE)

    # 根据索引的位置写入文件内容
    def __write_content_via_index(self, f, index, bytes_content):
        self.seek_via_index(f, index)
        f.write(bytes_content)

    # 清空一个扇区的已有内容
    def __clear_sector_via_index(self, f, index):
        self.__write_content_via_index(
            f, index, (0).to_bytes(FAT_16_SECTOR_SIZE, byteorder='big'))


import unittest


class test_disk(unittest.TestCase):
    def test_create_disk(self):
        create_disk('data1')
        # print(f.read(1024))

    def test_eof_value(self):
        self.assertTrue(FAT_16_EOF == 0xffffffff)

    def test_open_disk(self):
        with self.assertRaises(FileNotFoundError):
            with open_disk('nonexist') as f:
                # print(f.read(1024))
                pass
        with open_disk('data1') as f:
            pass

    def test_disk_size(self):
        create_disk('_1mdisk')
        self.assertTrue(os.path.getsize('_1mdisk.txt') == 1024 * 1024)
        create_disk('_3mdisk', 3 * 1024 * 1024)
        self.assertTrue(os.path.getsize('_3mdisk.txt') == 1024 * 1024 * 3)

    def test_vir_disk(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)

    def test_write_to_disk(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)
        with open('Circle.jpg', 'rb') as f:
            d.write_new_file('Circle.jpg', f.read())
        with open('Rice.jpg', 'rb') as f:
            d.write_new_file('Rice.jpg', f.read())
        d.write_new_file('resume.png', load_file_once('resume.png'))
        print(d.read_via_index(0))
        d.brief_fat()
    '''

    def test_delete_by_filename(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)
        d.delete_file_by_name('Rice.jpg')
        d.brief_fat()
    '''

    def test_write_index(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)
        with d.get_file() as f:
            self.assertTrue(d.get_next_index(f, 0) == 0xffffffff)
            #self.assertTrue(d.get_next_index(f, 1000) == 0)

    def test_load_file_by_sector_size(self):
        loader = load_file_by_sector_size('Circle.jpg')
        for i in range(6):
            bytes_content = next(loader)
        with self.assertRaises(StopIteration):
            bytes_content = next(loader)

    def test_root_dir(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)
        root_dict = d.get_root_dir()
        print(root_dict)
        self.assertTrue(isinstance(root_dict, dict))

    def test_sector_generator_from_bytes(self):
        with open('Circle.jpg', 'rb') as f:
            generator = sector_generator_from_bytes(f.read())
            for i in range(6):
                bytes_content = next(generator)
            with self.assertRaises(StopIteration):
                bytes_content = next(generator)

    def test_get_inode_by_filename(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)
        '''
        with open('Rice.jpg', 'rb') as f:
            test_inode = d.cover_old_file('Circle.jpg', f.read())

        with open('Circle.jpg', 'rb') as f:
            test_inode = d.cover_old_file('Rice.jpg', f.read())

        print(test_inode)

        d.cover_old_file('resume.png', load_file_once('effect.png'))
        '''
        with self.assertRaises(KeyError):
            d.cover_old_file('aaa.jpg', b'')

    def test_extract_file(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)
        bytes_content = d.extract_file_to_bytes('Circle.jpg')
        self.assertTrue(len(bytes_content) == 23810)
        with open("buffer.jpg", 'w+') as f:
            f.write('')
        with open("buffer.jpg", 'rb+') as f:
            f.write(bytes_content)

    def test_extract_png(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)
        bytes_content = d.extract_file_to_bytes('resume.png')
        with open("buffer.png", 'w+') as f:
            f.write('')
        with open("buffer.png", 'rb+') as f:
            f.write(bytes_content)

    def test_avaliable_storage(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)
        print('avaliable_storage:' + str(d.get_avaliable_storage()) + ' B')

    def test_large_file(self):
        d = vir_disk('_100mdisk', 100 * 1024 * 1024)

        with open('Circle.jpg', 'rb') as f:
            d.write_new_file('Circle.jpg', f.read())
        with open('Rice.jpg', 'rb') as f:
            d.write_new_file('Rice.jpg', f.read())
        d.write_new_file('resume.png', load_file_once('resume.png'))

        bytes_content = load_file_once('Big.mp4')
        print(d.get_avaliable_storage(), len(bytes_content))

        with self.assertRaises(ValueError):
            d.write_new_file('big file.mp4', bytes_content)


if __name__ == "__main__":
    unittest.main()
