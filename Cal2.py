#!/usr/bin/env python3
# -*- coding: utf-8 -*-

' a calendar module '

__author__ = 'Aric Zhang'

# 1900年1月1日是星期一
listr = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
listp = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

month_name = ["JAN", "FEB", "MAR", "APR", "MAY",
              "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


class Month(object):
    def __init__(self, month, dayy, r):
        self.mon_name = month_name[month - 1]
        daym = 0

        if r:
            for i in range(0, month - 1):
                daym += listr[i]
        else:
            for i in range(0, month - 1):
                daym += listp[i]
        # print(daym)
        days = daym + dayy + 1
        self.week = days % 7
        self.str_list = []
        self.str_list.append("\t\t\t" + month_name[month - 1] + "\t\t\t\t")
        self.str_list.append("日\t一\t二\t三\t四\t五\t六\t")

        week_str = "\t" * self.week
        if r:
            i = 1
            while i <= listr[month - 1]:
                week_str += "%2d\t" % i
                if (i + self.week) % 7 == 0:
                    self.str_list.append(week_str)
                    week_str = ""
                i += 1
        else:
            i = 1
            while i <= listp[month - 1]:
                week_str += "%2d\t" % i
                if (i + self.week) % 7 == 0:
                    self.str_list.append(week_str)
                    week_str = ""
                i += 1

        week_str += (7 - (i + self.week - 1) % 7) % 7 * "\t"
        if len(week_str) != 0:
            self.str_list.append(week_str)

    def __str__(self):
        month_str = ""
        for week_str in self.str_list:
            month_str += week_str
            month_str += "\n"
        return month_str

    def get_week_count(self):
        return len(self.str_list)

    def get_occu_str(self):
        return "\t" * 7


#month_test = Month(month, dayy, r)


class Year(object):
    def __init__(self, year):
        r = year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)
        dayy = 365 * (year - 1900) + (year - 1900 - 1) // 4 - \
            (year - 1900 - 1) // 100 + (year - 1600 - 1) // 400

        self.month_list = []

        for i in range(1, 13):
            self.month_list.append(Month(i, dayy, r))

    def __str__(self):
        year_str = ""
        for i in range(0, len(self.month_list) // 3):
            current_month_row = self.month_list[i * 3:i * 3 + 3]
            for j in range(max([count.get_week_count() for count in current_month_row])):
                for mon in current_month_row:
                    try:
                        year_str += mon.str_list[j] + "\t"
                    except IndexError:
                        year_str += mon.get_occu_str() + "\t"
                year_str += "\n"
            year_str += "\n"
        return year_str


if __name__ == '__main__':
    year = int(input("请输入年份："))
    year = Year(year)
    print(year)
