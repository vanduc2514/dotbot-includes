# Dotbot Include Plugin

This Dotbot plugin allows you to include and run other Dotbot configuration files from your main configuration `yaml` file. This can be useful for organizing and modularizing your Dotbot setup.

## Installation

1. Clone this repository as a submodule in your Dotbot configuration directory: `git submodule add https://github.com/vanduc2514/dotbot-includes.git`
2. Update the submodule `git submodule update --ini --recursive`
3. Pass the `includes.py` to the `dotbot` CLI argument: `-p dotbot-icludes/includes.py`

For example

```shell
dotbot -d dotfiles -c install.conf.yaml -p dotbot-includes/includes.py
```

## Usage

In the main `dotbot` configuration file, use the `includes` directive. Specify the paths to other base directories and configuration files.

For example, given this file structure

```text
dotfiles
|-- install.conf.yaml
|-- bash
|   |-- bash.yaml
```

Then the `includes` directive is specified as

```yaml
# Other directives like link, shell
- includes:
    bash: bash.yaml
```

When executing command `dotbot -d dotfiles -c install.conf.yaml -p dotbot-includes/includes.py` dotbot will execute directives in `bash.yaml` under the base directory `bash`. The path to `bash.yaml` is relative to the base directory `bash`

The `includes` Plugin also supports extended configuration. If using this form, the `config_file` property is required to set the path for each configuration file.

```yaml
- includes:
    bash:
        config_file: bash.yaml
```

If there are multiple configuration files in the same base directory

```yaml
- includes:
    base:
        - config_file: bash.yaml
        - config_file: other.yaml
```

### Using Defaults

This plugin applies `defaults` directive from the main configuration file to the execution context of each included configuration file. If an included file defines its own `defaults`, the one from the main configuration is skipped.

To force skip `defaults` from main configuration file, set the `skip_defaults` to `True`:

```yaml
- defaults:
    shell:
        quiet: True

- incldues:
    bash:
        config_file: bash.yaml
        skip_defaults: True
```

### CLI Arguments

The `includes` Plugin can pass CLI arguments to configuration files using the `options` property. If no arguments are provided, it defaults to using the arguments from the `dotbot` command line. (See [Command-line Arguments](https://github.com/anishathalye/dotbot/tree/v1.20.1?tab=readme-ov-file#command-line-arguments))

For example, run only `shell` directive of `bash.yaml`:

```yaml
- includes:
    bash:
        config_file: bash.yaml
        options:
            only: shell
```
