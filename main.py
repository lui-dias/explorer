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
from traceback import print_exc
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
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
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

# fmt: off
folders = {
    'folders/android'       : ('android',),
    'folders/api'           : ('api', 'apis'),
    'folders/app'           : ('app',),
    'folders/arangodb'      : ('arangodb', 'arango'),
    'folders/asset'         : ('assets',),
    'folders/aurelia'       : ('aurelia_project',),
    'folders/audio'         : ('audio', 'audios', 'sound', 'sounds'),
    'folders/aws'           : ('aws',),
    'folders/azure'         : ('azure',),
    'folders/azurepipelines': ('azure-pipelines',),
    'folders/binary'        : ('bin',),
    'folders/bloc'          : ('bloc', 'blocs'),
    'folders/blueprint'     : ('blueprint', 'blueprints'),
    'folders/bower'         : ('bower_components',),
    'folders/buildkite'     : ('buildkite',),
    'folders/cake'          : ('cake',),
    'folders/certificate'   : ('certificates', 'certs'),
    'folders/chef'          : ('chef',),
    'folders/circleci'      : ('circleci',),
    'folders/controller'    : ('controller', 'controllers', 'handlers'),
    'folders/component'     : ('component', 'components', 'gui', 'ui', 'widgets'),
    'folders/composer'      : ('composer',),
    'folders/cli'           : ('cli', 'cmd', 'command', 'commands', 'commandline', 'console'),
    'folders/client'        : ('client', 'clients'),
    'folders/cmake'         : ('cmake',),
    'folders/config'        : (
        'conf',
        'config',
        'configs',
        'configuration',
        'configurations',
        'setting',
        'settings',
        'ini',
        'initializers',
    ),
    'folders/coverage': ('coverage',),
    'folders/css'     : ('css', '_css'),
    'folders/cubit'   : ('cubits', 'cubit'),
    'folders/cypress' : ('cypress',),
    'folders/dapr'    : ('dapr',),
    'folders/db'      : (
        'db',
        'database',
        'sql',
        'data',
        'repo',
        'repository',
        'repositories',
    ),
    'folders/debian'      : ('debian', 'deb'),
    'folders/dependabot'  : ('dependabot',),
    'folders/devcontainer': ('devcontainer',),
    'folders/dist'        : (
        'dist',
        'dists',
        'out',
        'outs',
        'export',
        'exports',
        'build',
        'builds',
        'release',
        'releases',
        'target',
        'targets',
    ),
    'folders/docker'          : ('docker',),
    'folders/docs'            : ('docs', 'doc'),
    'folders/e2e'             : ('e2e',),
    'folders/elasticbeanstalk': ('elasticbeanstalk', 'ebextensions'),
    'folders/electron'        : ('electron',),
    'folders/expo'            : ('expo', 'expo-shared'),
    'folders/favicon'         : ('favicon', 'favicons'),
    'folders/flow'            : ('flow', 'flow-typed'),
    'folders/fonts'           : ('fonts', 'font', 'fnt'),
    'folders/gcp'             : ('gcp',),
    'folders/git'             : ('git', 'submodules'),
    'folders/github'          : ('github',),
    'folders/gitlab'          : ('gitlab',),
    'folders/graphql'         : ('graphql',),
    'folders/gradle'          : ('gradle',),
    'folders/grunt'           : ('grunt',),
    'folders/gulp'            : (
        'gulp',
        'gulpfile.js',
        'gulpfile.coffee',
        'gulpfile.ts',
        'gulpfile.babel.js',
        'gulpfile.babel.coffee',
        'gulpfile.babel.ts',
    ),
    'folders/haxelib': ('haxelib', 'haxe_libraries'),
    'folders/helper' : ('helper', 'helpers'),
    'folders/hook'   : ('hook', 'hooks'),
    'folders/husky'  : ('husky',),
    'folders/idea'   : ('idea',),
    'folders/images' : (
        'images',
        'image',
        'img',
        'imgs',
        'icons',
        'icon',
        'ico',
        'screenshot',
        'screenshots',
        'svg',
    ),
    'folders/include'   : ('include', 'includes', 'incl', 'inc'),
    'folders/interfaces': ('interface', 'interfaces'),
    'folders/ios'       : ('ios',),
    'folders/js'        : ('js',),
    'folders/json'      : ('json',),
    'folders/kubernetes': ('kubernetes', 'k8s', 'kube', 'kuber'),
    'folders/less'      : ('less', '_less'),
    'folders/library'   : ('lib', 'libs', 'lib', 'libs', 'library', 'libraries'),
    'folders/linux'     : ('linux',),
    'folders/locale'    : (
        'lang',
        'language',
        'languages',
        'locale',
        'locales',
        'internationalization',
        'globalization',
        'localization',
        'i18n',
        'g11n',
        'l10n',
    ),
    'folders/log'         : ('log', 'logs'),
    'folders/macos'       : ('macos', 'darwin'),
    'folders/mariadb'     : ('mariadb', 'maria'),
    'folders/maven'       : ('mvn',),
    'folders/memcached'   : ('memcached',),
    'folders/middleware'  : ('middleware', 'middlewares'),
    'folders/mjml'        : ('mjml', 'mjml'),
    'folders/minikube'    : ('minikube', 'minik8s', 'minikuber'),
    'folders/mock'        : ('mocks', 'mocks', '__mocks__'),
    'folders/model'       : ('model', 'models', 'entities'),
    'folders/mongodb'     : ('mongodb', 'mongo'),
    'folders/mysql'       : ('mysqldb', 'mysql'),
    'folders/next'        : ('next',),
    'folders/nginx'       : ('nginx', 'conf.d'),
    'folders/nix'         : ('niv', 'nix', 'niv'),
    'folders/node'        : ('node_modules',),
    'folders/notification': ('notification', 'notifications', 'event', 'events'),
    'folders/nuget'       : ('nuget',),
    'folders/package'     : ('package', 'packages', 'pkg'),
    'folders/paket'       : ('paket',),
    'folders/php'         : ('php',),
    'folders/platformio'  : ('pio', 'pioenvs'),
    'folders/plugin'      : ('plugin', 'plugins', 'extension', 'extensions'),
    'folders/prisma'      : ('prisma',),
    'folders/private'     : ('private',),
    'folders/public'      : ('public',),
    'folders/python'      : ('venv', 'virtualenv'),
    'folders/redis'       : ('redis',),
    'folders/ravendb'     : ('ravendb',),
    'folders/route'       : ('route', 'routes', 'routers'),
    'folders/redux'       : ('redux',),
    'folders/meteor'      : ('meteor',),
    'folders/nuxt'        : ('nuxt',),
    'folders/sass'        : ('sass', 'scss'),
    'folders/script'      : ('script', 'scripts'),
    'folders/server'      : ('server',),
    'folders/services'    : ('service', 'services'),
    'folders/src'         : ('src', 'source', 'sources'),
    'folders/sso'         : ('sso',),
    'folders/story'       : ('story', 'stories', '__stories__', 'storybook'),
    'folders/style'       : ('style', 'styles'),
    'folders/tauri'       : ('src-tauri',),
    'folders/test'        : (
        'tests',
        'test',
        '__tests__',
        '__test__',
        'spec',
        'specs',
        'integration',
    ),
    'folders/temp'      : ('temp', 'tmp'),
    'folders/template'  : ('template', 'templates'),
    'folders/theme'     : ('theme', 'themes'),
    'folders/travis'    : ('travis',),
    'folders/tools'     : ('tool', 'tools', 'util', 'utils'),
    'folders/trunk'     : ('trunk',),
    'folders/typescript': ('typescript', 'ts'),
    'folders/typings'   : ('typings', '@types'),
    'folders/vagrant'   : ('vagrant',),
    'folders/video'     : ('video', 'videos'),
    'folders/view'      : ('html', 'view', 'views', 'layout', 'layouts', 'page', 'pages'),
    'folders/vs'        : ('vs',),
    'folders/vscode'    : ('vscode',),
    'folders/webpack'   : ('webpack',),
    'folders/windows'   : ('windows', 'win32'),
    'folders/www'       : ('www', 'wwwroot'),
    'folders/yarn'      : ('yarn',),

    # ! --------------------------------------------
    # ! KEEP ALWAYS AT THE END
    # ! --------------------------------------------

    'folders/module': ('modules',),
}

files = {
    'files/access': (
        'accdb',
        'accdt',
        'mdb',
        'accda',
        'accdc',
        'accde',
        'accdp',
        'accdr',
        'accdu',
        'ade',
        'adp',
        'laccdb',
        'ldb',
        'mam',
        'maq',
        'mdw',
    ),
    'files/actionscript'           : ('as',),
    'files/ada'                    : ('ada',),
    'files/advpl'                  : ('prw',),
    'files/ai'                     : ('ai',),
    'files/al'                     : ('al',),
    'files/allcontributors'        : ('all-contributorsrc',),
    'files/affinitydesigner'       : ('afdesign', 'affinitydesigner'),
    'files/affinityphoto'          : ('afphoto', 'affinityphoto'),
    'files/affinitypublisher'      : ('appscript', 'affinitypublisher'),
    'files/appscript'              : ('gs',),
    'files/fitbit'                 : ('fba',),
    'files/angular'                : ('angular-cli.json', 'angular.json'),
    'files/ng_component_dart'      : ('component.dart',),
    'files/ng_component_ts'        : ('component.ts',),
    'files/ng_component_js'        : ('component.js',),
    'files/ng_directive_dart'      : ('directive.dart',),
    'files/ng_directive_ts'        : ('directive.ts',),
    'files/ng_directive_js'        : ('directive.js',),
    'files/ng_guard_dart'          : ('guard.dart',),
    'files/ng_guard_ts'            : ('guard.ts',),
    'files/ng_guard_js'            : ('guard.js',),
    'files/ng_module_dart'         : ('module.dart',),
    'files/ng_module_ts'           : ('module.ts',),
    'files/ng_module_js'           : ('module.js',),
    'files/ng_pipe_dart'           : ('pipe.dart',),
    'files/ng_pipe_ts'             : ('pipe.ts',),
    'files/ng_pipe_js'             : ('pipe.js',),
    'files/ng_routing_dart'        : ('routing.dart',),
    'files/ng_routing_ts'          : ('routing.ts',),
    'files/ng_routing_js'          : ('routing.js',),
    'files/ng_smart_component_dart': ('page.dart', 'container.dart'),
    'files/ng_smart_component_ts'  : ('page.ts', 'container.ts'),
    'files/ng_smart_component_js'  : ('page.js', 'container.js'),
    'files/ng_service_dart'        : ('service.dart',),
    'files/ng_service_ts'          : ('service.ts',),
    'files/ng_service_js'          : ('service.js',),
    'files/ng_interceptor_dart'    : ('interceptor.dart',),
    'files/ng_interceptor_ts'      : ('interceptor.ts',),
    'files/ng_interceptor_js'      : ('interceptor.js',),
    'files/ng_tailwind'            : ('ng-tailwind.js',),
    'files/affectscript'           : ('affect',),
    'files/ansible'                : ('ansible',),
    'files/antlr'                  : ('g4',),
    'files/anyscript'              : ('any',),
    'files/apache'                 : ('htaccess',),
    'files/apex'                   : ('cls',),
    'files/apib'                   : ('apib',),
    'files/api_extractor'          : ('api-extractor.json', 'api-extractor-base.json'),
    'files/apl'                    : ('apl',),
    'files/applescript'            : ('applescript',),
    'files/appsemble'              : ('.appsemblerc.yaml', 'app-definition.yaml'),
    'files/appveyor'               : ('appveyor.yml', '.appveyor.yml'),
    'files/arduino'                : ('ino', 'pde'),
    'files/asciidoc'               : ('adoc',),
    'files/asp'                    : ('asp',),
    'files/aspx'                   : ('aspx', 'ascx'),
    'files/assembly'               : ('asm',),
    'files/astro'                  : ('astro',),
    'files/astroconfig'            : (
        'astro.config.js',
        'astro.config.cjs',
        'astro.config.mjs',
        'astro.config.ts',
    ),
    'files/ats'  : ('ats',),
    'files/audio': (
        'aac',
        'act',
        'aiff',
        'amr',
        'ape',
        'au',
        'dct',
        'dss',
        'dvf',
        'flac',
        'gsm',
        'iklax',
        'ivs',
        'm4a',
        'm4b',
        'm4p',
        'mmf',
        'mogg',
        'mp3',
        'mpc',
        'msv',
        'oga',
        'ogg',
        'opus',
        'ra',
        'raw',
        'tta',
        'vox',
        'wav',
        'wma',
    ),
    'files/aurelia'       : ('aurelia.json',),
    'files/autohotkey'    : ('ahk',),
    'files/autoit'        : ('au3',),
    'files/avif'          : ('avif',),
    'files/avro'          : ('avcs',),
    'files/awk'           : ('awk',),
    'files/aws'           : ('aws',),
    'files/azure'         : ('azcli',),
    'files/azurepipelines': ('azure-pipelines.yml', '.vsts-ci.yml'),
    'files/babel'         : (
        '.babelrc',
        '.babelignore',
        '.babelrc.js',
        '.babelrc.cjs',
        '.babelrc.mjs',
        '.babelrc.json',
        'babel.config.js',
        'babel.config.cjs',
        'babel.config.mjs',
        'babel.config.json',
    ),
    'files/ballerina': ('bal',),
    'files/bat'      : ('bat',),
    'files/bats'     : ('bats',),
    'files/bazaar'   : ('.bzrignore',),
    'files/bazel'    : ('BUILD.bazel', '.bazelrc', 'bazel.rc', 'bazel.bazelrc', 'bzl'),
    'files/befunge'  : ('bf',),
    'files/bicep'    : ('bicep',),
    'files/biml'     : ('biml',),
    'files/binary'   : (
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
    ),
    'files/bithound'         : ('.bithoundrc',),
    'files/bitbucketpipeline': ('bitbucket-pipelines.yml',),
    'files/blade'            : ('blade.php',),
    'files/blitzbasic'       : ('bb', 'blitzbasic'),
    'files/bolt'             : ('bolt',),
    'files/bosque'           : ('bsq',),
    'files/bower'            : ('.bowerrc', 'bower.json'),
    'files/browserslist'     : ('.browserslistrc', 'browserslist'),
    'files/buckbuild'        : ('.buckconfig',),
    'files/bundler'          : ('gemfile', 'gemfile.lock'),
    'files/c'                : ('.c',),
    'files/c_al'             : ('.cal',),
    'files/cabal'            : ('.cabal',),
    'files/caddy'            : ('.Caddyfile',),
    'files/cake'             : ('cake',),
    'files/cakephp'          : ('cake.php',),
    'files/capacitor'        : ('capacitor.config.json',),
    'files/cargo'            : ('cargo.toml', 'cargo.lock'),
    'files/casc'             : ('casc',),
    'files/cddl'             : ('cddl',),
    'files/cert'             : (
        'csr',
        'crt',
        'cer',
        'der',
        'pfx',
        'p12',
        'p7b',
        'p7r',
        'src',
        'crl',
        'sst',
        'stl',
    ),
    'files/ceylon' : ('lucee',),
    'files/cf'     : ('lucee',),
    'files/cfc'    : ('cfc',),
    'files/cfm'    : ('cfm',),
    'files/cheader': ('h',),
    'files/chef'   : (
        'chefignore',
        'berksfile',
        'berksfile.lock',
        'policyfile.rb',
        'policyfile.lock.json',
    ),
    'files/class'        : ('class',),
    'files/circleci'     : ('circle.yml',),
    'files/clojure'      : ('cjm', 'cljc', 'clojure'),
    'files/clojurescript': ('cljs', 'clojurescript'),
    'files/cloudfoundry' : ('.cfignore',),
    'files/cmake'        : ('cmake', 'CMakeCache.txt'),
    'files/cobol'        : ('cbl',),
    'files/codeql'       : ('ql',),
    'files/codeowners'   : ('codeowners',),
    'files/codacy'       : ('.codacy.yml', '.codacy.yaml'),
    'files/codeclimate'  : ('.codeclimate.yml',),
    'files/codecov'      : ('codecov.yml', '.codecov.yml'),
    'files/codekit'      : (
        'config.codekit',
        'config.codekit2',
        'config.codekit3',
        '.config.codekit',
        '.config.codekit2',
        '.config.codekit3',
    ),
    'files/coffeelint'  : ('coffeelint.json', '.coffeelintignore'),
    'files/coffeescript': ('coffee',),
    'files/conan'       : ('conanfile.txt', 'conanfile.py'),
    'files/conda'       : ('.condarc',),
    'files/config'      : ('plist', 'env', 'properties', '.tool-versions'),
    'files/commitizen'  : ('.czrc', '.cz.json'),
    'files/commitlint'  : (
        '.commitlintrc',
        'commitlint.config.js',
        'commitlint.config.cjs',
        'commitlint.config.ts',
        '.commitlintrc.json',
        '.commitlintrc.yaml',
        '.commitlintrc.yml',
        '.commitlintrc.js',
        '.commitlintrc.cjs',
        '.commitlintrc.ts',
    ),
    'files/compass'      : ('compass',),
    'files/composer'     : ('composer.json', 'composer.lock'),
    'files/chef_cookbook': ('ckbk',),
    'files/confluence'   : ('confluence',),
    'files/coveralls'    : ('.coveralls.yml',),
    'files/cpp'          : ('cpp',),
    'files/cppheader'    : ('hpp', 'hh', 'hxx', 'h++'),
    'files/crowdin'      : ('crowdin.yml',),
    'files/crystal'      : ('cr',),
    'files/csharp'       : ('csx', 'cs'),
    'files/csproj'       : ('csproj',),
    'files/css'          : ('css',),
    'files/csscomb'      : ('.csscomb.json',),
    'files/csslint'      : ('.csslintrc',),
    'files/cssmap'       : ('css.map',),
    'files/cucumber'     : ('feature',),
    'files/cuda'         : ('cu',),
    'files/cython'       : ('pyx',),
    'files/cypress'      : (
        'cypress.json',
        'cypress.env.json',
        'cypress.config.js',
        'cypress.config.ts',
        'cypress.config.cjs',
        'cypress.config.mjs',
    ),
    'files/cypress_spec': (
        'cy.js',
        'cy.mjs',
        'cy.cjs',
        'cy.coffee',
        'cy.ts',
        'cy.tsx',
        'cy.jsx',
    ),
    'files/cvs'               : ('.cvsignore',),
    'files/dal'               : ('dal',),
    'files/darcs'             : ('.boringignore',),
    'files/dartlang'          : ('dart',),
    'files/dartlang_generated': ('g.dart', 'freezed.dart'),
    'files/dartlang_ignore'   : ('.pubignore',),
    'files/db'                : ('db',),
    'files/dependabot'        : ('dependabot.yml',),
    'files/dependencies'      : ('dependencies.yml',),
    'files/delphi'            : ('pas',),
    'files/devcontainer'      : ('devcontainer.json', '.devcontainer.json'),
    'files/dhall'             : ('dhall',),
    'files/django'            : ('djt',),
    'files/diff'              : ('diff',),
    'files/docker'            : (
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
        'dockerfile',
    ),
    'files/dockertest': ('docker-compose.test.yml',),
    'files/docpad'    : ('eco',),
    'files/docz'      : (
        '.doczrc',
        'docz.js',
        'docz.json',
        '.docz.js',
        '.docz.json',
        'doczrc.js',
        'doczrc.json',
        'docz.config.js',
        'docz.config.json',
    ),
    'files/dojo'   : ('.dojorc',),
    'files/doxygen': ('.dox',),
    'files/drawio' : (
        '.drawio',
        'dio' '.drawio.png',
        '.drawio.svg',
        '.dio.png',
        '.dio.svg',
    ),
    'files/drone'           : ('.drone.yml', '.drone.yml.sig'),
    'files/drools'          : ('.drl',),
    'files/dotjs'           : ('dot',),
    'files/dustjs'          : ('dust',),
    'files/dvc'             : ('.dvc',),
    'files/dylan'           : ('dylan',),
    'files/editorconfig'    : ('.editorconfig',),
    'files/earthly'         : ('.earthlyignore', 'earthfile'),
    'files/edge'            : ('edge',),
    'files/eex'             : ('eex',),
    'files/ejs'             : ('ejs',),
    'files/elastic'         : ('es',),
    'files/elasticbeanstalk': ('elasticbeanstalk',),
    'files/elixir'          : ('ex',),
    'files/elm'             : ('elm-package.json', 'elm'),
    'files/emacs'           : ('el', 'elc'),
    'files/ember'           : ('.ember-cli',),
    'files/ensime'          : ('ensime',),
    'files/eps'             : ('eps',),
    'files/erb'             : ('erb',),
    'files/erlang'          : ('emakefile', '.emakerfile', 'erl'),
    'files/eslint'          : (
        '.eslintrc',
        '.eslintignore',
        '.eslintcache',
        '.eslintrc.js',
        '.eslintrc.mjs',
        '.eslintrc.cjs',
        '.eslintrc.json',
        '.eslintrc.yaml',
        '.eslintrc.yml',
    ),
    'files/excel'          : ('xls', 'xlsx', 'xlsm', 'ods', 'fods', 'xlsb'),
    'files/expo'           : ('app.json', 'app.config.js', 'app.config.json', 'app.config.json5'),
    'files/falcon'         : ('falcon',),
    'files/fauna'          : ('.faunarc', 'fql'),
    'files/favicon'        : ('favicon.ico',),
    'files/fbx'            : ('fbx',),
    'files/firebase'       : ('.firebaserc',),
    'files/firebasehosting': ('firebase.json',),
    'files/firestore'      : ('firestore.rules', 'firestore.indexes.json'),
    'files/fla'            : ('fla',),
    'files/flareact'       : ('flareact.config.js',),
    'files/flash'          : ('swf', 'swc'),
    'files/floobits'       : ('.flooignore',),
    'files/flow'           : ('js.flow', '.flowconfig'),
    'files/flutter'        : ('.flutter-plugins', '.metadata'),
    'files/flutter_package': ('pubspec.lock', 'pubspec.yaml', '.packages'),
    'files/font'           : ('woff', 'woff2', 'ttf', 'otf', 'eot', 'pfa', 'pfb', 'sfd'),
    'files/formkit'        : (
        'formkit.config.js',
        'formkit.config.mjs',
        'formkit.config.cjs',
        'formkit.config.ts',
    ),
    'files/fortran'   : ('f',),
    'files/fossa'     : ('.fossaignore',),
    'files/fossil'    : ('ignore-glob',),
    'files/fsharp'    : ('fs',),
    'files/fsproj'    : ('fsproj',),
    'files/freemarker': ('ftl',),
    'files/fthtml'    : ('fthtml',),
    'files/funding'   : ('funding.yml',),
    'files/fusebox'   : ('fuse.js',),
    'files/galen'     : ('gspec',),
    'files/git'       : (
        '.gitattributes',
        '.gitconfig',
        '.gitignore',
        '.gitmodules',
        '.gitkeep',
        '.mailmap',
        '.issuetracker',
        'git-commit',
        'git-rebase',
        'ignore',
        'git',
    ),
    'files/gamemaker': ('gmx', 'gml'),
    'files/gatsby'   : (
        'gatsby-browser.js',
        'gatsby-browser.ts',
        'gatsby-browser.tsx',
        'gatsby-ssr.js',
        'gatsby-ssr.ts',
        'gatsby-ssr.tsx',
        'gatsby-config.js',
        'gatsby-config.ts',
        'gatsby-node.js',
        'gatsby-node.ts',
    ),
    'files/gcode'         : ('gcode',),
    'files/genstat'       : ('gen',),
    'files/gitlab'        : ('.gitlab-ci.yml',),
    'files/gitpod'        : ('.gitpod.yaml', '.gitpod.yml', 'gitpod.yaml', 'gitpod.yml'),
    'files/glide'         : ('glide.yml',),
    'files/glitter'       : ('.glitterrc',),
    'files/glsl'          : ('glsl',),
    'files/glyphs'        : ('glyphs',),
    'files/gnuplot'       : ('gp',),
    'files/go'            : ('go',),
    'files/go_package'    : ('go.sum', 'go.mod'),
    'files/goctl'         : ('api',),
    'files/godot'         : ('gd',),
    'files/gradle'        : ('gradle',),
    'files/graphql'       : ('.gqlconfig', 'gql'),
    'files/graphql_config': (
        '.graphqlconfig',
        '.graphqlconfig.yml',
        '.graphqlconfig.yaml',
    ),
    'files/graphviz'   : ('dot',),
    'files/greenkeeper': ('greenkeeper.json',),
    'files/gridsome'   : (
        'gridsome.config.js',
        'gridsome.config.ts',
        'gridsome.server.js',
        'gridsome.server.ts',
        'gridsome.client.js',
        'gridsome.client.ts',
    ),
    'files/groovy': ('groovy',),
    'files/grunt' : (
        'gruntfile.js',
        'gruntfile.coffee',
        'gruntfile.ts',
        'gruntfile.babel.js',
        'gruntfile.babel.coffee',
        'gruntfile.babel.ts',
    ),
    'files/gulp': (
        'gulpfile.js',
        'gulpfile.coffee',
        'gulpfile.ts',
        'gulpfile.mjs',
        'gulpfile.esm.js',
        'gulpfile.esm.coffee',
        'gulpfile.esm.ts',
        'gulpfile.esm.mjs',
        'gulpfile.babel.js',
        'gulpfile.babel.coffee',
        'gulpfile.babel.ts',
        'gulpfile.babel.mjs',
    ),
    'files/haml'          : ('haml',),
    'files/handlebars'    : ('hbs',),
    'files/harbour'       : ('prg',),
    'files/hardhat'       : ('hardhat.config.js', 'hardhat.config.ts'),
    'files/haskell'       : ('hs',),
    'files/haxe'          : ('haxelib.json', 'haxe'),
    'files/haxecheckstyle': ('checkstyle.json',),
    'files/haxedevelop'   : ('hxproj',),
    'files/helix'         : ('.p4ignore',),
    'files/helm'          : ('chart.lock', 'chart.yaml', 'helm.tpl'),
    'files/hjson'         : ('hjson',),
    'files/hlsl'          : ('hlsl',),
    'files/horusec'       : ('horusec-config.json',),
    'files/host'          : ('hosts',),
    'files/html'          : ('html',),
    'files/htmlhint'      : ('.htmlhintrc',),
    'files/http'          : ('http',),
    'files/hunspell'      : ('aff',),
    'files/husky'         : (
        '.huskyrc',
        'husky.config.js',
        '.huskyrc.js',
        '.huskyrc.json',
        '.huskyrc.yaml',
        '.huskyrc.yml',
    ),
    'files/hy'       : ('hy',),
    'files/hygen'    : ('htejs.ttp',),
    'files/hypr'     : ('hypr',),
    'files/icl'      : ('icl',),
    'files/idris'    : ('idr', 'lidr'),
    'files/idrisbin' : ('ibc',),
    'files/idrispkg' : ('ipkg',),
    'files/image'    : ('jpeg', 'jpg', 'gif', 'png', 'bmp', 'tiff', 'ico', 'webp'),
    'files/imba'     : ('imba', 'imba2'),
    'files/inc'      : ('inc', 'include'),
    'files/infopath' : ('infopathxml', 'xsn', 'xsf', 'xtp2'),
    'files/informix' : ('4gl',),
    'files/ini'      : ('ini',),
    'files/ink'      : ('ink',),
    'files/innosetup': ('iss',),
    'files/ionic'    : ('ionic.project', 'ionic.config.json'),
    'files/jake'     : ('jakefile', 'jakefile.js'),
    'files/janet'    : ('janet',),
    'files/jar'      : ('jar',),
    'files/jasmine'  : ('jasmine.json',),
    'files/java'     : ('java',),
    'files/jbuilder' : ('jbuilder',),
    'files/jest'     : (
        'jest.config.ts',
        'jest.config.base.ts',
        'jest.config.common.ts',
        'jest.json',
        '.jestrc',
        '.jestrc.js',
        '.jestrc.json',
        'jest.config.js',
        'jest.config.cjs',
        'jest.config.mjs',
        'jest.config.base.js',
        'jest.config.base.cjs',
        'jest.config.base.mjs',
        'jest.config.common.js',
        'jest.config.common.cjs',
        'jest.config.common.mjs',
        'jest.config.babel.js',
        'jest.config.babel.cjs',
        'jest.config.babel.mjs',
    ),
    'files/jest_snapshot': ('js.snap', 'jsx.snap', 'ts.snap', 'tsx.snap'),
    'files/jekyll'       : ('jekyll',),
    'files/jenkins'      : ('jenkins',),
    'files/jinja'        : ('jinja',),
    'files/jpm'          : ('.jpmignore',),
    'files/jsbeautify'   : ('.jsbeautifyrc', 'jsbeautifyrc', '.jsbeautify', 'jsbeautify'),
    'files/jsconfig'     : ('jsconfig.json',),
    'files/jscpd'        : (
        '.jscpd.json',
        'jscpd-report.xml',
        'jscpd-report.json',
        'jscpd-report.html',
    ),
    'files/jshint'   : ('.jshintrc', '.jshintignore'),
    'files/jsmap'    : ('js.map', 'cjs.map', 'mjs.map'),
    'files/jsonnet'  : ('jsonnet',),
    'files/json5'    : ('json5',),
    'files/jsonld'   : ('jsonld', 'json-ld'),
    'files/jsp'      : ('jsp',),
    'files/jss'      : ('jss',),
    'files/julia'    : ('jl',),
    'files/jupyter'  : ('ipynb',),
    'files/io'       : ('io',),
    'files/iodine'   : ('id',),
    'files/k'        : ('k',),
    'files/karma'    : ('karma.conf.js', 'karma.conf.coffee', 'karma.conf.ts'),
    'files/key'      : ('key', 'pem'),
    'files/kite'     : ('.kiteignore',),
    'files/kitchenci': ('.kitchen.yml', 'kitchen.yml'),
    'files/kivy'     : ('kv',),
    'files/kos'      : ('ks',),
    'files/kotlin'   : ('kt',),
    'files/kusto'    : ('.kusto',),
    'files/latino'   : ('lat',),
    'files/layout'   : (
        'master',
        'layout.html',
        'layout.htm',
        'layout.html',
        'layout.htm',
    ),
    'files/lerna'  : ('lerna.json',),
    'files/less'   : ('less',),
    'files/lex'    : ('flex',),
    'files/license': (
        'enc',
        'lic',
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
    ),
    'files/licensebat': ('.licrc',),
    'files/lighthouse': (
        '.lighthouserc.js',
        '.lighthouserc.json',
        '.lighthouserc.yaml',
        '.lighthouserc.yml',
    ),
    'files/lisp'        : ('lisp',),
    'files/lime'        : ('hxp', 'include.xml'),
    'files/lintstagedrc': (
        '.lintstagedrc',
        '.lintstagedrc.json',
        '.lintstagedrc.yaml',
        '.lintstagedrc.yml',
        '.lintstagedrc.mjs',
        '.lintstagedrc.js',
        '.lintstagedrc.cjs',
        'lint-staged.config.mjs',
        'lint-staged.config.js',
        'lint-staged.config.cjs',
    ),
    'files/liquid'             : ('liquid',),
    'files/livescript'         : ('ls',),
    'files/lnk'                : ('lnk',),
    'files/locale'             : ('locale',),
    'files/log'                : ('log', 'tlg'),
    'files/lolcode'            : ('lol',),
    'files/lsl'                : ('lsl',),
    'files/lua'                : ('lua',),
    'files/luau'               : ('luau',),
    'files/lync'               : ('crec', 'ocrec'),
    'files/makefile'           : ('mk', 'makefile'),
    'files/manifest'           : ('manifest',),
    'files/manifest_skip'      : ('manifest.skip',),
    'files/manifest_bak'       : ('manifest.bak',),
    'files/map'                : ('map',),
    'files/markdown'           : ('mdown', 'markdown', 'md'),
    'files/markdownlint'       : ('.markdownlint.json',),
    'files/markdownlint_ignore': ('.markdownlintignore',),
    'files/marko'              : ('marko',),
    'files/markojs'            : ('marko.js',),
    'files/matlab'             : (
        'fig',
        'mex',
        'mexn',
        'mexrs6',
        'mn',
        'mum',
        'mx',
        'mx3',
        'rwd',
        'slx',
        'slddc',
        'smv',
        'xvc',
        'mat',
    ),
    'files/maxscript': ('ms',),
    'files/maven'    : ('maven.config', 'pom.xml', 'extensions.xml', 'settings.xml'),
    'files/maya'     : ('mel',),
    'files/mdx'      : ('mel',),
    'files/mediawiki': ('mediawiki',),
    'files/mercurial': ('.hgignore',),
    'files/meson'    : ('meson.build',),
    'files/meteor'   : ('meteor',),
    'files/mjml'     : ('mjml',),
    'files/mlang'    : ('pq',),
    'files/mocha'    : (
        'mocha.opts',
        '.mocharc.js',
        '.mocharc.json',
        '.mocharc.jsonc',
        '.mocharc.yaml',
        '.mocharc.yml',
    ),
    'files/modernizr': (
        'modernizr',
        'modernizr.js',
        'modernizrrc.js',
        '.modernizr.js',
        '.modernizrrc.js',
    ),
    'files/mojolicious': ('ep',),
    'files/moleculer'  : (
        'moleculer.config.js',
        'moleculer.config.json',
        'moleculer.config.ts',
    ),
    'files/mongo'   : ('mongo',),
    'files/monotone': ('.mtn-ignore',),
    'files/mson'    : ('mson',),
    'files/mustache': ('mustache', 'mst'),
    'files/ndst'    : ('ndst.yaml', 'ndst.yml', 'ndst.json'),
    'files/nearly'  : ('ne',),
    'files/nestjs'  : (
        '.nest-cli.json',
        'nest-cli.json',
        'nestconfig.json',
        '.nestconfig.json',
    ),
    'files/nest_adapter_js'    : ('adapter.js',),
    'files/nest_adapter_ts'    : ('nest_decorator_js',),
    'files/nest_controller_js' : ('controller.js',),
    'files/nest_controller_ts' : ('controller.ts',),
    'files/nest_decorator_js'  : ('decorator.js',),
    'files/nest_decorator_ts'  : ('decorator.ts',),
    'files/nest_filter_js'     : ('filter.js',),
    'files/nest_filter_ts'     : ('filter.ts',),
    'files/nest_gateway_js'    : ('gateway.js',),
    'files/nest_gateway_ts'    : ('gateway.ts',),
    'files/nest_guard_js'      : ('guard.js',),
    'files/nest_guard_ts'      : ('guard.ts',),
    'files/nest_interceptor_js': ('interceptor.js',),
    'files/nest_interceptor_ts': ('interceptor.ts',),
    'files/nest_middleware_js' : ('middleware.js',),
    'files/nest_middleware_ts' : ('middleware.ts',),
    'files/nest_module_js'     : ('module.js',),
    'files/nest_module_ts'     : ('module.ts',),
    'files/nest_pipe_js'       : ('pipe.js',),
    'files/nest_pipe_ts'       : ('pipe.ts',),
    'files/nest_service_js'    : ('service.js',),
    'files/nest_service_ts'    : ('service.ts',),
    'files/netlify'            : ('netlify.toml',),
    'files/next'               : ('next.config.js', 'next.config.mjs'),
    'files/nginx'              : ('nginx.conf',),
    'files/nim'                : ('nim',),
    'files/nimble'             : ('nimble',),
    'files/ninja'              : ('build.ninja',),
    'files/noc'                : ('noc',),
    'files/nix'                : ('nix',),
    'files/njsproj'            : ('njsproj',),
    'files/node'               : ('.node-version', '.nvmrc'),
    'files/nodemon'            : ('nodemon.json',),
    'files/npm'                : (
        '.npmignore',
        '.npmrc',
        'package.json',
        'package-lock.json',
        'npm-shrinkwrap.json',
    ),
    'files/nsi' : ('nsi',),
    'files/nsri': (
        '.nsrirc',
        '.nsriignore',
        'nsri.config.js',
        '.nsrirc.js',
        '.nsrirc.json',
        '.nsrirc.yaml',
        '.nsrirc.yml',
    ),
    'files/nsri-integrity': ('.integrity.json',),
    'files/nuget'         : ('nupkg', 'snupkg', 'nuspec', 'psmdcp'),
    'files/numpy'         : ('npy', 'npz'),
    'files/nunjucks'      : ('nunj', 'njs', 'nunjucks'),
    'files/nuxt'          : ('nuxt.config.js', 'nuxt.config.ts'),
    'files/nyc'           : ('.nycrc', '.nycrc.json'),
    'files/objectivec'    : ('m',),
    'files/objectivecpp'  : ('mm',),
    'files/objidconfig'   : ('.objidconfig',),
    'files/ocaml'         : ('.merlin', '.ml'),
    'files/ogone'         : ('o3',),
    'files/onenote'       : ('one', 'onepkg', 'onetoc', 'onetoc2', 'sig'),
    'files/openscad'      : ('scad',),
    'files/opencl'        : ('cl', 'opencl'),
    'files/openHAB'       : ('things',),
    'files/org'           : ('org',),
    'files/outlook'       : ('pst', 'bcmx', 'otm', 'msg', 'oft'),
    'files/ovpn'          : ('ovpn',),
    'files/package'       : ('pkg',),
    'files/paket'         : (
        'paket.dependencies',
        'paket.lock',
        'paket.references',
        'paket.template',
        'paket.local',
    ),
    'files/patch'          : ('patch',),
    'files/pcl'            : ('pcd',),
    'files/pddl'           : ('pddl',),
    'files/pddl_plan'      : ('plan',),
    'files/pddl_happenings': ('happenings',),
    'files/pdf'            : ('pdf',),
    'files/peeky'          : ('peeky.config.ts', 'peeky.config.js', 'peeky.config.mjs'),
    'files/perl'           : ('pl',),
    'files/perl6'          : ('pl6',),
    'files/pgsql'          : ('pgsql',),
    'files/photoshop'      : ('psd',),
    'files/php'            : (
        'php1',
        'php2',
        'php3',
        'php4',
        'php5',
        'php6',
        'phps',
        'phpsa',
        'phpt',
        'phtml',
        'phar',
        'php',
    ),
    'files/phpcsfixer'          : ('.php_cs', '.php_cs.dist'),
    'files/phpunit'             : ('phpunit', 'phpunit.xml', 'phpunit.xml.dist'),
    'files/phraseapp'           : ('.phraseapp.yml',),
    'files/pine'                : ('pine',),
    'files/pip'                 : ('pipfile', 'pipfile.lock', 'requirements.txt'),
    'files/pipeline'            : ('pipeline',),
    'files/platformio'          : ('platformio.ini', 'dbgasm'),
    'files/plantuml'            : ('pu', 'plantuml', 'iuml', 'puml'),
    'files/playwright'          : ('playwright.config.js', 'playwright.config.ts'),
    'files/plsql'               : ('ddl',),
    'files/plsql_package'       : ('pkb',),
    'files/plsql_package_body'  : ('pkh',),
    'files/plsql_package_header': ('pck',),
    'files/plsql_package_spec'  : ('pks',),
    'files/pnpm'                : ('pnpmfile.js', 'pnpm-lock.yaml', 'pnpm-workspace.yaml'),
    'files/poedit'              : ('po', 'mo'),
    'files/polymer'             : ('polymer',),
    'files/pony'                : ('pony',),
    'files/postcss'             : ('pcss',),
    'files/postcssconfig'       : (
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
    ),
    'files/powerpoint': (
        'pot',
        'potx',
        'potm',
        'pps',
        'ppsx',
        'ppsm',
        'ppt',
        'pptx',
        'pptm',
        'pa',
        'ppa',
        'ppam',
        'sldm',
        'sldx',
    ),
    'files/powershell'       : ('ps1',),
    'files/powershell_psm'   : ('psm1',),
    'files/powershell_psd'   : ('psd1',),
    'files/powershell_format': ('format.ps1xml',),
    'files/powershell_types' : ('types.ps1xml',),
    'files/preact'           : ('preact.config.js',),
    'files/precommit'        : ('.pre-commit-config.yaml',),
    'files/prettier'         : (
        '.prettierrc',
        '.prettierignore',
        'prettier.config.js',
        'prettier.config.cjs',
        'prettier.config.ts',
        'prettier.config.coffee',
        '.prettierrc.js',
        '.prettierrc.cjs',
        '.prettierrc.json',
        '.prettierrc.json5',
        '.prettierrc.yml',
        '.prettierrc.yaml',
        '.prettierrc.toml',
    ),
    'files/prisma'        : ('prisma',),
    'files/processinglang': ('pde',),
    'files/procfile'      : ('procfile',),
    'files/progress'      : ('w',),
    'files/prolog'        : ('pro', 'P'),
    'files/prometheus'    : ('rules',),
    'files/protobuf'      : ('proto',),
    'files/protractor'    : (
        'protractor.conf.js',
        'protractor.conf.coffee',
        'protractor.conf.ts',
    ),
    'files/publisher': ('pub', 'puz'),
    'files/puppet'   : ('pp',),
    'files/pug'      : (
        '.jade-lintrc',
        '.pug-lintrc',
        '.jade-lint.json',
        '.pug-lintrc.js',
        '.pug-lintrc.json',
        'pug',
    ),
    'files/purescript'   : ('purs',),
    'files/pyret'        : ('arr',),
    'files/python'       : ('py',),
    'files/pytyped'      : ('py.typed',),
    'files/pyup'         : ('.pyup', '.pyup.yml'),
    'files/q'            : ('q',),
    'files/qbs'          : ('qbs',),
    'files/qlikview'     : ('qvd', 'qvw', 'qvs'),
    'files/qml'          : ('qml',),
    'files/qmldir'       : ('qmldir',),
    'files/qsharp'       : ('qs',),
    'files/quasar'       : ('quasar.config.js', 'quasar.conf.js'),
    'files/r'            : ('r',),
    'files/racket'       : ('rkt',),
    'files/rails'        : ('rails',),
    'files/rake'         : ('rake', 'rakefile'),
    'files/raml'         : ('raml',),
    'files/razor'        : ('cshtml',),
    'files/razzle'       : ('razzle.config.js',),
    'files/reactjs'      : ('jsx',),
    'files/reacttemplate': ('rt',),
    'files/reactts'      : ('tsx',),
    'files/reason'       : ('re',),
    'files/red'          : ('red',),
    'files/registry'     : ('reg',),
    'files/rego'         : ('rego',),
    'files/rehype'       : (
        '.rehyperc',
        '.rehypeignore',
        '.rehyperc.cjs',
        '.rehyperc.js',
        '.rehyperc.json',
        '.rehyperc.mjs',
        '.rehyperc.yml',
        '.rehyperc.yaml',
    ),
    'files/remark': (
        '.remarkrc',
        '.remarkignore',
        '.remarkrc.cjs',
        '.remarkrc.js',
        '.remarkrc.json',
        '.remarkrc.mjs',
        '.remarkrc.yml',
        '.remarkrc.yaml',
    ),
    'files/renovate': ('.renovaterc', 'renovate.json', '.renovaterc.json'),
    'files/replit'  : ('.replit', 'replit.nix'),
    'files/rescript': ('res',),
    'files/rest'    : ('rst',),
    'files/retext'  : (
        '.retextrc',
        '.retextignore',
        '.retextrc.cjs',
        '.retextrc.js',
        '.retextrc.json',
        '.retextrc.mjs',
        '.retextrc.yml',
        '.retextrc.yaml',
    ),
    'files/rexx'          : ('rex',),
    'files/riot'          : ('tag',),
    'files/robotframework': ('robot',),
    'files/robots'        : ('robots.txt',),
    'files/rollup'        : (
        'rollup.config.js',
        'rollup.config.cjs',
        'rollup.config.mjs',
        'rollup.config.coffee',
        'rollup.config.ts',
        'rollup.config.common.js',
        'rollup.config.common.cjs',
        'rollup.config.common.mjs',
        'rollup.config.common.coffee',
        'rollup.config.common.ts',
        'rollup.config.dev.js',
        'rollup.config.dev.cjs',
        'rollup.config.dev.mjs',
        'rollup.config.dev.coffee',
        'rollup.config.dev.ts',
        'rollup.config.prod.js',
        'rollup.config.prod.cjs',
        'rollup.config.prod.mjs',
        'rollup.config.prod.coffee',
        'rollup.config.prod.ts',
    ),
    'files/ron'           : ('ron',),
    'files/rmd'           : ('rmd',),
    'files/rproj'         : ('rproj',),
    'files/rspec'         : ('.rspec',),
    'files/rubocop'       : ('.rubocop.yml', '.rubocop_todo.yml'),
    'files/ruby'          : ('rb',),
    'files/rust'          : ('rs',),
    'files/rust_toolchain': ('rust-toolchain',),
    'files/sails'         : ('.sailsrc',),
    'files/saltstack'     : ('sls',),
    'files/san'           : ('san',),
    'files/sas'           : ('sas',),
    'files/sass'          : ('sass',),
    'files/sbt'           : ('sbt',),
    'files/scala'         : ('scala',),
    'files/script'        : ('wsf',),
    'files/scss'          : ('scssm', 'scss'),
    'files/scilab'        : ('sce',),
    'files/sdlang'        : ('sdl',),
    'files/sentry'        : ('.sentryclirc',),
    'files/serverless'    : (
        'serverless.yml',
        'serverless.json',
        'serverless.js',
        'serverless.ts',
    ),
    'files/sequelize'   : ('.sequelizerc', '.sequelizerc.js', '.sequelizerc.json'),
    'files/shaderlab'   : ('unity', 'shader'),
    'files/shell'       : ('fish', 'sh'),
    'files/siyuan'      : ('sy',),
    'files/sketch'      : ('sketch',),
    'files/slang'       : ('slang',),
    'files/slashup'     : ('slash-up.config.js',),
    'files/slice'       : ('ice',),
    'files/slim'        : ('slim',),
    'files/sln'         : ('sln',),
    'files/silverstripe': ('ss',),
    'files/skipper'     : ('eskip',),
    'files/smarty'      : ('tpl',),
    'files/snapcraft'   : ('snapcraft.yaml',),
    'files/snort'       : ('snort',),
    'files/snyk'        : ('.snyk',),
    'files/solidarity'  : ('.solidarity', '.solidarity.json'),
    'files/solidity'    : ('sol',),
    'files/source'      : ('source',),
    'files/spacengine'  : ('spe',),
    'files/sparql'      : ('rq',),
    'files/sqf'         : ('sqf',),
    'files/sql'         : ('sql',),
    'files/sqlite'      : ('sqlite', 'sqlite3', 'db3'),
    'files/squirrel'    : ('nut',),
    'files/sss'         : ('sss',),
    'files/stan'        : ('stan',),
    'files/stata'       : ('dta', 'do'),
    'files/stencil'     : ('stencil',),
    'files/stryker'     : (
        'stryker.conf.mjs',
        'stryker.conf.cjs',
        'stryker.conf.js',
        'stryker.conf.conf',
        'stryker.conf.json',
        '.stryker.conf.mjs',
        '.stryker.conf.cjs',
        '.stryker.conf.js',
        '.stryker.conf.conf',
        '.stryker.conf.json',
        'stryker-config.mjs',
        'stryker-config.cjs',
        'stryker-config.js',
        'stryker-config.conf',
        'stryker-config.json',
        'stryker4s.mjs',
        'stryker4s.cjs',
        'stryker4s.js',
        'stryker4s.conf',
        'stryker4s.json',
    ),
    'files/style'    : ('style',),
    'files/stylelint': (
        '.stylelintrc',
        '.stylelintignore',
        '.stylelintcache',
        'stylelint.config.js',
        'stylelint.config.json',
        'stylelint.config.yaml',
        'stylelint.config.yml',
        'stylelint.config.ts',
        'stylelint.config.cjs',
        '.stylelintrc.js',
        '.stylelintrc.json',
        '.stylelintrc.yaml',
        '.stylelintrc.yml',
        '.stylelintrc.coffee.stylelintrc.ts',
        '.stylelintrc.cjs',
    ),
    'files/stylable'       : ('st.css',),
    'files/styled'         : ('styled',),
    'files/stylish_haskell': ('.stylish-haskell.yaml',),
    'files/stylus'         : ('styl',),
    'files/storyboard'     : ('storyboard',),
    'files/storybook'      : (
        'story.js',
        'story.jsx',
        'story.ts',
        'story.tsx',
        'story.mdx',
        'stories.js',
        'stories.jsx',
        'stories.ts',
        'stories.tsx',
        'stories.mdx',
    ),
    'files/subversion'   : ('.svnignore',),
    'files/svelte'       : ('svelte',),
    'files/svg'          : ('svg',),
    'files/swagger'      : ('swagger',),
    'files/swift'        : ('package.pins', 'swift'),
    'files/swig'         : ('swig',),
    'files/symfony'      : ('symfony.lock',),
    'files/systemd'      : ('link',),
    'files/systemverilog': ('sv',),
    'files/t4tt'         : ('tt',),
    'files/tailwind'     : (
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
    ),
    'files/tauri'    : ('tauri.conf.json',),
    'files/teal'     : ('teal',),
    'files/tt'       : ('tt2', 'tt3'),
    'files/tcl'      : ('ttcl', 'expt'),
    'files/tera'     : ('tera',),
    'files/terraform': ('tfstate', 'tf'),
    'files/test'     : ('tst',),
    'files/testcafe' : ('.testcaferc.json',),
    'files/testjs'   : (
        'test.js',
        'test.jsx',
        'test.mjs',
        'spec.js',
        'spec.jsx',
        'spec.mjs',
    ),
    'files/testts': (
        'test.ts',
        'test.tsx',
        'spec.ts',
        'spec.tsx',
        'e2e-test.ts',
        'e2e-test.tsx',
        'e2e-spec.ts',
        'e2e-spec.tsx',
    ),
    'files/tex'     : ('texi', 'tikz', 'sty', 'tex'),
    'files/text'    : ('csv', 'tsv', 'txt'),
    'files/textile' : ('textile',),
    'files/tiltfile': ('Tiltfile',),
    'files/tfs'     : ('.tfignore',),
    'files/todo'    : ('todo',),
    'files/toit'    : ('toit',),
    'files/toml'    : ('toml',),
    'files/tox'     : ('tox.ini',),
    'files/travis'  : ('.travis.yml',),
    'files/trunk'   : ('trunk.yaml',),
    'files/tsconfig': (
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
    ),
    'files/tslint'       : ('tslint.json', 'tslint.yaml', 'tslint.yml'),
    'files/ttcn'         : ('ttcn3',),
    'files/tuc'          : ('tuc',),
    'files/twig'         : ('twig',),
    'files/typedoc'      : ('typedoc.js', 'typedoc.json'),
    'files/typescriptdef': ('d.ts', 'd.cts', 'd.mts'),
    'files/typo3'        : ('typoscript',),
    'files/unibeautify'  : (
        '.unibeautifyrc',
        'unibeautify.config.js',
        '.unibeautifyrc.js',
        '.unibeautifyrc.json',
        '.unibeautifyrc.yaml',
        '.unibeautifyrc.yml',
    ),
    'files/unlicense': (
        'unlicense',
        'unlicence',
        'unlicense.md',
        'unlicense.txt',
        'unlicence.md',
        'unlicence.txt',
    ),
    'files/vagrant'        : ('vagrantfile',),
    'files/vala'           : ('vala',),
    'files/vanilla_extract': ('css.ts',),
    'files/vapi'           : ('vapi',),
    'files/vash'           : ('vash',),
    'files/vapor'          : ('vapor.yml',),
    'files/vb'             : ('vb',),
    'files/vba'            : ('cls',),
    'files/vbhtml'         : ('vbhtml',),
    'files/vbproj'         : ('vbproj',),
    'files/vcxproj'        : ('vcxproj',),
    'files/velocity'       : ('vm',),
    'files/verilog'        : ('v',),
    'files/vhdl'           : ('vhdl',),
    'files/video'          : (
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
    ),
    'files/view'          : ('view',),
    'files/vim'           : ('.vimrc', '.gvimrc', 'vim'),
    'files/vite'          : ('vite.config.js', 'vite.config.ts'),
    'files/vitest'        : ('vitest.config.ts', 'vitest.config.js', 'vitest.config.mjs'),
    'files/vlang'         : ('v',),
    'files/volt'          : ('volt',),
    'files/vscode'        : ('.vscodeignore', 'launch.json', 'tasks.json', 'vscodeignore.json'),
    'files/vsix'          : ('vsix',),
    'files/vsixmanifest'  : ('vsixmanifest',),
    'files/vue'           : ('vue',),
    'files/vueconfig'     : ('.vuerc', 'vue.config.js', 'vue.config.cjs', 'vue.config.mjs'),
    'files/wallaby'       : ('vue',),
    'files/watchmanconfig': ('.watchmanconfig',),
    'files/wasm'          : ('wasm',),
    'files/webpack'       : (
        'webpack.base.conf.js',
        'webpack.base.conf.coffee',
        'webpack.base.conf.ts',
        'webpack.common.js',
        'webpack.common.coffee',
        'webpack.common.ts',
        'webpack.config.js',
        'webpack.config.coffee',
        'webpack.config.ts',
        'webpack.config.base.js',
        'webpack.config.base.coffee',
        'webpack.config.base.ts',
        'webpack.config.common.js',
        'webpack.config.common.coffee',
        'webpack.config.common.ts',
        'webpack.config.dev.js',
        'webpack.config.dev.coffee',
        'webpack.config.dev.ts',
        'webpack.config.development.js',
        'webpack.config.development.coffee',
        'webpack.config.development.ts',
        'webpack.config.staging.js',
        'webpack.config.staging.coffee',
        'webpack.config.staging.ts',
        'webpack.config.test.js',
        'webpack.config.test.coffee',
        'webpack.config.test.ts',
        'webpack.config.prod.js',
        'webpack.config.prod.coffee',
        'webpack.config.prod.ts',
        'webpack.config.production.js',
        'webpack.config.production.coffee',
        'webpack.config.production.ts',
        'webpack.config.babel.js',
        'webpack.config.babel.coffee',
        'webpack.config.babel.ts',
        'webpack.config.base.babel.js',
        'webpack.config.base.babel.coffee',
        'webpack.config.base.babel.ts',
        'webpack.config.common.babel.js',
        'webpack.config.common.babel.coffee',
        'webpack.config.common.babel.ts',
        'webpack.config.dev.babel.js',
        'webpack.config.dev.babel.coffee',
        'webpack.config.dev.babel.ts',
        'webpack.config.development.babel.js',
        'webpack.config.development.babel.coffee',
        'webpack.config.development.babel.ts',
        'webpack.config.staging.babel.js',
        'webpack.config.staging.babel.coffee',
        'webpack.config.staging.babel.ts',
        'webpack.config.test.babel.js',
        'webpack.config.test.babel.coffee',
        'webpack.config.test.babel.ts',
        'webpack.config.prod.babel.js',
        'webpack.config.prod.babel.coffee',
        'webpack.config.prod.babel.ts',
        'webpack.config.production.babel.js',
        'webpack.config.production.babel.coffee',
        'webpack.config.production.babel.ts',
        'webpack.dev.js',
        'webpack.dev.coffee',
        'webpack.dev.ts',
        'webpack.dev.conf.js',
        'webpack.dev.conf.coffee',
        'webpack.dev.conf.ts',
        'webpack.prod.js',
        'webpack.prod.coffee',
        'webpack.prod.ts',
        'webpack.prod.conf.js',
        'webpack.prod.conf.coffee',
        'webpack.prod.conf.ts',
        'webpack.main.config.js',
        'webpack.main.config.coffee',
        'webpack.main.config.ts',
        'webpack.mix.js',
        'webpack.mix.coffee',
        'webpack.mix.ts',
        'webpack.plugins.js',
        'webpack.plugins.coffee',
        'webpack.plugins.ts',
        'webpack.renderer.config.js',
        'webpack.renderer.config.coffee',
        'webpack.renderer.config.ts',
        'webpack.rules.js',
        'webpack.rules.coffee',
        'webpack.rules.ts',
        'webpack.test.conf.js',
        'webpack.test.conf.coffee',
        'webpack.test.conf.ts',
    ),
    'files/wenyan'   : ('wy',),
    'files/wercker'  : ('wercker.yml',),
    'files/windi'    : ('windi.config.ts', 'windi.config.js'),
    'files/wolfram'  : ('wl',),
    'files/word'     : ('doc', 'docx', 'docm', 'dot', 'dotx', 'dotm', 'wll'),
    'files/wpml'     : ('wpml-config.xml',),
    'files/wurst'    : ('wurst',),
    'files/wxml'     : ('wxml',),
    'files/wxss'     : ('wxss',),
    'files/xcode'    : ('xcodeproj',),
    'files/xfl'      : ('xfl',),
    'files/xib'      : ('xib',),
    'files/xliff'    : ('xliff', 'xlf'),
    'files/xmake'    : ('xmake.lua',),
    'files/xml'      : ('xml',),
    'files/xquery'   : ('xquery',),
    'files/xsl'      : ('xsl',),
    'files/yacc'     : ('bison',),
    'files/yamllint	': ('.yamllint',),
    'files/yandex'   : ('.yaspellerrc', '.yaspeller.json'),
    'files/yang'     : ('yang',),
    'files/yarn'     : (
        'yarn.lock',
        '.yarnrc',
        '.yarnrc.yml',
        '.yarnclean',
        '.yarn-integrity',
        '.yarn-metadata.json',
        '.yarnignore',
    ),
    'files/yeoman' : ('.yo-rc.json',),
    'files/zeit'   : ('now.json', '.nowignore', 'vercel.json', '.vercelignore'),
    'files/zig'    : ('zig',),
    'files/turbo'  : ('turbo.json',),
    'files/doppler': ('doppler.yaml', 'doppler-template.yaml'),
    'files/zip'    : (
        'zip',
        'rar',
        '7z',
        'tar',
        'tgz',
        'bz',
        'gz',
        'bzip2',
        'xz',
        'bz2',
        'zipx',
    ),

    # ! --------------------------------------------
    # ! KEEP ALWAYS AT THE END
    # ! --------------------------------------------

    'files/json'      : ('jsonl', 'ndjson', 'json', 'jsonc'),
    'files/js'        : ('js',),
    'files/typescript': ('ts',),
    'files/yaml'      : ('yaml', 'yml'),
    'files/dlang'     : ('d',),
}
# fmt: on

for i in [files, folders]:
    for k, v in i.items():
        assert isinstance(k, str), f'{k} is not a string'
        assert isinstance(v, tuple), f'{v} is not a tuple'


def get_file_type(path: Path):
    name = path.name

    if name in file_type_cache:
        return file_type_cache[name]

    n = 'Unknown'

    if path.is_dir():
        for t, ext in folders.items():
            if any(name.endswith(i.lower()) for i in ext):
                n = t
                break
        else:
            n = 'folders/folder'

    elif path.is_file():
        for t, ext in files.items():
            if any(name.endswith(i.lower()) for i in ext):
                n = t
                break
        else:
            n = 'files/file'

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

    def start_find(self, path: str, query: str):
        s = StreamFind(path, query)
        s.start()
        streams_finds[path] = s

    def start_folder_size(self, path: str):
        s = StreamFolderSize(path)
        s.start()
        streams_files[path] = s

    def start_delete(self, id: str, path: str, moveToTrash=True):
        s = StreamDelete(id, path, moveToTrash)
        s.start()
        streams_deletes[id] = s

    def ls(self, folder: str):
        if folder not in streams_ls:
            return

        streams_ls[folder].pause()

        # Need copy items, else items is passed by reference and will be empty after clear
        r = {'items': [*streams_ls[folder].items], 'end': streams_ls[folder].end}
        streams_ls[folder].items.clear()

        streams_ls[folder].resume()

        if streams_ls[folder].end:
            del streams_ls[folder]

        return r

    def stream_folder_size(self, path: str | list[str]):
        if path not in streams_files:
            return

        r = {'size': streams_files[path].size, 'end': streams_files[path].end}

        if streams_files[path].end:
            del streams_files[path]

        return r

    def stream_delete(self, id: str):
        if id not in streams_deletes:
            return

        r = {
            'end': streams_deletes[id].end,
            'total': streams_deletes[id].total,
            'deleted': streams_deletes[id].deleted,
            'last_deleted': streams_deletes[id].last_deleted,
        }

        if streams_deletes[id].end:
            del streams_deletes[id]

        return r

    def stream_find(self, path: str):
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

    def home(self):
        return Path.home().as_posix()

    def rename(self, path: str, name: str):
        Path(path).rename(Path(path).parent / name)

    def create_file(self, path: str):
        Path(path).touch()

    def create_folder(self, path: str):
        Path(path).mkdir()

    def exists(self, path: str):
        return Path(path).exists()

    def delete_all_streams_ls(self):
        streams_ls.clear()

    def delete_all_streams_find(self):
        streams_finds.clear()

    def delete_all_streams_folder_size(self):
        streams_files.clear()

    def delete_all_streams_delete(self):
        streams_deletes.clear()

    def get_config(self):
        return load_toml(CONFIG_FILE)

    def set_config(self, config: dict):
        CONFIG_FILE.write_text(dumps_toml(config))

    def read(self, path: str):
        try:
            return Path(path).read_text('utf-8')
        except UnicodeDecodeError:
            return Path(path).read_text('iso-8859-1')

    def read_b64(self, path: str):
        return b64encode(Path(path).read_bytes()).decode()

    def user(self):
        return getuser()

    def pwd(self):
        return Path('').absolute().as_posix()

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
        # https://github.com/urbans0ft/fclip
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

    def get_installed_apps(self):
        # https://pastebin.com/MfDPJ9AM
        run('get-apps.exe', shell=True)

        p = Path('apps.json')
        d = sorted(loads(p.read_text('utf-8')), key=lambda x: x['name'].lower())
        p.unlink()

        return d

    def shell(self, cmd: str):
        run(cmd, shell=True)


streams_files = {}
streams_deletes = {}
streams_finds = {}
streams_ls = {}

DRIVE_TYPES = {
    0: 'Unknown',
    1: 'No Root Directory',
    2: 'Removable Disk',
    3: 'Local Disk',
    4: 'Network Drive',
    5: 'Compact Disc',
    6: 'RAM Disk',
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
                try:
                    data = loads(await ws.recv())

                    if data['type'] == 'call':
                        id = data['id']
                        name = data['name']
                        args = data['args']

                        try:
                            r = getattr(api, name)(*args)
                        except Exception:
                            print_exc()
                            continue

                        await ws.send(dumps({'type': 'return', 'id': id, 'r': r}))
                except ConnectionClosedOK:
                    ...
                except ConnectionClosedError as e:
                    if str(e) != 'no close frame received or sent':
                        raise

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
        debug = False

        if len(args) == 1 and args[0] == 'debug':
            debug = True

        run('cd ui && npm run build', shell=True)
        Thread(target=lambda: run('cd ui && npm run preview', shell=True)).start()

        start(debug=debug, server=False)

elif __name__ == '__main__':
    start()
