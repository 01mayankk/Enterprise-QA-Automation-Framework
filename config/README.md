# Configuration Directory

This directory contains the central configuration files for the test automation framework.

## Contents
* `config.json`: Centralized configuration settings for environments, timeouts, browser choices, and file paths.

## Usage
The configuration parameters are loaded by `utils/config_loader.py` and used globally across tests and Page Objects to prevent hardcoding.
