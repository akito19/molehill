# Molehill

Molehill is a tool that generates a [Digdag](https://www.digdag.io/) workflow template. The template helps to create Digdag workflow for sending a campaign via [Mailchimp](https://mailchimp.com/):

- Create an Audience.
- Set merge fields.
- Upload HTML template.
- Create a Campaign.

Note that it assumes using Treasure Data workflow.

## Install

This tool has required building from source yet.

```
$ git clone https://github.com/akito19/molehill.git
$ cd molehill
$ cargo install --path .
```

## Usage

You can find options by `-h` or `--help` option.

```
$ molehill -h
Generate Workflow template files.

USAGE:
    molehill [OPTIONS]

FLAGS:
    -h, --help       Prints help information
    -V, --version    Prints version information

OPTIONS:
    -o, --output <PATH>      Output file path.
    -t, --template <PATH>    Set Digdag workflow template directory.
```

The tool generates files wihout options like:

```
$ molehill
```

If you run `molehill` without option, generates [default files](https://github.com/akito19/molehill/tree/main/src/examples).
Thus, when you have already template directory within your machine, `--template` option is available:

```
$ molehill -t path/to/template
```

Note that if you have nested directory within a template directory, the nested one will be ignored.

## Development

```
$ git clone https://github.com/akito19/molehill.git
$ cd molehill
$ cargo build // Build
$ cargo test // Run unit tests
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/akito19/molehill.
