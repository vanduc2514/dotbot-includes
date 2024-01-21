import glob
import os
import dotbot
from dotbot.dispatcher import Dispatcher
from dotbot.cli import read_config
from dotbot.plugins import Clean, Create, Link, Shell
from dotbot.util import module
from argparse import Namespace


class Includes(dotbot.Plugin):
    _directive = "includes"
    _defaults = "defaults"

    def can_handle(self, directive):
        return directive == self._directive

    def handle(self, directive, data):
        base_directory = self._context.base_directory()
        success = True
        for directory in data:
            include_config = data.get(directory)
            directory = self._resolve_path(base_directory, directory)
            if not self._handle_config(directory, include_config):
                self._log.error(f"An error occoured when execution actions for {directory}")
                success = False
        return success

    def _handle_config(self,
                       directory: str,
                       include_config: dict):
        options: Namespace = self._context.options()
        skip_defaults = False
        if isinstance(include_config, str):
            config_file = include_config
        elif isinstance(include_config, dict):
            config_file = include_config.get("config_file")
            skip_defaults = include_config.get("skip_defaults")
            include_options = include_config.get("options")
            if include_options is not None:
                options.__dict__.update({option: include_options[option]
                                         for option in vars(options)
                                         if include_options.get(option) is not None})
        else:
            self._log.error("Config for includes must be a string or a dict")
            return False
        tasks = read_config(self._resolve_path(directory, config_file))
        if not skip_defaults and self._defaults not in tasks:
            # if defaults is not at 0 then other plugins can't find it
            tasks.insert(0, {self._defaults: self._context.defaults()})
        return self._execute_config(directory, tasks, options)

    def _execute_config(self,
                        directory: str,
                        tasks: dict,
                        options: Namespace):
        plugins = self._get_plugins(directory, options)
        dispatcher = Dispatcher(base_directory=directory,
                                only=options.only,
                                skip=options.skip,
                                exit_on_failure=options.exit_on_failure,
                                options=options,
                                plugins=plugins)
        return dispatcher.dispatch(tasks)

    def _get_plugins(self,
                     directory: str,
                     options):
        plugins = []
        plugin_paths = options.plugins
        if not options.disable_built_in_plugins:
            plugins.extend([Clean, Create, Link, Shell])
        for plugin_dir in options.plugin_dirs:
            for plugin_path in glob.glob(os.path.join(plugin_dir, "*.py")):
                plugin_paths.append(plugin_path)
        for plugin in plugin_paths:
            path = self._find_plugin_path(directory, plugin)
            if path is None:
                self._log.error(f"Could not find plugin. The path should be relative to the base directory")
            else: 
                load_plugins = module.load(path)
                for plugin in load_plugins:
                    if (not plugin.__name__ == Includes.__name__
                        and not plugin in plugins):
                        plugins.append(plugin)
                        load_plugins.remove(plugin)
        return plugins

    def _find_plugin_path(self,
                          directory: str,
                          plugin: str):
        current = directory
        path = self._resolve_path(current, plugin)
        if os.path.exists(path): return path
        else: current = os.getcwd()
        # Perhaps plugin path is somewhere relative to the working directory ?
        while True:
            path = self._resolve_path(current, plugin)
            if os.path.exists(path): return path
            else:
                parent = os.path.dirname(current)
                if current == parent:  # if current is root
                    return None
                else: current = parent

    def _resolve_path(self, parent: str, child: str):
        return os.path.normpath(os.path.expanduser(child)) if os.path.isabs(child) else os.path.join(parent, child)
