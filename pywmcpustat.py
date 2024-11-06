#!/usr/bin/env python3.11
import os
import argparse
import re 
import subprocess
import math
import time
import wmdocklib

with open(os.path.dirname(__file__) + "/background.xpm", "r") as fo:
    BACKGROUND = "".join(fo.readlines())

with open(os.path.dirname(__file__) + "/font.xpm", "r") as fo:
    FONT = "".join(fo.readlines())

with open(os.path.dirname(__file__) + "/font_text.xpm", "r") as fo:
    TEXT_FONT = "".join(fo.readlines())

CPU_PATTERN = r"CPU (\d+):.* interrupt, ?(\d+\.\d+)%"

def gradient_color(value, min_value=1, max_value=100):
    # Ensure value is within bounds
    value = max(min_value, min(value, max_value))
    

    ratio = 7/max_value
    
    val = math.ceil((100 - value) * ratio)

    return val

def get_cpus(data):
    lines = data.split(b'\n')
    results = []
    for l in lines:
        match = re.search(CPU_PATTERN, l.decode('utf-8'))
        if match:
            results = [match.groups()] + results

    return results

class CpuDockApp(wmdocklib.DockApp):
    background_color = "#202020"
    graph_width = 58
    graph_max_height = 36
    graph_coords = (3, 25)

    def __init__(self, args=None):
        super().__init__(args)
        self._remote_args = ["ssh", args.remote, "top -P -n -s 0.01 -d 20"]
        self.name = args.name
        self.fonts = [wmdocklib.BitmapFonts(FONT, (5, 4)), wmdocklib.BitmapFonts(TEXT_FONT, (6, 8))]
        self.background = BACKGROUND

    def _put_string(self, item, h_pos=1, v_pos=1, font_setting=0):
        name = item
        self.fonts[font_setting].add_string(name, v_pos, h_pos)

    def _set_cpu(self):
        output = subprocess.check_output(self._remote_args)
        data = get_cpus(output)
        ncpu = int(data[0][0]) + 1
        
        temp = {}
        for k, i in data:
            if k in temp:
                temp[k] = min(temp[k], i)
            else:
                temp[k] = i

        idle = [gradient_color(int(float(idle))) for _, idle in temp.items()]

        max_per_row = 11
        to_print = [idle[x:x+max_per_row] for x in range(0, len(idle), max_per_row)]

        symbol_offset = " "
        for idx, row in enumerate(to_print):
            item = ''.join([chr((ord(symbol_offset) + val)) for val in row])
            self._put_string(item, h_pos=idx*4)


    def run(self):
        self.prepare_pixmaps()
        self.open_xwindow()
        try:
            self.main_loop()
        except KeyboardInterrupt:
            pass

    def main_loop(self):

        count = 0
        while True:
            if count > 360:
                self._set_cpu()
                count = 0

            count += 1

            self._put_string(self.name.upper(), h_pos=50, font_setting=1)
            self.redraw()
            time.sleep(0.1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="Name")
    parser.add_argument("-r", "--remote", help="hostname")
    args = parser.parse_args()

    dockapp = CpuDockApp(args)
    dockapp.run()


if __name__ == "__main__":
    main()
