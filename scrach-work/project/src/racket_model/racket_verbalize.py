import os

def remove_langs(path):
    temp_path = path + '.temp'
    with open(path, 'r', errors='ignore') as in_file, open(temp_path, 'w') as temp_file:
        for line in in_file:
            if not lang_line(line):
                temp_file.write(line)

    os.remove(path)
    os.rename(temp_path, path)

def lang_line(line: str):
    return line.strip().startswith('#lang')


def verbalize_file(path):
    remove_langs(path)


verbalize_file('output/0a98082deb09707a710455ad72e139da970fae0a482c5db466d7c9e11947956b.rkt')