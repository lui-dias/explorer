import logging
import sys
from asyncio import Future
from asyncio import run as run_async
from collections import deque
from concurrent.futures import ALL_COMPLETED, ThreadPoolExecutor, wait
from contextlib import contextmanager, suppress
from datetime import datetime, timezone
from getpass import getuser
from hashlib import md5, sha1, sha256
from pathlib import Path, PurePath
from shutil import rmtree
from subprocess import run
from threading import Lock, Thread
from time import sleep, time_ns
from typing import Literal, TypedDict
from zlib import crc32

import click as c
import regex as re
import webview
import wmi
from flask import Flask, send_from_directory
from flask_cors import CORS
from fontTools.ttLib import TTFont, TTLibError
from psutil import disk_partitions, disk_usage
from pybase64 import b64encode
from send2trash import send2trash
from toml import dumps as dumps_toml
from toml import load as load_toml
from ujson import dumps, loads
from websockets.legacy.server import WebSocketServerProtocol
from websockets.server import serve

try:
    from rich import print
except ImportError:
    ...


def measure(text):
    def wrapper(fn):
        def inner(*args, **kwargs):
            start = time_ns()
            result = fn(*args, **kwargs)
            end = time_ns()
            print(f'{text} took {(end - start) / 1_000_000} ms')
            return result

        return inner

    return wrapper


@contextmanager
def with_measure(text):
    start = time_ns()
    yield
    end = time_ns()
    print(f'{text} took {(end - start) / 1_000_000} ms')


class ExplorerItem(TypedDict):
    name: str
    path: str
    kind: Literal['file', 'folder']
    modified: str
    accessed: str
    created: str
    type: str
    size: str
    parent: str


class Disk(TypedDict):
    name: str
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
    p = Path(path)
    stat = p.stat()

    return ExplorerItem(
        name=p.name,
        path=p.as_posix(),
        kind='folder' if p.is_dir() else 'file',
        modified=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        accessed=datetime.fromtimestamp(stat.st_atime, timezone.utc).isoformat(),
        created=datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
        type=get_file_type(p),
        size=0,
        parent=p.parent.as_posix(),
    )


file_type_cache = {}


def get_file_type(path: Path):
    name = path.name

    if name in file_type_cache:
        return file_type_cache[name]

    n = ''

    if path.is_dir():
        if any(name.endswith(i.lower()) for i in ['.vscode', 'vscode']):
            n = 'FolderVscode'

        elif any(name.endswith(i.lower()) for i in ['node_modules']):
            n = 'FolderNode Modules'

        elif any(name.endswith(i.lower()) for i in ['public', '.public']):
            n = 'FolderPublic'

        elif any(name.endswith(i.lower()) for i in ['src', 'source', 'sources']):
            n = 'FolderSrc'

        elif any(
            name.endswith(i.lower())
            for i in ['component', 'components', '.components', 'gui', 'ui', 'widgets']
        ):
            n = 'FolderComponent'

        elif any(
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
            n = 'FolderView'

        elif any(
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
            n = 'FolderDist'

        elif any(
            name.endswith(i.lower())
            for i in ['assets', '.assets', 'asset', '.asset', 'static']
        ):
            n = 'FolderAssets'

        elif any(
            name.endswith(i.lower())
            for i in ['git', '.git', 'submodules', '.submodules']
        ):
            n = 'FolderGit'

        elif any(
            name.endswith(i.lower())
            for i in ['cli', 'cmd', 'command', 'commands', 'commandline', 'console']
        ):
            n = 'FolderCLI'

        elif any(name.endswith(i.lower()) for i in ['.github']):
            n = 'FolderGithub'

        elif any(
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
            n = 'FolderTest'

        elif any(name.endswith(i.lower()) for i in ['docs', '.docs', 'doc', '.doc']):
            n = 'FolderDocs'

        elif any(name.endswith(i.lower()) for i in ['.next']):
            n = 'FolderNext'
        else:
            n = 'Folder'
    elif path.is_file():
        if any(name.endswith(i.lower()) for i in ['.py']):
            n = 'FilePython'

        elif any(name.endswith(i.lower()) for i in ['.prettierrc', '.prettierignore']):
            n = 'FilePrettier'

        elif any(
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
            n = 'FileTsconfig'

        elif any(
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
            n = 'FileGit'

        elif any(name.endswith(i.lower()) for i in ['.markdown', '.md', '.mdown']):
            n = 'FileMarkdown'

        elif any(name.endswith(i.lower()) for i in ['.toml']):
            n = 'FileToml'

        elif any(name.endswith(i.lower()) for i in ['.astro']):
            n = 'FileAstro'

        elif any(
            name.endswith(i.lower())
            for i in [
                'astro.config.js',
                'astro.config.cjs',
                'astro.config.mjs',
                'astro.config.ts',
            ]
        ):
            n = 'FileAstro Config'

        elif any(
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
            n = 'FileTailwind'

        elif any(name.endswith(i.lower()) for i in ['.d.ts', '.d.cts', '.d.mts']):
            n = 'FileTypescript Definition'

        elif any(name.endswith(i.lower()) for i in ['.db']):
            n = 'FileDatabase'

        elif any(name.endswith(i.lower()) for i in ['.svg']):
            n = 'FileSVG'

        elif any(name.endswith(i.lower()) for i in ['.html']):
            n = 'FileHTML'

        elif any(name.endswith(i.lower()) for i in ['.css']):
            n = 'FileCSS'

        elif any(
            name.endswith(i.lower())
            for i in ['.woff', '.woff2', '.ttf', '.otf', '.eot', '.pfa', '.pfb', '.sfd']
        ):
            n = 'FileFont'

        elif any(name.endswith(i.lower()) for i in ['.csv', '.tsv', '.txt']):
            n = 'FileText'

        elif any(name.endswith(i.lower()) for i in ['.plist', '.properties', '.env']):
            n = 'FileConfig'

        elif any(
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
            n = 'FileYarn'

        elif any(
            name.endswith(i.lower())
            for i in ['pnpmfile.js', 'pnpm-lock.yaml', 'pnpm-workspace.yaml']
        ):
            n = 'FilePNPM'

        elif any(name.endswith(i.lower()) for i in ['.pdf']):
            n = 'FilePDF'

        elif any(
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
            n = 'FileDocker'

        elif any(
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
            n = 'FileLicense'

        elif any(name.endswith(i.lower()) for i in ['.rst']):
            n = 'FileRst'

        elif any(
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
            n = 'FileImage'

        elif any(
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
            n = 'FileESLint'

        elif any(
            name.endswith(i.lower())
            for i in [
                '.npmignore',
                '.npmrc',
                'package.json',
                'package-lock.json',
                'npm-shrinkwrap.json',
            ]
        ):
            n = 'FileNPM'

        elif any(
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
            n = 'FilePostCSSConfig'

        elif any(
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
            n = 'FileZip'

        elif any(
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
            n = 'FileVideo'

        # ! --------------------------------------------
        # ! KEEP ALWAYS AT THE END
        # ! --------------------------------------------

        elif any(
            name.endswith(i.lower())
            for i in ['.json', '.jsonl', '.ndjson', '.json-tmlanguage', '.jsonc']
        ):
            n = 'FileJson'

        elif any(name.endswith(i.lower()) for i in ['.js']):
            n = 'FileJavascript'

        elif any(name.endswith(i.lower()) for i in ['.ts']):
            n = 'FileTypescript'

        elif any(
            name.endswith(i.lower()) for i in ['.yaml', '.yml', '.yaml-tmlanguage']
        ):
            n = 'FileYaml'

        elif any(
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
            n = 'FileBinary'
        else:
            n = 'File'
    else:
        n = 'unknown'

    file_type_cache[name] = n

    return n


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
        def get(path: Path):
            self.items.append(get_path_info(path.as_posix()))
            self.total += 1

            while self.paused:
                sleep(0.001)

        with ThreadPoolExecutor(max_workers=4) as executor:
            for i in self.path.iterdir():
                executor.submit(get, i)

        self.end = True

    def __eq__(self, other):
        return self.path == other.path


class API:
    def close(self):
        w.destroy()
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
    
    def start_find(self, path: str, query: str):
        s = StreamFind(path, query)
        s.start()
        streams_finds[path] = s


    def stream_find(self, path: str, query: str):
        if path not in streams_finds:
            return

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
            for i in streams_finds.values():
                print(i.end)

            sleep(0.001)

    def stop_all_streams_ls(self):
        for i in streams_ls.values():
            i.end = True

        while streams_ls:
            sleep(0.001)

    def delete_all_streams_ls(self):
        streams_ls.clear()

    def delete_all_streams_find(self):
        streams_finds.clear()

    def get_config(self):
        return load_toml(CONFIG_FILE)

    def set_config(self, config: dict):
        CONFIG_FILE.write_text(dumps_toml(config))

    def read(self, path: str):
        return Path(path).read_text()

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
        c = wmi.WMI()

        disks: list[Disk] = []

        for i in disk_partitions():
            d = next(
                d for d in c.Win32_LogicalDisk() if i.mountpoint.startswith(d.Caption)
            )
            usage = disk_usage(i.mountpoint)

            disks.append(
                {
                    'name': d.VolumeName or DRIVE_TYPES[d.DriveType],
                    'device': DRIVE_TYPES[d.DriveType],
                    'path': d.Caption,
                    'free': usage.free,
                    'total': usage.total,
                    'used': usage.used,
                    'percent': usage.percent,
                }
            )

        return disks

    def get(self, k: str):
        with local_store_lock:
            d = loads(LOCAL_STORAGE.read_text())

            return d.get(k)

    def set(self, k: str, v):
        with local_store_lock:
            d = loads(LOCAL_STORAGE.read_text())

            d[k] = v

            LOCAL_STORAGE.write_text(dumps(dict(sorted(d.items())), indent=4))

    def get_font_weight(self, path: str):
        try:
            return TTFont(path)['OS/2'].usWeightClass
        except TTLibError:
            return

    def copy(self, path: str):
        run(f'fileclip.exe {path}')

    def paste(self, folder: str):
        run(f'cd {folder} && fileclip.exe -v', shell=True)

    def get_crc32(self, path: str):
        with open(path, 'rb') as f:
            h = 0
            while True:
                data = f.read(65536)
                if not data:
                    break
                h = crc32(data, h)

            h = h & 0xFFFFFFFF

        return f'{h:08x}'

    def get_md5(self, path: str):
        with open(path, 'rb') as f:
            h = md5()

            while True:
                data = f.read(65536)
                if not data:
                    break
                h.update(data)

        return h.hexdigest()

    def get_sha1(self, path: str):
        with open(path, 'rb') as f:
            h = sha1()

            while True:
                data = f.read(65536)
                if not data:
                    break
                h.update(data)

        return h.hexdigest()

    def get_sha256(self, path: str):
        with open(path, 'rb') as f:
            h = sha256()

            while True:
                data = f.read(65536)
                if not data:
                    break
                h.update(data)

        return h.hexdigest()


streams_files = {}
streams_deletes = {}
streams_finds = {}
streams_ls = {}

DRIVE_TYPES = {
    0: "Unknown",
    1: "No Root Directory",
    2: "Removable Disk",
    3: "Local Disk",
    4: "Network Drive",
    5: "Compact Disc",
    6: "RAM Disk",
}

w = None

UI_FOLDER = Path('ui')
SEED_FOLDER = Path('seed')
CONFIG_FILE = Path('config.toml')
LOCAL_STORAGE = Path('localstorage.json')

local_store_lock = Lock()

if not LOCAL_STORAGE.exists() or LOCAL_STORAGE.stat().st_size == 0:
    LOCAL_STORAGE.write_text('{}')

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
    run('cd ui && pnpm dev', shell=True)


def show_ui():
    run('python main.py', shell=True)


def start(debug=True, server=True):
    global w

    if server:
        Thread(target=start_server).start()

    app = Flask(__name__)
    CORS(app)

    # Disable flask logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    c.echo = lambda *args, **kwargs: None
    c.secho = lambda *args, **kwargs: None

    @app.route('/stream/<path:path>')
    def _(path):
        path = Path(path)

        return send_from_directory(path.parent, path.name, conditional=True)

    w = webview.create_window(
        'Explorer',
        'http://localhost:3000',
        frameless=True,
        easy_drag=False,
        width=1280,
        height=600,
    )

    def ws_server():
        async def server(ws: WebSocketServerProtocol):
            while True:
                data = loads(await ws.recv())

                if data['type'] == 'call':
                    id = data['id']
                    name = data['name']
                    args = data['args']

                    with suppress(Exception):
                        r = getattr(api, name)(*args)

                    await ws.send(dumps({'type': 'return', 'id': id, 'r': r}))

        async def main():
            async with serve(server, 'localhost', 3004):
                await Future()

        api = API()
        run_async(main())

    Thread(target=app.run, args=('localhost', 3003)).start()
    webview.start(ws_server, debug=debug, private_mode=False)


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
