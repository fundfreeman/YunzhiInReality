import os, subprocess
from typing import List, Tuple

from pathgen import GEO_POINT
from const import SAMPLE_PERIOD

def sample(pass_points : List[GEO_POINT], speed1 : float, speed2 : float) -> List[GEO_POINT]:
    p = subprocess.Popen(['gen'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    p.stdin.write(f'{len(pass_points)}\n'.encode())
    # print(f'{len(pass_points)}\n')
    for point in pass_points:
        p.stdin.write(f'{point[1]} {point[0]}\n'.encode())
        # print(f'{point[1]} {point[0]}\n')
    p.stdin.write(f'{SAMPLE_PERIOD} 5 {speed1} {speed2}'.encode())
    # print(f'2000 5 {speed}')
    p.stdin.close()

    res = []
    while True:
        bt = p.stdout.readline()
        if not bt:
            break
        # print(bt.decode(), end='')
        st = bt.decode().strip().split(',')
        if len(st) > 3:
            res.append( ((float(st[2]), float(st[1])), float(st[3])) )

    p.terminate()
    return res
