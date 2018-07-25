#!/usr/bin/env python


import sys


def main(stdin):
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
        except UnicodeDecodeError:
            break
        
        if line.startswith('BG:'):
            normalized_line= ''.join(c.lower() if c.isalpha() else ' ' for c in line[4:])
                        
            #--- remove leading and trailing whitespace---
            line = normalized_line.strip()

            #--- split the line into words ---
            words = line.split()

            #--- output tuples [word, 1] in tab-delimited format---
            for word in words: 
                print(f'{word}\t1')

                
if __name__ == '__main__':
    main(sys.stdin)
