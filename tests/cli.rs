use assert_cmd::prelude::*;
use predicates::prelude::*;
use std::process::Command;

use std::fs;
use std::path::Path;
use std::error::Error;

fn setup_dir(dir: &str) {
    fs::create_dir_all(dir).unwrap();
}

fn clean_dir(dir: &str) {
    fs::remove_dir_all(dir).unwrap();
}

#[test]
fn invvalid_template_option_short() -> Result<(), Box<dyn Error>> {
    let mut cmd = Command::cargo_bin("molehill")?;

    cmd.arg("-t").arg("path/to/file.txt");
    cmd.assert().failure()
        .stderr(predicate::str::contains("Specify directory path for `-t` / `--template` option."));

    Ok(())
}

#[test]
fn invalid_template_option_long() -> Result<(), Box<dyn Error>> {
    let mut cmd = Command::cargo_bin("molehill")?;

    cmd.arg("--template").arg("path/to/file.txt");
    cmd.assert().failure()
        .stderr(predicate::str::contains("Specify directory path for `-t` / `--template` option."));

    Ok(())
}

#[test]
fn invalid_output_option_long() -> Result<(), Box<dyn Error>> {
    let mut cmd = Command::cargo_bin("molehill")?;
    let pathname = "path/to/dir";

    cmd.arg("--output").arg(pathname);
    cmd.assert().success()
        .stdout(predicate::str::contains(pathname));

    clean_dir("path");
    Ok(())
}

#[test]
fn valid_output_option() -> Result<(), Box<dyn Error>> {
    let mut cmd = Command::cargo_bin("molehill")?;
    let dir = "foo/bar";
    setup_dir(dir);

    cmd.arg("-o").arg("foo/bar");
    cmd.assert().success()
        .stdout(predicate::str::contains("Generated Digdag workflow files!"));

    assert!(Path::new("foo/bar/mailchimp.py").exists());
    assert!(Path::new("foo/bar/notification.dig").exists());
    assert!(Path::new("foo/bar/config.dig").exists());
    assert!(Path::new("foo/bar/sample.sql").exists());
    assert!(Path::new("foo/bar/template_ja.html").exists());
    assert!(Path::new("foo/bar/template_en.html").exists());

    clean_dir("foo");
    Ok(())
}

#[test]
fn valid_template_option() -> Result<(), Box<dyn Error>> {
    let mut cmd = Command::cargo_bin("molehill")?;

    cmd.arg("-t").arg("tests/template_example");
    cmd.assert().success()
        .stdout(predicate::str::contains("Generated Digdag workflow files!"));

    assert!(Path::new("foo.dig").exists());
    assert!(Path::new("bar.sql").exists());

    fs::remove_file("foo.dig").unwrap();
    fs::remove_file("bar.sql").unwrap();
    Ok(())
}

#[test]
fn without_options() -> Result<(), Box<dyn Error>> {
    let mut cmd = Command::cargo_bin("molehill")?;
    cmd.assert().success()
        .stdout(predicate::str::contains("Generated Digdag workflow files!"));

    assert!(Path::new("notification.dig").exists());
    assert!(Path::new("config.dig").exists());
    assert!(Path::new("mailchimp.py").exists());
    assert!(Path::new("sample.sql").exists());
    assert!(Path::new("template_ja.html").exists());
    assert!(Path::new("template_en.html").exists());

    fs::remove_file("notification.dig").unwrap();
    fs::remove_file("config.dig").unwrap();
    fs::remove_file("mailchimp.py").unwrap();
    fs::remove_file("sample.sql").unwrap();
    fs::remove_file("template_ja.html").unwrap();
    fs::remove_file("template_en.html").unwrap();
    Ok(())
}

#[test]
fn with_options() -> Result<(), Box<dyn Error>> {
    let mut cmd = Command::cargo_bin("molehill")?;
    let dir = "baz";
    setup_dir(dir);

    cmd.arg("--template").arg("tests/template_example")
        .arg("--output").arg("baz");
    cmd.assert().success();

    assert!(Path::new("baz/bar.sql").exists());
    assert!(Path::new("baz/foo.dig").exists());

    clean_dir(dir);
    Ok(())
}
