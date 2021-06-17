# Molehill

Molehill is a tool that generates a [Digdag](https://www.digdag.io/) workflow template. The template helps to create Digdag workflow for sending a campaign via [Mailchimp](https://mailchimp.com/):

- Create an Audience.
- Set merge fields.
- Upload HTML template.
- Create a Campaign.

Note that it assumes using Treasure Data workflow.

### Install

```
$ cargo install --path .
```

### Usage

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

### Development

```
$ git clone https://github.com/akito19/molehill.git
$ cd molehill
$ cargo build // Build
$ cargo test // Run unit tests
```

