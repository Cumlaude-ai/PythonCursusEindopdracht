import importlib.util
import os

from setuptools import Command
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py


_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_GOOGLE_COMMON_PROTOS_ROOT_DIR = os.path.join(
    _ROOT_DIR, 'third_party/api-common-protos'
)

# Tuple of proto message definitions to build Python bindings for. Paths must
# be relative to root directory.
_DM_ENV_RPC_PROTOS = (
    'dm_env_rpc/v1/dm_env_rpc.proto',
    'dm_env_rpc/v1/extensions/properties.proto',
)


class _GenerateProtoFiles(Command):
  """Command to generate protobuf bindings for dm_env_rpc.proto."""

  descriptions = 'Generates Python protobuf bindings for dm_env_rpc.proto.'
  user_options = []

  def initialize_options(self):
    pass

  def finalize_options(self):
    pass

  def run(self):
    # Import grpc_tools and importlib_resources here, after setuptools has
    # installed setup_requires dependencies.
    from grpc_tools import protoc  # pylint: disable=g-import-not-at-top
    import importlib_resources  # pylint: disable=g-import-not-at-top

    if not os.path.exists(
        os.path.join(_GOOGLE_COMMON_PROTOS_ROOT_DIR, 'google/rpc/status.proto')
    ):
      raise RuntimeError(
          'Cannot find third_party/api-common-protos. '
          'Please run `git submodule init && git submodule update` to install '
          'the api-common-protos submodule.'
      )

    with importlib_resources.as_file(
        importlib_resources.files('grpc_tools') / '_proto'
    ) as grpc_protos_include:
      for proto_path in _DM_ENV_RPC_PROTOS:
        proto_args = [
            'grpc_tools.protoc',
            '--proto_path={}'.format(_GOOGLE_COMMON_PROTOS_ROOT_DIR),
            '--proto_path={}'.format(grpc_protos_include),
            '--proto_path={}'.format(_ROOT_DIR),
            '--python_out={}'.format(_ROOT_DIR),
            '--grpc_python_out={}'.format(_ROOT_DIR),
            os.path.join(_ROOT_DIR, proto_path),
        ]
        if protoc.main(proto_args) != 0:
          raise RuntimeError('ERROR: {}'.format(proto_args))


class _BuildExt(build_ext):
  """Generate protobuf bindings in build_ext stage."""

  def run(self):
    self.run_command('generate_protos')
    build_ext.run(self)


class _BuildPy(build_py):
  """Generate protobuf bindings in build_py stage."""

  def run(self):
    self.run_command('generate_protos')
    build_py.run(self)


def _load_version():
  """Load dm_env_rpc version."""
  spec = importlib.util.spec_from_file_location(
      '_version', 'dm_env_rpc/_version.py'
  )
  version_module = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(version_module)
  return version_module.__version__


setup(
  name = 'CumlaudeDashboardTool',         # How you named your package folder (MyLib)
  packages = ['CumlaudeDashboardTool'],   # Chose the same as "name"
  version = '1.0',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Python pandas tool for creating dsahboards made by cumlaude.ai',   # Give a short description about your library
  author = 'Bram Teunis',                   # Type in your name
  author_email = 'bram.teunis@cumlaude.ai',      # Type in your E-Mail
  url = 'https://github.com/Cumlaude-ai/PythonCursusEindopdracht',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/Cumlaude-ai/PythonCursusEindopdracht/archive/refs/tags/publish.tar.gz',    # I explain this later on
  keywords = ['Pandas', 'Dashboard', 'Data'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'datetime',
          'dash',
          'matplotlib',
          'dash_bootstrap_components',
          'plotly',
          'pandas',
          'dateutil',
          'uuid'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
  ],
)
