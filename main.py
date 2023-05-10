from time import sleep
import regex as re
import sys
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
from contextlib import suppress
from datetime import datetime, timezone
from pathlib import Path, PurePath
from subprocess import Popen, run
from threading import Thread, Lock
from collections import deque
from typing import Literal, TypedDict
from getpass import getuser
from shutil import rmtree
from ujson import loads, dumps

import webview
from send2trash import send2trash
from toml import load as load_toml, dumps as dumps_toml
from pybase64 import b64encode
from flask import Flask, send_from_directory
from flask_cors import CORS
from psutil import disk_partitions, disk_usage
from fontTools.ttLib import TTFont, TTLibError

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

class Disk(TypedDict):
    device: str
    path: str
    total: int
    used: int
    free: int
    percent: float

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
            return 'FolderVscode'

        if any(name.endswith(i.lower()) for i in ['node_modules']):
            return 'FolderNode Modules'

        if any(name.endswith(i.lower()) for i in ['public', '.public']):
            return 'FolderPublic'

        if any(name.endswith(i.lower()) for i in ['src', 'source', 'sources']):
            return 'FolderSrc'

        if any(
            name.endswith(i.lower())
            for i in ['component', 'components', '.components', 'gui', 'ui', 'widgets']
        ):
            return 'FolderComponent'

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
            return 'FolderView'

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
            return 'FolderDist'

        if any(
            name.endswith(i.lower())
            for i in ['assets', '.assets', 'asset', '.asset', 'static']
        ):
            return 'FolderAssets'

        if any(
            name.endswith(i.lower())
            for i in ['git', '.git', 'submodules', '.submodules']
        ):
            return 'FolderGit'

        if any(
            name.endswith(i.lower())
            for i in ['cli', 'cmd', 'command', 'commands', 'commandline', 'console']
        ):
            return 'FolderCLI'

        if any(name.endswith(i.lower()) for i in ['.github']):
            return 'FolderGithub'

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
            return 'FolderTest'

        if any(name.endswith(i.lower()) for i in ['docs', '.docs', 'doc', '.doc']):
            return 'FolderDocs'

        if any(name.endswith(i.lower()) for i in ['.next']):
            return 'FolderNext'

        return 'Folder'
    elif path.is_file():
        if any(name.endswith(i.lower()) for i in ['.py']):
            return 'FilePython'

        if any(name.endswith(i.lower()) for i in ['.prettierrc', '.prettierignore']):
            return 'FilePrettier'

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
            return 'FileTsconfig'

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
            return 'FileGit'

        if any(name.endswith(i.lower()) for i in ['.markdown', '.md', '.mdown']):
            return 'FileMarkdown'

        if any(name.endswith(i.lower()) for i in ['.toml']):
            return 'FileToml'

        if any(name.endswith(i.lower()) for i in ['.astro']):
            return 'FileAstro'

        if any(
            name.endswith(i.lower())
            for i in [
                'astro.config.js',
                'astro.config.cjs',
                'astro.config.mjs',
                'astro.config.ts',
            ]
        ):
            return 'FileAstro Config'

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
            return 'FileTailwind'

        if any(name.endswith(i.lower()) for i in ['.d.ts', '.d.cts', '.d.mts']):
            return 'FileTypescript Definition'

        if any(name.endswith(i.lower()) for i in ['.db']):
            return 'FileDatabase'

        if any(name.endswith(i.lower()) for i in ['.svg']):
            return 'FileSVG'

        if any(name.endswith(i.lower()) for i in ['.html']):
            return 'FileHTML'

        if any(name.endswith(i.lower()) for i in ['.css']):
            return 'FileCSS'

        if any(
            name.endswith(i.lower())
            for i in ['.woff', '.woff2', '.ttf', '.otf', '.eot', '.pfa', '.pfb', '.sfd']
        ):
            return 'FileFont'

        if any(name.endswith(i.lower()) for i in ['.csv', '.tsv', '.txt']):
            return 'FileText'

        if any(name.endswith(i.lower()) for i in ['.plist', '.properties', '.env']):
            return 'FileConfig'

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
            return 'FileYarn'

        if any(
            name.endswith(i.lower())
            for i in ['pnpmfile.js', 'pnpm-lock.yaml', 'pnpm-workspace.yaml']
        ):
            return 'FilePNPM'

        if any(name.endswith(i.lower()) for i in ['.pdf']):
            return 'FilePDF'

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
            return 'FileDocker'

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
            return 'FileLicense'

        if any(name.endswith(i.lower()) for i in ['.rst']):
            return 'FileRst'

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
            return 'FileImage'

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
            return 'FileESLint'

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
            return 'FileNPM'

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
            return 'FilePostCSSConfig'

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
            return 'FileZip'

        if any(
            name.endswith(i.lower())
            for i in [
                '3g2',
                '3gp',
                'asf',
                'amv',
                'avi',
                'divx',
                'qt',
                'f4a',
                'f4b',
                'f4p',
                'f4v',
                'flv',
                'm2v',
                'm4v',
                'mkv',
                'mk3d',
                'mov',
                'mp2',
                'mp4',
                'mpe',
                'mpeg',
                'mpeg2',
                'mpg',
                'mpv',
                'nsv',
                'ogv',
                'rm',
                'rmvb',
                'svi',
                'vob',
                'webm',
                'wmv',
            ]
        ):
            return 'FileVideo'

        # ! --------------------------------------------
        # ! KEEP ALWAYS AT THE END
        # ! --------------------------------------------

        if any(
            name.endswith(i.lower())
            for i in ['.json', '.jsonl', '.ndjson', '.json-tmlanguage', '.jsonc']
        ):
            return 'FileJson'

        if any(name.endswith(i.lower()) for i in ['.js']):
            return 'FileJavascript'

        if any(name.endswith(i.lower()) for i in ['.ts']):
            return 'FileTypescript'

        if any(name.endswith(i.lower()) for i in ['.yaml', '.yml', '.yaml-tmlanguage']):
            return 'FileYaml'

        if any(
            name.endswith(i.lower())
            for i in [
                '.a',
                '.app',
                '.bin',
                '.cmo',
                '.cmx',
                '.cma',
                '.cmxa',
                '.cmi',
                '.dll',
                '.exe',
                '.hl',
                '.ilk',
                '.lib',
                '.n',
                '.ndll',
                '.o',
                '.obj',
                '.pyc',
                '.pyd',
                '.pyo',
                '.pdb',
                '.scpt',
                '.scptd',
                '.so',
            ]
        ):
            return 'FileBinary'

        return 'File'
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
        self.paused = False

    def start(self):
        self.thread = Thread(target=self.ls)
        self.thread.start()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def ls(self):
        for i in self.path.iterdir():
            if i.exists():
                self.items.append(get_path_info(i.as_posix()))
                self.total += 1

            while self.paused:
                sleep(0.001)

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

    def start_ls(self, folder: str):
        s = StreamLs(folder)
        s.start()
        streams_ls[folder] = s

    def ls(self, folder: str):
        streams_ls[folder].pause()

        # Need copy items, else items is passed by reference and will be empty after clear
        r = {'items': [*streams_ls[folder].items], 'end': streams_ls[folder].end}
        streams_ls[folder].items.clear()

        streams_ls[folder].resume()

        if streams_ls[folder].end:
            del streams_ls[folder]

        return r

    def home(self):
        return Path.home().as_posix()

    def rename(self, path: str, name: str):
        Path(path).rename(Path(path).parent / name)

    def createFile(self, path: str):
        Path(path).touch()

    def createFolder(self, path: str):
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

        streams_finds[path].items = []

        if streams_finds[path].end:
            del streams_finds[path]

        return r

    def stop_all_streams_file_size(self):
        for i in streams_files.values():
            i.end = True

        while streams_files:
            sleep(0.001)

    def stop_all_streams_find(self):
        for i in streams_finds.values():
            i.end = True

        while streams_finds:
            sleep(0.001)

    def stopAllStreamsLs(self):
        for i in streams_ls.values():
            i.end = True

        while streams_ls:
            sleep(0.001)

    def deleteAllStreamsLs(self):
        streams_ls.clear()

    def get_config(self):
        return load_toml(CONFIG_FILE)

    def set_config(self, config: dict):
        CONFIG_FILE.write_text(dumps_toml(config))

    def read(self, path: str):
        return b64encode(Path(path).read_bytes()).decode()

    def user(self):
        return getuser()

    def pwd(self):
        return Path('.').absolute().as_posix()

    def setup_tests(self):
        tests = Path('__tests')

        if tests.exists():
            rmtree(tests)

        tests.mkdir()

        for i in range(1000):
            tests.joinpath(f'{i}').touch()

        tests.joinpath('test.txt').touch()
        tests.joinpath('foo.py').touch()
        tests.joinpath('bar.py').touch()

    def clear_tests(self):
        rmtree('__tests')

    def disks_info(self):
        disks: list[Disk] = []

        for i in disk_partitions():
            usage = disk_usage(i.mountpoint)

            disks.append({
                'device': i.device.replace('\\', '/'),
                'path': i.mountpoint.replace('\\', '/'),
                'free': usage.free,
                'total': usage.total,
                'used': usage.used,
                'percent': usage.percent
            })

        return disks
    
    def get(self, k: str):
        with local_store_lock:
            d = loads(LOCALSTORAGE.read_text())

            return d.get(k)
    
    def set(self, k: str, v):
        with local_store_lock:
            d = loads(LOCALSTORAGE.read_text())

            d[k] = v

            LOCALSTORAGE.write_text(dumps(d))

    def get_font_weight(self, path: str):
        try:
            return TTFont(path)['OS/2'].usWeightClass
        except TTLibError:
            return


streams_files = {}
streams_deletes = {}
streams_finds = {}
streams_ls = {}

w = None

UI_FOLDER = Path('ui')
SEED_FOLDER = Path('seed')
CONFIG_FILE = Path('config.toml')
LOCALSTORAGE = Path('localstorage.json')

local_store_lock = Lock()

if not LOCALSTORAGE.exists() or LOCALSTORAGE.stat().st_size == 0:
    LOCALSTORAGE.write_text('{}')

server_process = None

if not SEED_FOLDER.exists():
    SEED_FOLDER.mkdir()

if not CONFIG_FILE.exists():
    CONFIG_FILE.write_text(
        dumps_toml(
            {
                'colors': {
                    'primary': '#fecaca',
                    'accent': '#dc2626',
                    'text': '#fee2e2',
                    'background': '#27272a',
                    'divider': '#4b5563',
                }
            }
        )
    )


def start_server():
    global server_process
    server_process = Popen('cd ui && pnpm dev', shell=True)


def show_ui():
    run('python main.py', shell=True)

def start(debug=True, server=True):
    global w

    if server:
        Thread(target=start_server).start()

    app = Flask(__name__)
    CORS(app)

    w = webview.create_window(
        'Explorer',
        'http://localhost:3000',
        js_api=API(),
        frameless=True,
        width=1280,
        height=600,
    )

    @app.route('/stream/<path:path>')
    def _(path):
        path = Path(path)

        return send_from_directory(path.parent, path.name, conditional=True)

    Thread(target=app.run, args=('localhost', 3003)).start()
    webview.start(debug=debug)



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

    if command == 'release':
        run('cd ui && npm run build', shell=True)
        Thread(target=lambda: run('cd ui && npm run preview', shell=True)).start()

        start(debug=False, server=False)

elif __name__ == '__main__':
    start()