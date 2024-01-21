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
            directory = self._resolve_path(base_directory, directory)
            if not self._handle_config(directory, include_config):
                self._log.error(f"An error occoured when execution actions for {directory}")
                success = False
        return success

    def _handle_config(self,
                       directory: str,
                       include_config: dict):
        options: Namespace = self._context.options()
        if isinstance(include_config, str):
            config_file = include_config
        elif isinstance(include_config, dict):
            config_file = include_config.get("config_file")
            include_options = include_config.get("options")
            if include_options is not None:
                options.__dict__.update({option: include_options[option]
                                         for option in vars(options)
                                         if include_options.get(option) is not None})
        else:
            self._log.error("Config for includes must be a string or a dict")
            return False
        # TODO: merge plugins
        # TODO: use defaults from main ?
        tasks = read_config(self._resolve_path(directory, config_file))
        return self._execute_config(directory, tasks, options)

    def _execute_config(self,
                        directory: str,
                        tasks: dict,
                        options: Namespace):
        dispatcher = Dispatcher(base_directory=directory,
                                only=options.only,
                                skip=options.skip,
                                exit_on_failure=options.exit_on_failure,
                                options=options,
                                plugins=[Clean, Create, Link, Shell])
        return dispatcher.dispatch(tasks)

    def _resolve_path(self, parent: str, child: str):
        return child if os.path.isabs(child) else os.path.join(parent, child)
