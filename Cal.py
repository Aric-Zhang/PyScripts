year = int(input("请输入年份："))
# 1900年1月1日是星期一

listr = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
listp = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

month_name = ["JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY",
              "JUNE", "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"]

# 年份index为真实年份，月份index为真实月份-1，即1月为0


def get_first_day_in_week(year_index, month_index, leap_flag=False):
    dayy = 365 * (year_index - 1900) + (year_index - 1900 - 1) // 4 - \
        (year_index - 1900 - 1) // 100 + (year_index - 1600 - 1) // 400
    # 蔡勒公式使用，一年的第一天是星期几
    daym = 0
    if leap_flag:
        for i in range(0, month_index - 1):
            daym += listr[i]
    else:
        for i in range(0, month_index - 1):
            daym += listp[i]
    # 顺推每个月的第一天是星期几
    days = daym + dayy + 1
    return days % 7


def month_generator_get(month_index, first_day_in_week, leap_flag=False):

    def get_month_str_in_week():
        yield month_name[month_index - 1].center(4 * 7, " ")
        yield "日{0}一{0}二{0}三{0}四{0}五{0}六{0}".format("\t")

        week_str = "\t" * first_day_in_week  # 第一天是星期几，前面就空几格
        i = 1  # 一个月的天数进度
        if leap_flag:
            number_of_days = listr[month_index - 1]
        else:
            number_of_days = listp[month_index - 1]

        while i <= number_of_days:
            week_str += ("%2d\t" % i)
            if (i + first_day_in_week) % 7 == 0:
                yield week_str
                week_str = ""
            i += 1
        if(week_str != ""):
            week_str += (7 - (first_day_in_week + number_of_days) % 7) * "\t"
            yield week_str

    return get_month_str_in_week


def print_year(year_index, *, separator="\t", col_count=3, segment_spacing=1):
    print(str(year).center(col_count * 4 * 7 + (col_count - 1) * 4), " ")
    # 闰年标记计算
    r = year % 400 == 0 or (year % 4 == 0 and year % 100 != 0)
    month = 0  # 月份记号
    for i in range(12 // col_count):
        month_generator_list = []
        for month in range(month, col_count + month):
            week = get_first_day_in_week(year_index, month + 1, r)
            month_generator_list.append(
                [month_generator_get(month + 1, week, r)(), True])
        month += 1

        for spacing in range(segment_spacing):
            print()

        while True:
            line_str = ""
            print_flag = False
            for month_generator in month_generator_list:
                try:
                    line_str += next(month_generator[0])
                    print_flag = True
                except StopIteration:
                    month_generator[1] = False
                    line_str += "\t" * 7
                line_str += separator

            if False == print_flag:
                break
            else:
                print(line_str)


print_year(year)
