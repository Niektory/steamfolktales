# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

MEGA = 1048576
MEGA_STR = ' ' * MEGA

def alloc_max_array():
    i = 0
    ar = []
    while True:
        try:
            #ar.append(MEGA_STR)  # no copy if reusing the same string!
            #ar.append(MEGA_STR + str(i))
            ar.append(' ' * MEGA)
        except MemoryError:
            break
        i += 1
    max_i = i - 1
    print('Maximum array allocation:', max_i, 'MB')#, "{:,}".format(sys.getsizeof(ar))

def alloc_max_str():
    i = 0
    while True:
        try:
            a = ' ' * (i * MEGA)
            #print "{:,}".format(sys.getsizeof(a))
            del a
        except MemoryError:
            break
        i += 100
    max_i = i - 100
    print('Maximum string allocation:', max_i, 'MB')
