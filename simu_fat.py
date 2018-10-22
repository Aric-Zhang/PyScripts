#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random


DISK_SIZE = 100 * 1024 * 1024
BLOCK_SIZE = 512 * 1024
FAT_LENGTH = DISK_SIZE // BLOCK_SIZE
FAT_NULL = 0
FAT_EOF = 0xffffffff


class disk:
    def __init__(self):
        self.fat_list = [0] * FAT_LENGTH
        self.file_list = []
        self.current_block = 1
        self.fat_list[0] = self.current_block

    def write_file_to_disk(self, new_file):
        if isinstance(new_file, v_file) != True:
            raise TypeError('not a file')
        self.file_list.append(new_file)
        content = new_file.get_file_content()()
        prev_index = 0
        index = 0
        try:
            for a in content:
                index = self.__find_next_avalable_block()
                if prev_index == 0:
                    new_file.start_index = index
                else:
                    self.__write_next_index(prev_index, index)
                prev_index = index
            self.__write_next_index(prev_index, FAT_EOF)
        except IndexError:
            try:
                self.__write_next_index(index, FAT_EOF)
            except ValueError:
                pass
            self.delete_file_from_disk(new_file)

    def get_next_index(self, index):
        if index == 0:
            raise ValueError('0 block is reserved for further use')
        return self.fat_list[index]

    def __write_next_index(self, index, content):
        if index == 0:
            raise ValueError('0 block is reserved for further use')
        self.fat_list[index] = content

    def print_fat(self):
        for index in self.fat_list:
            if index == FAT_EOF:
                print('EOF', end="   ")
            else:
                print('%3d' % index, end="   ")
        print()

    def get_file_fat_nodes(self, written_file):
        if isinstance(written_file, v_file) != True:
            raise TypeError('not a file')
        node_list = []
        self.file_list.index(written_file)
        index = written_file.start_index
        while index != FAT_EOF:
            node_list.append(index)
            index = self.get_next_index(index)
        return node_list

    def print_files(self):
        for file in self.file_list:
            node_list = self.get_file_fat_nodes(file)
            print(file)
            print("nodes:%s" % str(node_list))

    def delete_file_from_disk(self, written_file):
        if isinstance(written_file, v_file) != True:
            raise TypeError('not a file')
        self.file_list.remove(written_file)
        try:
            index = written_file.start_index
        except AttributeError:
            return
        while index != FAT_EOF:
            next_index = self.get_next_index(index)
            self.__write_next_index(index, FAT_NULL)
            index = next_index

    def __find_next_avalable_block(self):
        endflag = self.current_block
        while self.get_next_index(self.current_block) != FAT_NULL:
            self.current_block += 1
            if self.current_block >= FAT_LENGTH:
                self.current_block = 1
            if self.current_block == endflag:
                raise IndexError('the disk is already full.')
        return self.current_block


class v_file:
    def __init__(self):
        max_size = 20 * 1024 * 1024
        self.size = random.randint(0, max_size)

    @property
    def num_of_blocks(self):
        if self.size % BLOCK_SIZE != 0:
            rear = 1
        else:
            rear = 0
        return self.size // BLOCK_SIZE + rear

    def get_file_content(self):
        num = self.num_of_blocks

        def file_content():
            for i in range(0, num):
                yield 0
        return file_content

    def __str__(self):
        return "----------------------\nfile info:\nsize:%d" % self.size


d = disk()
print("----------------------Step 1----------------------")
try:
    for i in range(0, 20):
        d.write_file_to_disk(v_file())
except IndexError:
    print('disk full')
d.print_fat()
d.print_files()
print("----------------------Step 2----------------------")
for i in range(0, 10):
    num_of_files = d.file_list
    d.delete_file_from_disk(
        d.file_list[random.randint(0, len(d.file_list) - 1)])
d.print_fat()
d.print_files()
print("----------------------Step 3----------------------")
try:
    for i in range(0, 20):
        d.write_file_to_disk(v_file())
except IndexError:
    print('disk full')
d.print_fat()
d.print_files()
print("----------------------Step 4----------------------")
for i in range(0, 5):
    num_of_files = d.file_list
    d.delete_file_from_disk(
        d.file_list[random.randint(0, len(d.file_list) - 1)])
d.print_fat()
d.print_files()
