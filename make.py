
import sys
from os import chdir
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from subprocess import run
from threading import Thread
from time import sleep

UI_FOLDER = Path('ui')
SEED_FOLDER = Path('seed')

if not SEED_FOLDER.exists():
    SEED_FOLDER.mkdir()


def start_server():
    run('pnpm dev', shell=True)


def show_ui():
    run('python main.py', shell=True)


def parse_size(size: str):
    size = size.lower()

    if size.endswith('gb'):
        return int(size[:-2]) * 1024 * 1024 * 1024

    if size.endswith('mb'):
        return int(size[:-2]) * 1024 * 1024

    if size.endswith('kb'):
        return int(size[:-2]) * 1024

    if size.endswith('b'):
        return int(size[:-1])


args = sys.argv[1:]

if args:
    command, *args = args

    if command == 'seed':
        if len(args) == 0:
            raise Exception('No quantity provided')

        quantity = int(args[0])

        if len(args) == 1:
            size = '1mb'

        if len(args) == 2:
            size = args[1]

        size = parse_size(size)

        def seed(i):
            with open(SEED_FOLDER / f'{i}', 'wb') as f:
                for _ in range(0, size, 1024 * 10):
                    f.write('a'.encode('utf-8') * 1024 * 10)

        with ThreadPoolExecutor(max_workers=16) as executor:
            for i in range(quantity):
                executor.submit(seed, i)

else:
    chdir(UI_FOLDER)
    Thread(target=start_server).start()

    sleep(1)

    chdir('..')
    show_ui()
