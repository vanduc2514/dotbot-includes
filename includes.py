import os
import dotbot
from dotbot.dispatcher import Dispatcher
from dotbot.cli import read_config
from dotbot.plugins import Clean, Create, Link, Shell
from argparse import Namespace


class Include(dotbot.Plugin):
    _directive = "includes"

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        base_directory = self._context.base_directory()
        success = True
        for directory in data:
            include_config = data.get(directory)
            if not self._handle_config(base_directory, directory, include_config):
                self._log.error(f"An error occoured when execution actions for {directory}")
                success = False
        return success

    def _handle_config(self,
                       base_directory: str,
                       directory: str,
                       options: dict):
        if options is None:
            raise ValueError(f"Could not find config file for {base_directory}")
        default_options: Namespace = self._context._options
        _base_directory = self._resolve_path(parent=base_directory,
                                            child=directory)
        default_options.__setattr__("base_directory", _base_directory)
        if isinstance(options, str):
            config_file = self._resolve_path(parent=default_options.base_directory,
                                             child=options)
            _options = default_options
        elif isinstance(options, dict):
            config_file = self._resolve_path(parent=default_options.base_directory,
                                             child=options.get("config_file"))
            _options = self._merge_options(default_options, options)
        else:
            raise ValueError("Config file is neither a string or a dict")
        default_options.__setattr__("config_file", config_file)
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
