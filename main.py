import regex as re
import sys
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path, PurePath
from subprocess import Popen, run
from threading import Thread
from collections import deque
from typing import Literal, TypedDict

import webview
from send2trash import send2trash
from toml import load as load_toml, dumps as dumps_toml

try:
    from rich import print
except ImportError:
    ...


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


def get_path_info(path: str):
    path = Path(path)
    return ExplorerItem(
        name=path.name,
        path=path.as_posix(),
        kind='folder' if path.is_dir() else 'file',
        modified=datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime(
            '%d/%m/%Y %H:%M'
        ),
        type=get_file_type(path),
        size=0,
        parent=path.parent.as_posix(),
    )


def get_file_type(path: Path):
    name = path.name

    if path.is_dir():
        if any(name.endswith(i.lower()) for i in ['.vscode', 'vscode']):
            return 'Vscode'

        if any(name.endswith(i.lower()) for i in ['node_modules']):
            return 'Node Modules'

        if any(name.endswith(i.lower()) for i in ['public', '.public']):
            return 'Public'

        if any(name.endswith(i.lower()) for i in ['src', 'source', 'sources']):
            return 'Src'

        if any(
            name.endswith(i.lower())
            for i in ['component', 'components', '.components', 'gui', 'ui', 'widgets']
        ):
            return 'Component'

        if any(
            name.endswith(i.lower())
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
            name.endswith(i.lower())
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
            name.endswith(i.lower()) for i in ['assets', '.assets', 'asset', '.asset', 'static']
        ):
            return 'Assets'

        if any(name.endswith(i.lower()) for i in ['git', '.git', 'submodules', '.submodules']):
            return 'Git'

        if any(
            name.endswith(i.lower())
            for i in ['cli', 'cmd', 'command', 'commands', 'commandline', 'console']
        ):
            return 'CLI'

        if any(name.endswith(i.lower()) for i in ['.github']):
            return 'Github'

        if any(
            name.endswith(i.lower())
            for i in [
                'tests',
                '.tests',
                'test',
                '.test',
                '__tests__',
                '__test__',
                'spec',
                '.spec',
                'specs',
                '.specs',
                'integration',
            ]
        ):
            return 'Test'

        if any(name.endswith(i.lower()) for i in ['docs', '.docs', 'doc', '.doc']):
            return 'Docs'

        if any(name.endswith(i.lower()) for i in ['.next']):
            return 'Next'

        return 'folder'
    elif path.is_file():
        if any(name.endswith(i.lower()) for i in ['.py']):
            return 'Python'

        if any(name.endswith(i.lower()) for i in ['.prettierrc', '.prettierignore']):
            return 'Prettier'

        if any(
            name.endswith(i.lower())
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
            name.endswith(i.lower())
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

        if any(name.endswith(i.lower()) for i in ['.markdown', '.md', '.mdown']):
            return 'Markdown'

        if any(name.endswith(i.lower()) for i in ['.toml']):
            return 'Toml'

        if any(name.endswith(i.lower()) for i in ['.astro']):
            return 'Astro'

        if any(
            name.endswith(i.lower())
            for i in [
                'astro.config.js',
                'astro.config.cjs',
                'astro.config.mjs',
                'astro.config.ts',
            ]
        ):
            return 'Astro Config'

        if any(
            name.endswith(i.lower())
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

        if any(name.endswith(i.lower()) for i in ['.d.ts', '.d.cts', '.d.mts']):
            return 'Typescript Definition'

        if any(name.endswith(i.lower()) for i in ['.db']):
            return 'Database'

        if any(name.endswith(i.lower()) for i in ['.svg']):
            return 'SVG'

        if any(name.endswith(i.lower()) for i in ['.html']):
            return 'HTML'

        if any(name.endswith(i.lower()) for i in ['.css']):
            return 'CSS'

        if any(
            name.endswith(i.lower())
            for i in ['.woff', '.woff2', '.ttf', '.otf', '.eot', '.pfa', '.pfb', '.sfd']
        ):
            return 'Font'

        if any(name.endswith(i.lower()) for i in ['.csv', '.tsv', '.txt']):
            return 'Text'

        if any(name.endswith(i.lower()) for i in ['.plist', '.properties', '.env']):
            return 'Config'

        if any(
            name.endswith(i.lower())
            for i in [
                'yarn.lock',
                '.yarnrc',
                '.yarnrc.yml',
                '.yarnclean',
                '.yarn-integrity',
                '.yarn-metadata.json',
                '.yarnignore',
            ]
        ):
            return 'Yarn'

        if any(
            name.endswith(i.lower())
            for i in ['pnpmfile.js', 'pnpm-lock.yaml', 'pnpm-workspace.yaml']
        ):
            return 'PNPM'

        if any(name.endswith(i.lower()) for i in ['.pdf']):
            return 'PDF'

        if any(
            name.endswith(i.lower())
            for i in [
                '.dockerignore',
                'compose.yaml',
                'compose.yml',
                'docker-compose.yaml',
                'docker-compose.yml',
                'docker-compose.ci-build.yaml',
                'docker-compose.ci-build.yml',
                'docker-compose.override.yaml',
                'docker-compose.override.yml',
                'docker-compose.vs.debug.yaml',
                'docker-compose.vs.debug.yml',
                'docker-compose.vs.release.yaml',
                'docker-compose.vs.release.yml',
                'docker-cloud.yaml',
                'docker-cloud.yml',
                'Dockerfile',
            ]
        ):
            return 'Docker'

        if any(
            name.endswith(i.lower())
            for i in [
                'LICENSE',
                'enc',
                'lic',
                'license_dark',
                'license',
                'licence',
                'copying',
                'copying.lesser',
                'license-mit',
                'license-apache',
                'license.md',
                'license.txt',
                'licence.md',
                'licence.txt',
                'copying.md',
                'copying.txt',
                'copying.lesser.md',
                'copying.lesser.txt',
                'license-mit.md',
                'license-mit.txt',
                'license-apache.md',
                'license-apache.txt',
            ]
        ):
            return 'License'

        if any(name.endswith(i.lower()) for i in ['.rst']):
            return 'Rst'

        if any(
            name.endswith(i.lower())
            for i in [
                '.jpeg',
                '.jpg',
                '.gif',
                '.png',
                '.bmp',
                '.tiff',
                '.ico',
                '.webp',
            ]
        ):
            return 'Image'

        if any(
            name.endswith(i.lower())
            for i in [
                '.eslintrc',
                '.eslintignore',
                '.eslintcache',
                '.eslintrc.js',
                '.eslintrc.mjs',
                '.eslintrc.cjs',
                '.eslintrc.json',
                '.eslintrc.yaml',
                '.eslintrc.yml',
            ]
        ):
            return 'ESLint'

        if any(
            name.endswith(i.lower())
            for i in [
                '.npmignore',
                '.npmrc',
                'package.json',
                'package-lock.json',
                'npm-shrinkwrap.json',
            ]
        ):
            return 'NPM'

        if any(
            name.endswith(i.lower())
            for i in [
                '.postcssrc',
                '.postcssrc.json',
                '.postcssrc.yaml',
                '.postcssrc.yml',
                '.postcssrc.ts',
                '.postcssrc.js',
                '.postcssrc.cjs',
                'postcss.config.ts',
                'postcss.config.js',
                'postcss.config.cjs',
            ]
        ):
            return 'PostCSSConfig'

        if any(
            name.endswith(i.lower())
            for i in [
                '.zip',
                '.rar',
                '.7z',
                '.tar',
                '.tgz',
                '.bz',
                '.gz',
                '.bzip2',
                '.xz',
                '.bz2',
                '.zipx',
            ]
        ):
            return 'Zip'

        # ! --------------------------------------------
        # ! KEEP ALWAYS AT THE END
        # ! --------------------------------------------

        if any(
            name.endswith(i.lower())
            for i in ['.json', '.jsonl', '.ndjson', '.json-tmlanguage', '.jsonc']
        ):
            return 'Json'

        if any(name.endswith(i.lower()) for i in ['.js']):
            return 'Javascript'

        if any(name.endswith(i.lower()) for i in ['.ts']):
            return 'Typescript'

        if any(name.endswith(i.lower()) for i in ['.yaml', '.yml', '.yaml-tmlanguage']):
            return 'Yaml'

        if any(
            name.endswith(i.lower())
            for i in [
                'a',
                'app',
                'bin',
                'cmo',
                'cmx',
                'cma',
                'cmxa',
                'cmi',
                'dll',
                'exe',
                'hl',
                'ilk',
                'lib',
                'n',
                'ndll',
                'o',
                'obj',
                'pyc',
                'pyd',
                'pyo',
                'pdb',
                'scpt',
                'scptd',
                'so',
            ]
        ):
            return 'Binary'

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
    def __init__(self, id: str, path: str | list[str], moveToTrash=True):
        self.id = id
        self.paths = path
        self.end = False
        self.items = []
        self.total = 0
        self.deleted = 0
        self.moveToTrash = moveToTrash
        self.last_deleted = None

    def count(self, path):
        if path.is_dir():
            for i in path.iterdir():
                self.count(i)

        self.items.append(path)

    def start(self):
        self.thread = Thread(target=self.delete)
        self.thread.start()

    def delete(self):
        for path in self.paths:
            self.count(Path(path))
        self.total = len(self.items)

        def delete_file(path):
            with suppress(FileNotFoundError):
                path.unlink()
            self.deleted += 1
            self.last_deleted = path.as_posix()

        def delete_folder(path):
            with suppress(FileNotFoundError):
                path.rmdir()
            self.deleted += 1
            self.last_deleted = path.as_posix()

        def move_to_trash(path):
            try:
                send2trash(path)
            except OSError as e:
                print(e)
                raise

            self.deleted += 1
            self.last_deleted = path.as_posix()

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


class StreamFind:
    def __init__(self, path: str, query: str):
        self.path = Path(path)
        self.query = query
        self.end = False
        self.items = []
        self.total = 0
        self.regex = self.create_regex(query)

    def start(self):
        self.thread = Thread(target=self.find)
        self.thread.start()

    def create_regex(self, search: str):
        flags = {
            'i': re.I,
            'm': re.M,
            's': re.S,
            'x': re.X,
            'a': re.A,
            'u': re.U,
            'l': re.L,
        }
        is_regex = re.search(r'\/(?<regex>.+)\/(?<flags>.*)', search)

        if is_regex:
            parsed_flags = 0

            for i in is_regex.group('flags'):
                parsed_flags |= flags.get(i, 0)

            return re.compile(is_regex.group('regex'), parsed_flags)

        return re.compile(re.escape(search), re.I)

    def find(self):
        paths = deque([self.path])

        while paths:
            path = paths.popleft()

            for i in path.iterdir():
                if i.is_dir():
                    paths.append(i)

                if self.regex.search(i.name) or PurePath(i.name).match(self.query):
                    self.items.append(get_path_info(i.as_posix()))

                self.total += 1

        self.end = True

    def __eq__(self, other):
        return self.path == other.path

class StreamLs:
    def __init__(self, path: str):
        self.path = Path(path)
        self.end = False
        self.items = []
        self.total = 0

    def start(self):
        self.thread = Thread(target=self.ls)
        self.thread.start()

    def ls(self):
        for i in self.path.iterdir():
            if i.exists():
                self.items.append(get_path_info(i.as_posix()))
                self.total += 1

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

    def get_path_info(self, path: str):
        return get_path_info(path)

    def ls(self, folder: str):
        s = StreamLs(folder)
        
        if folder not in streams_ls:
            s.start()
            streams_ls[folder] = s

        r = {'items': streams_ls[folder].items, 'end': streams_ls[folder].end}

        if streams_ls[folder].end:
            del streams_ls[folder]

        return r

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

    def stream_folder_size(self, path: str | list[str]):
        s = StreamFolderSize(path)

        if path not in streams_files:
            s.start()
            streams_files[path] = s

        r = {'size': streams_files[path].size, 'end': streams_files[path].end}

        if streams_files[path].end:
            del streams_files[path]

        return r

    def stream_delete(self, id: str, path: str, moveToTrash=True):
        s = StreamDelete(id, path, moveToTrash)

        if s.id not in streams_deletes:
            s.start()
            streams_deletes[s.id] = s

        r = {
            'end': streams_deletes[s.id].end,
            'total': streams_deletes[s.id].total,
            'deleted': streams_deletes[s.id].deleted,
            'last_deleted': streams_deletes[s.id].last_deleted,
        }

        if streams_deletes[s.id].end:
            del streams_deletes[s.id]

        return r

    def stream_find(self, path: str, query: str):
        s = StreamFind(path, query)

        if path not in streams_finds:
            s.start()
            streams_finds[path] = s

        r = {
            'end': streams_finds[path].end,
            'total': streams_finds[path].total,
            'files': streams_finds[path].items,
        }

        if streams_finds[path].end:
            del streams_finds[path]

        return r

    def stop_stream_delete(self, id: str):
        if id in streams_deletes:
            streams_deletes[id].end = True

    def stop_stream_file_size(self, path: str):
        if path in streams_files:
            streams_files[path].end = True

    def stop_stream_find(self, path: str):
        if path in streams_finds:
            streams_finds[path].end = True

    def stop_all_streams_delete(self):
        for i in streams_deletes.values():
            i.end = True

    def stop_all_streams_file_size(self):
        for i in streams_files.values():
            i.end = True

    def stop_all_streams_find(self):
        for i in streams_finds.values():
            i.end = True

    def stop_all_streams_ls(self):
        for i in streams_ls.values():
            i.end = True

    def get_config(self):
        return load_toml(CONFIG_FILE)
    
    def set_config(self, config: dict):
        CONFIG_FILE.write_text(dumps_toml(config))


streams_files = {}
streams_deletes = {}
streams_finds = {}
streams_ls = {}

UI_FOLDER = Path('ui')
SEED_FOLDER = Path('seed')
CONFIG_FILE = Path('config.toml')

server_process = None

if not SEED_FOLDER.exists():
    SEED_FOLDER.mkdir()

if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text(dumps_toml({
        'colors': {
            'primary': '#fecaca',
            'accent': '#dc2626',
            'text': '#fee2e2',
            'background': '#27272a',
            'divider': '#4b5563'
        }
    }))


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
                f.write('a'.encode('utf-8') * size)

        with ThreadPoolExecutor(max_workers=16) as executor:
            for i in range(quantity):
                executor.submit(seed, i)

else:
    Thread(target=start_server).start()

    w = webview.create_window(
        'Explorer', 'http://localhost:3000', js_api=API(), frameless=True
    )

    webview.start(debug=True)
