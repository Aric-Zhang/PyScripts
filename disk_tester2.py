from virtual_fat_disk import *
import turtle
import random
from PIL import Image, ImageDraw, ImageFont

d = vir_disk('_800kdisk', 800 * 1024)
# d.brief_fat(max=1800)
# print(d.read_via_index(1796))


class painter:
    GRID_SIZE = 40
    ROW_COUNT = 15
    COL_COUNT = 20
    WIDTH = 800
    HEIGHT = 600

    def __init__(self):
        self.block = Image.new(
            "RGB", (self.GRID_SIZE, self.GRID_SIZE), 'black')

    def paint(self, index_state_list):
        fat_length = len(index_state_list)
        im = Image.new("RGB", (self.WIDTH, self.HEIGHT), 'grey')
        draw = ImageDraw.Draw(im)
        i = 0
        for state in index_state_list:
            if state == FAT_16_EOF:
                draw.rectangle(self.__get_grid_box(i), fill=(255, 255, 0))
            elif state > NULL:
                draw.rectangle(self.__get_grid_box(i), fill=(0, 255, 0))
            elif state == NULL:
                draw.rectangle(self.__get_grid_box(i), fill=(255, 255, 255))
            elif state < NULL:
                draw.rectangle(self.__get_grid_box(i), fill=(0, 0, 255))
            i += 1
        self.draw_icon(draw)
        im.show('map')
        im.save('map.jpg', 'jpeg')

    def __get_grid_box(self, index):
        row = index // self.COL_COUNT
        col = index % self.COL_COUNT
        row_pos = row * self.GRID_SIZE
        col_pos = col * self.GRID_SIZE
        return (col_pos, row_pos, col_pos + self.GRID_SIZE - 2, row_pos + self.GRID_SIZE - 2)

    def draw_icon(self, draw):
        font = ImageFont.truetype('C:\\Windows\\Fonts\\Arial.ttf', 30)
        draw.rectangle((100, 500, 100 + self.GRID_SIZE - 2, 500 + self.GRID_SIZE - 2),
                       fill=(255, 255, 0))
        draw.rectangle((250, 500, 250 + self.GRID_SIZE - 2, 500 + self.GRID_SIZE - 2),
                       fill=(0, 255, 0))
        draw.rectangle((400, 500, 400 + self.GRID_SIZE - 2, 500 + self.GRID_SIZE - 2),
                       fill=(255, 255, 255))
        draw.rectangle((600, 500, 600 + self.GRID_SIZE - 2, 500 + self.GRID_SIZE - 2),
                       fill=(0, 0, 255))

        draw.text((150, 500), 'EOF', font=font, fill=(255, 255, 255))
        draw.text((300, 500), 'Written', font=font, fill=(255, 255, 255))
        draw.text((450, 500), 'Avaliable', font=font, fill=(255, 255, 255))
        draw.text((650, 500), 'Boot', font=font, fill=(255, 255, 255))


print('step 1')

path = 'test_dir_2'

list_dir = [x for x in os.listdir(path) if os.path.isfile(x)]
list_length = len(list_dir)
files = d.list_root_dir()
for file in files:
    d.delete_file_by_name(file)

try:
    for i in range(0, 20):
        rand_file_index = random.randint(0, list_length - 1)
        suffix = os.path.splitext(list_dir[rand_file_index])[-1]
        byte_content = load_file_once(
            os.path.join(path, list_dir[rand_file_index]))
        d.write_new_file('test_insert%d' % i + suffix, byte_content)
except ValueError:
    print("%d files written.")
    pass
# print(d.list_root_dir())
root_dir = d.list_root_dir()
for filename in root_dir:
    d.breif_loacations_by_filename(filename)
# d.brief_fat(max=4096)

index_state_list = d.get_sector_state()
p = painter()
p.paint(index_state_list)

print('step 2')
files = d.list_root_dir()
for i in range(10):
    try:
        random_file = files[random.randint(0, len(files) - 1)]
    except ValueError:
        break
    d.delete_file_by_name(random_file)
    files.remove(random_file)
# print(d.list_root_dir())
root_dir = d.list_root_dir()
for filename in root_dir:
    d.breif_loacations_by_filename(filename)
# d.brief_fat(max=4096)

index_state_list = d.get_sector_state()
p = painter()
p.paint(index_state_list)

print('step 3')
try:
    for i in range(20, 40):
        rand_file_index = random.randint(0, list_length - 1)
        suffix = os.path.splitext(list_dir[rand_file_index])[-1]
        byte_content = load_file_once(
            os.path.join(path, list_dir[rand_file_index]))
        d.write_new_file('test_insert%d' % i + suffix, byte_content)
except ValueError:
    print("%d files written.")
    pass
# print(d.list_root_dir())
root_dir = d.list_root_dir()
for filename in root_dir:
    d.breif_loacations_by_filename(filename)
# d.brief_fat(max=4096)

index_state_list = d.get_sector_state()
p = painter()
p.paint(index_state_list)

print('step 4')
files = d.list_root_dir()
for i in range(10):
    try:
        random_file = files[random.randint(0, len(files) - 1)]
    except ValueError:
        break
    d.delete_file_by_name(random_file)
    files.remove(random_file)
# print(d.list_root_dir())
root_dir = d.list_root_dir()
for filename in root_dir:
    d.breif_loacations_by_filename(filename)
# d.brief_fat(max=4096)

index_state_list = d.get_sector_state()
p = painter()
p.paint(index_state_list)
