import sys
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path
from subprocess import Popen, run
from threading import Thread
from typing import Literal, TypedDict

import webview
from send2trash import send2trash


class ExplorerItem(TypedDict):
    name: str
    path: str
    kind: Literal['file', 'folder']
    modified: str
    type: str
    size: str
    parent: str


def get_folder_size(path: Path):
    if path.is_dir():
        yield sum(get_folder_size(i) for i in path.iterdir())
    elif path.is_file():
        yield path.stat().st_size
    yield 0


def get_file_type(path: Path):
    name = path.name

    if path.is_dir():
        if any(name.endswith(i) for i in ['.vscode', 'vscode']):
            return 'Vscode'

        if any(name.endswith(i) for i in ['node_modules']):
            return 'Node Modules'

        if any(name.endswith(i) for i in ['public', '.public']):
            return 'Public'

        if any(name.endswith(i) for i in ['src', 'source', 'sources']):
            return 'Src'

        if any(
            name.endswith(i)
            for i in ['component', 'components', '.components', 'gui', 'ui', 'widgets']
        ):
            return 'Component'

        if any(
            name.endswith(i)
            for i in [
                'html',
                'view',
                'views',
                'layout',
                'layouts',
                'page',
                'pages',
                '_view',
                '_views',
                '_layout',
                '_layouts',
                '_page',
                '_pages',
            ]
        ):
            return 'View'

        if any(
            name.endswith(i)
            for i in [
                'dist',
                '.dist',
                'dists',
                'out',
                'outs',
                'export',
                'exports',
                'build',
                '.build',
                'builds',
                'release',
                'releases',
                'target',
                'targets',
            ]
        ):
            return 'Dist'

        if any(
            name.endswith(i) for i in ['assets', '.assets', 'asset', '.asset', 'static']
        ):
            return 'Assets'

        if any(name.endswith(i) for i in ['git', '.git', 'submodules', '.submodules']):
            return 'Git'

        return 'folder'
    elif path.is_file():
        if any(name.endswith(i) for i in ['.py']):
            return 'Python'

        if any(name.endswith(i) for i in ['.prettierrc', '.prettierignore']):
            return 'Prettier'

        if any(
            name.endswith(i)
            for i in [
                'tsconfig.json',
                'tsconfig.app.json',
                'tsconfig.base.json',
                'tsconfig.common.json',
                'tsconfig.dev.json',
                'tsconfig.development.json',
                'tsconfig.e2e.json',
                'tsconfig.eslint.json',
                'tsconfig.node.json',
                'tsconfig.prod.json',
                'tsconfig.production.json',
                'tsconfig.server.json',
                'tsconfig.spec.json',
                'tsconfig.staging.json',
                'tsconfig.test.json',
                'tsconfig.lib.json',
                'tsconfig.lib.prod.json',
            ]
        ):
            return 'Tsconfig'

        if any(
            name.endswith(i)
            for i in [
                '.gitattributes',
                '.gitconfig',
                '.gitignore',
                '.gitmodules',
                '.gitkeep',
                '.mailmap',
                '.issuetracker',
            ]
        ):
            return 'Git'

        if any(name.endswith(i) for i in ['.yaml', '.yml', '.yaml-tmlanguage']):
            return 'Yaml'

        if any(name.endswith(i) for i in ['.markdown', '.md', '.mdown']):
            return 'Markdown'

        if any(name.endswith(i) for i in ['.toml']):
            return 'Toml'

        if any(name.endswith(i) for i in ['.astro']):
            return 'Astro'

        if any(
            name.endswith(i)
            for i in [
                'astro.config.js',
                'astro.config.cjs',
                'astro.config.mjs',
                'astro.config.ts',
            ]
        ):
            return 'Astro Config'

        if any(
            name.endswith(i)
            for i in [
                'tailwind.js',
                'tailwind.cjs',
                'tailwind.coffee',
                'tailwind.ts',
                'tailwind.json',
                'tailwind.config.js',
                'tailwind.config.cjs',
                'tailwind.config.coffee',
                'tailwind.config.ts',
                'tailwind.config.json',
                '.tailwind.js',
                '.tailwind.cjs',
                '.tailwind.coffee',
                '.tailwind.ts',
                '.tailwind.json',
                '.tailwindrc.js',
                '.tailwindrc.cjs',
                '.tailwindrc.coffee',
                '.tailwindrc.ts',
                '.tailwindrc.json',
            ]
        ):
            return 'Tailwind'

        if any(name.endswith(i) for i in ['.d.ts', '.d.cts', '.d.mts']):
            return 'Typescript Definition'

        if any(name.endswith(i) for i in ['.db']):
            return 'Database'

        if any(name.endswith(i) for i in ['.svg']):
            return 'SVG'

        if any(name.endswith(i) for i in ['.html']):
            return 'HTML'

        if any(name.endswith(i) for i in ['.css']):
            return 'CSS'

        if any(
            name.endswith(i)
            for i in ['.woff', '.woff2', '.ttf', '.otf', '.eot', '.pfa', '.pfb', '.sfd']
        ):
            return 'Font'

        if any(name.endswith(i) for i in ['.csv', '.tsv', '.txt']):
            return 'Text'

        # ! --------------------------------------------
        # ! KEEP ALWAYS AT THE END
        # ! --------------------------------------------

        if any(
            name.endswith(i)
            for i in ['.json', '.jsonl', '.ndjson', '.json-tmlanguage', '.jsonc']
        ):
            return 'Json'

        if any(name.endswith(i) for i in ['.js']):
            return 'Javascript'

        if any(name.endswith(i) for i in ['.ts']):
            return 'Typescript'

        return 'file'
    return 'unknown'


class StreamFolderSize:
    def __init__(self, path: str):
        self.size = 0
        self.path = Path(path)

    @property
    def end(self):
        return not self.thread.is_alive()

    def start(self):
        self.thread = Thread(target=self.get_size, args=(self.path,))
        self.thread.start()

    def get_size(self, path: Path):
        if path.is_dir():
            for i in path.iterdir():
                self.get_size(i)
        elif path.is_file():
            self.size += path.stat().st_size

    def __eq__(self, other):
        return self.path == other.path


class StreamDelete:
    def __init__(self, path: str, moveToTrash=True):
        self.path = Path(path)
        self.end = False
        self.items = []
        self.total = 0
        self.deleted = 0
        self.moveToTrash = moveToTrash

    def count(self, path):
        if path.is_dir():
            for i in path.iterdir():
                self.count(i)

        self.items.append(path)

    def start(self):
        self.thread = Thread(target=self.delete, args=(self.path,))
        self.thread.start()

    def delete(self, path: Path):
        self.count(path)
        self.total = len(self.items)

        def delete_file(path):
            with suppress(FileNotFoundError):
                path.unlink()
            self.deleted += 1

        def delete_folder(path):
            with suppress(FileNotFoundError):
                path.rmdir()
            self.deleted += 1

        def move_to_trash(path):
            try:
                send2trash(path)
            except OSError as e:
                print(e)
                raise

            self.deleted += 1

        tasks = []
        with ThreadPoolExecutor(max_workers=16) as executor:
            for i in self.items:
                if i.is_file():
                    if self.moveToTrash:
                        tasks.append(executor.submit(move_to_trash, i))
                    else:
                        tasks.append(executor.submit(delete_file, i))

            wait(tasks, return_when=ALL_COMPLETED)

            for i in self.items:
                if i.is_dir():
                    if self.moveToTrash:
                        tasks.append(executor.submit(move_to_trash, i))
                    else:
                        tasks.append(executor.submit(delete_folder, i))

        self.end = True

    def __eq__(self, other):
        return self.path == other.path


class API:
    def close(self):
        w.destroy()
        server_process.kill()
        sys.exit(0)

    def minimize(self):
        w.minimize()

    def maximize(self):
        w.toggle_fullscreen()

    def ls(self, folder: str):
        return [
            ExplorerItem(
                name=i.name,
                path=i.as_posix(),
                kind='folder' if i.is_dir() else 'file',
                modified=datetime.fromtimestamp(
                    i.stat().st_mtime, timezone.utc
                ).strftime('%d/%m/%Y %H:%M'),
                type=get_file_type(i),
                size=0,
                parent=i.parent.as_posix(),
            )
            for i in Path(folder).iterdir()
        ]

    def home(self):
        return Path.home().as_posix()

    def rename(self, path: str, name: str):
        Path(path).rename(Path(path).parent / name)

    def create_file(self, path: str):
        Path(path).touch()

    def create_folder(self, path: str):
        Path(path).mkdir()

    def exists(self, path: str, ignore: str = None):
        p1 = Path(path)
        p2 = Path(ignore) if ignore else None

        return p1.exists() and p1 != p2

    def stream_folder_size(self, path: str):
        s = StreamFolderSize(path)

        if path not in streams_files:
            s.start()
            streams_files[path] = s

        if streams_files[path].end:
            del streams_files[path]

        return {'size': streams_files[path].size, 'end': streams_files[path].end}

    def stream_delete(self, path: str, moveToTrash=True):
        s = StreamDelete(path, moveToTrash)

        if path not in streams_deletes:
            s.start()
            streams_deletes[path] = s

        if streams_deletes[path].end:
            del streams_deletes[path]

        return {
            'end': streams_deletes[path].end,
            'total': streams_deletes[path].total,
            'deleted': streams_deletes[path].deleted,
        }

    def reset_stream_size(self, path: str):
        if path in streams_files:
            del streams_files[path]

    def reset_stream_delete(self, path: str):
        if path in streams_deletes:
            del streams_deletes[path]


streams_files = {}
streams_deletes = {}

UI_FOLDER = Path('ui')
SEED_FOLDER = Path('seed')

server_process = None

if not SEED_FOLDER.exists():
    SEED_FOLDER.mkdir()


def start_server():
    global server_process
    server_process = Popen('cd ui && pnpm dev', shell=True)


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
    Thread(target=start_server).start()

    w = webview.create_window(
        'Explorer', 'http://localhost:3000', js_api=API(), frameless=True
    )

    webview.start(debug=True)
