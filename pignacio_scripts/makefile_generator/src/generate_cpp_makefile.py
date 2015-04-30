from __future__ import unicode_literals, print_function
from argparse import ArgumentParser, ArgumentTypeError
import collections
import datetime
import logging
import os
import re
import yaml

INCLUDE_RE = r'\s*#include\s+"([^"]*)"'
HEADER_EXTENSIONS = [".h", ".hpp"]
SOURCE_EXTENSIONS = [".c", ".cpp"]
CPP_EXTENSIONS = HEADER_EXTENSIONS + SOURCE_EXTENSIONS

DEFAULT_CONFIG_FILE = '.makefilegenerator.config'


def _get_arg_parser():
    parser = ArgumentParser()
    parser.add_argument("-c", "--config",
                        default=DEFAULT_CONFIG_FILE,
                        type=MakefileGeneratorConfig.from_argument,
                        help='Configuration file. defaults to {}'
                        .format(DEFAULT_CONFIG_FILE))
    return parser


class MakefileGeneratorConfig():
    def __init__(self, config):
        self._config = config
        self.libs = self._get_field("libs", default=[])
        self.compiler = self._get_field("compiler", description="Compiler")
        self.cargs = self._get_field("compiler_args", default="")
        self.source_dir = os.path.normpath(
            self._get_field("source_dir",
                            description="Sources dir"))
        self.program = self._get_field("program", description="Program name")
        self.compiled_subdir = self._get_field("compiled_subdir",
                                               default=".compiled")

    def _get_field(self, name, default=None, description=None):
        try:
            return self._config[name]
        except KeyError:
            if default is not None:
                return default
            if description is None:
                message = ("Field '{}' is missing from configuration file"
                           .format(name))
            else:
                message = ("{} field '{}' is missing from configuration file"
                           .format(description, name))
            raise ValueError(message)

    @classmethod
    def from_file(cls, filename):
        if not os.path.isfile(filename):
            raise ValueError("{}: Could not load config from '{}'. "
                             "File does not exist"
                             .format(cls.__name__, filename))
        with open(filename) as fin:
            config = yaml.load(fin) or {}
        if not isinstance(config, dict):
            raise ValueError("{}: Coudl not load config from '{}'. "
                             "Parsed config is not a dictionary"
                             .format(cls.__name__, filename))
        return cls(config)

    @classmethod
    def from_argument(cls, filename):
        try:
            return cls.from_file(filename)
        except Exception as exception:
            raise ArgumentTypeError(str(exception))


def _get_dependencies(fname):
    with open(fname) as fin:
        for line in fin:
            mobj = re.match(INCLUDE_RE, line)
            if mobj:
                dep = _normalize_dependency(fname, mobj.group(1))
                if os.path.isfile(dep):
                    yield dep


def _normalize_dependency(parent, dependency):
    return os.path.normpath(os.path.join(os.path.dirname(parent), dependency))


def _rm_extension(fname):
    return fname.rsplit(".", 1)[0]


def _get_header_file(cppfile):
    basename = _rm_extension(cppfile)
    for extensions in HEADER_EXTENSIONS:
        fname = basename + extensions
        if os.path.isfile(fname):
            return fname
    return None


def main():
    logging.basicConfig(level=logging.INFO)
    options = _get_arg_parser().parse_args()
    with open("makefile", "w") as fout:
        _print_makefile(options.config, fout)


def _has_extension(fname, extensions):
    return any(fname.endswith(e) for e in extensions)


def _walk_source_dir(source_dir):
    dependencies = collections.defaultdict(list)
    for path, _subdirs, files in os.walk(source_dir):
        for fname in files:
            fullpath = os.path.join(path, fname)
            if not _has_extension(fullpath, CPP_EXTENSIONS):
                continue
            dependencies[fullpath].extend(_get_dependencies(fullpath))
    return dependencies


def _get_object_filename(source_path, config):
    object_fname = os.path.relpath(source_path, config.source_dir)
    object_fname = os.path.join(config.compiled_subdir, object_fname)
    return _rm_extension(object_fname) + ".o"


def _print_makefile(config, fout):
    def _print(message=""):
        print(message, file=fout)

    dependencies = _walk_source_dir(config.source_dir)
    _print("# Automatically generated makefile. DO NOT EDIT BY HAND")
    _print("# Generated on {}".format(datetime.datetime.now()))
    _print()
    _print("CC := {}".format(config.compiler))
    _print("CARGS := {}".format(config.cargs))
    _print("LIBS := {}".format(" ".join("-l{}".format(l)
                                        for l in config.libs)))
    _print()
    _print("all: {}".format(config.program))
    _print()

    dependencies = sorted(dependencies.items())

    _print()
    _print("# Source files")
    _print()

    object_fnames = []

    for path, deps in dependencies:
        if not _has_extension(path, SOURCE_EXTENSIONS):
            continue
        object_fname = _get_object_filename(path, config)
        object_fnames.append(object_fname)
        _print("{}: {} {}".format(object_fname, path, " ".join(deps)))
        _print("\t-@mkdir -p {}".format(os.path.dirname(object_fname)))
        _print("\t$(CC) $(CARGS) -c -MMD -MP -MF\"$(@:%.o=%.d)\" "
               "-MT\"$(@:%.o=%.d)\" -o \"$@\" \"$<\" $(LIBS)")
        _print()

    _print()
    _print("# Header files")
    _print()

    for path, deps in dependencies:
        if not _has_extension(path, HEADER_EXTENSIONS):
            continue
        _print("{}: {}".format(path, " ".join(deps)))
    _print()

    _print()
    _print("# Listing object files files")
    _print()

    _print("OBJS := \\")
    _print(" \\\n".join(sorted(object_fnames)))
    _print()

    _print("{}: $(OBJS)".format(config.program))
    _print("\t@echo ' '")
    _print("\t@echo 'Linking: $@'")
    _print("\t$(CC) $(CARGS) -o '$@' $(OBJS) $(LIBS)")
    _print("\t@echo 'Finished building $@'")
    _print("\t@echo ' '")
    _print()
    _print("clean:")
    _print("\t-rm -rf $(OBJS) {}".format(config.program))
    _print("\t-@echo ' '")
    _print()
    _print(".PHONY: all clean")


if __name__ == "__main__":
    main()
