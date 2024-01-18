import os
import dotbot
from dotbot.dispatcher import Dispatcher
from dotbot.cli import read_config
from dotbot.plugins import Clean, Create, Link, Shell
from argparse import Namespace


class Include(dotbot.Plugin):
    _directive = "includes"
    _base_directory: str

    def can_handle(self, directive):
        if directive == self._directive:
            self._base_directory = self._context.base_directory()
            return True
        return False

    def handle(self, directive, data):
        if not isinstance(data, dict):
            raise ValueError(
                f"Cannot handle {type(data)} in directive {self.__name__}")
        return all(self._handle_config(config, data.get(config)) for config in data)

    def _handle_config(self,
                       config: str,
                       options: dict | Namespace):
        default_options: Namespace = self._context._options
        config_file = self._resolve_path(parent=self._base_directory,
                                         child=config)
        default_options.__setattr__("config_file", config_file)
        _options = default_options
        if options is not None:
            _options = self._merge_options(default_options, options)
        # TODO: merge plugins
        dispatcher = Dispatcher(base_directory=_options.base_directory,
                                only=_options.only,
                                skip=_options.skip,
                                exit_on_failure=_options.exit_on_failure,
                                options=_options,
                                plugins=self._get_plugins())
        tasks = read_config(config_file=_options.config_file)
        return dispatcher.dispatch(tasks=tasks)

    def _merge_options(self, default_options: Namespace, options: dict):
        if (base_directory := options.get("base_directory")) is not None:
            base_directory = self._resolve_path(parent=self._base_directory,
                                                child=base_directory)
            default_options.__setattr__("base_directory", base_directory)
        if (disable_built_in_plugins := options.get("disable_built_in_plugins")) is not None:
            default_options.__setattr__("disable_built_in_plugins", disable_built_in_plugins)
        if (exit_on_failure := options.get("exit_on_failure")) is not None:
            default_options.__setattr__("exit_on_failure", exit_on_failure)
        if (force_color := options.get("force_color")) is not None:
            default_options.__setattr__("force_color", force_color)
        if (no_color := options.get("no_color")) is not None:
            default_options.__setattr__("no_color", no_color)
        if (only := options.get("only")) is not None:
            default_options.__setattr__("only", only)
        if (plugin_dirs := options.get("plugin_dirs")) is not None:
            default_options.__setattr__("plugin_dirs", plugin_dirs)
        if (plugins := options.get("plugins")) is not None:
            default_options.__setattr__("plugins", plugins)
        if (quiet := options.get("quiet")) is not None:
            default_options.__setattr__("quiet", quiet)
        if (skip := options.get("except")) is not None:
            default_options.__setattr__("skip", skip)
        if (super_quiet := options.get("super_quiet")) is not None:
            default_options.__setattr__("super_quiet", super_quiet)
        if (verbose := options.get("verbose")) is not None:
            default_options.__setattr__("verbose", verbose)
        return self._context.options()

    def _resolve_path(self, parent: str, child: str):
        return child if os.path.isabs(child) else os.path.join(parent, child)

    def _get_plugins(self):
        plugins = []
        plugins.extend([Clean, Create, Link, Shell])
        return plugins
