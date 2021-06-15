# MoleHill

MailMole is a tool that generates a [Digdag](https://www.digdag.io/) workflow template. The template helps to create Digdag workflow for sending a campaign via [MailChimp](https://mailchimp.com/):

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
$ molehill
```

### Development

```
$ git clone https://github.com/akito19/molehill.git
$ cd molehill
$ cargo build // Build
$ cargo test // Run unit tests
```

