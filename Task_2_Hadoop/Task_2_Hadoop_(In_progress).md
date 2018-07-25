
# Task 2

*Note: check shebang. Works on macOS `#!/usr/bin/env python3`. Works on Windows `#!/usr/bin/env python`.*

Word count in Python streaming
The goal of this task is to write map-reduce job in [Hadoop Streaming](http://hadoop.apache.org/docs/stable/hadoop-streaming/HadoopStreaming.html) using python, i.e. the mapper and reducer have to be written in Python. Note that the Hadoop Streaming map-reduce job can be tested on a local Hadoop cluster or by faking it with the following
shell command:

```Bash
cat dataset.txt | python your_mapper.py | sort -k1,1 | python your_reducer.py
```

- **a.** Download the [data](https://s3.amazonaws.com/products-42matters/test/biographies.list.gz) set over which to run word count.

- **b.** Implement a mapper and reducer in python that counts the number of
occurrences of each word in the provided file.  
Only lines **starting with the “BG:”** should be considered, and a whitespace tokenizer should be used for tokenizing the text.

___
First is pretty straightforward. We've got the file `biographies.list.gz`.

- decompress archive with:
```Bash
gzip -d biographies.list.gz
```
- check it:
```Bash
cat biographies.list | head -n 20
```

Our mapper, implemented on Python:
```Python
#!/usr/bin/env python3

import sys


def main(stdin):
    
    while True:
        # to be safe from corrupted input 
        try:
            line = stdin.readline()
            if not line:
                break
        except UnicodeDecodeError:
            break
        
        if line.startswith('BG:'):
            normalized_line= ''.join(c.lower() if c.isalpha() else ' ' for c in line[4:])
                        
            # remove leading and trailing whitespace
            line = normalized_line.strip()

            # split the line into words
            words = line.split()

            # output tuples [word, 1] in tab-delimited format
            for word in words: 
                print(f'{word}\t1')

                
if __name__ == '__main__':
    main(sys.stdin)
```

- make mapper executable (we need that to work with **Hadoop**):
```Bash
chmod +x mapper.py
```
- test mapper with:
```Bash
cat  |  biographies.list | head -n 20 | ./mapper.py | sort -k 1,1
```

Our reducer:
```Python
#!/usr/bin/env python3

from operator import itemgetter
import sys

current_word = None
current_count = 0
word = None

# input comes from STDIN
for line in sys.stdin:
    # remove leading and trailing whitespace
    line = line.strip()

    # parse the input we got from mapper.py
    word, count = line.split('\t', 1)

    # convert count (currently a string) to int
    try:
        count = int(count)
    except ValueError:
        # count was not a number, so silently
        # ignore/discard this line
        continue

    # this IF-switch only works because Hadoop sorts map output
    # by key (here: word) before it is passed to the reducer
    if current_word == word:
        current_count += count
    else:
        if current_word:
            # write result to STDOUT
            print(f'{current_word}\t{current_count}')
        current_count = count
        current_word = word

# do not forget to output the last word if needed!
if current_word == word:
    print(f'{current_word}\t{current_count}')
```

- make reducer executable (we need that to work with **Hadoop**):
```Bash
chmod +x reducer.py
```
- test reducer with:
```Bash
cat  |  biographies.list | head -n 20 | ./mapper.py | sort -k 1,1 | ./reducer.py
```

*Everything is ready to use Hadoop... but...*
