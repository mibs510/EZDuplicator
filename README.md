![EZ Duplicator](https://files.ezduplicator.com/f.php?h=2nyeqxyT&p=1)

A simple easy-to-use mass USB cloning/duplication GUI application that offers most (often more) 
features commonly found on commercially available products. 

![EZ Duplicator App](https://files.ezduplicator.com/f.php?h=2HDChfOu&p=1)


# Development
The following steps are needed to start hacking away:
1. Install [Ubuntu 20.04](https://ubuntu.com/download/desktop/thank-you?version=20.04.3&architecture=amd64)
2. Download and install
   1. [PyCharm](https://www.jetbrains.com/pycharm/download/#section=linux)
   2. [Glader](https://github.com/welbornprod/glader)
3. Install [Git Commit Template](https://plugins.jetbrains.com/plugin/9861-git-commit-template)
   1. Required to comply with Semantic Versioning Specification ([semver](https://semver.org/))
4. Clone this GitHub repo
   1. In the Welcome to PyCharm wizard, select Get from VCS
5. Run `EZDuplicator/EZDuplicator/utils/setup.sh` from a terminal to install all necessary system packages.
   1. **NOTE**: `setup.sh` should be run in the same directory in which this README.md file is located in.
6. Download [.pypirc](https://help.ezduplicator.com) and place it into your home directory `/home/<username>/.pypirc`
   1. TODO: Update file download link. Link will be posted in Bookstack as soon as the developer book is published.

### Development Cycle
1. 🌟🎊 Fix/add/improve code. 🎩🧙
   1. Use Glade to edit `EZDuplicator/res/window.ui` (pre-installed by running `setup.sh`)
   2. Use [Glader](https://github.com/welbornprod/glader) to generate Gtk.Dialog/Window/* Classes easily (**NOT** pre-installed by running `setup.sh`. Manual installation and setup required.)
2. Upload wheel package onto the development repository by selecting mkpypi-dev Run/Debug Configuration on the top right-hand corner and running (Shift + F10)
   1. ![mkpipy-dev](https://files.ezduplicator.com/f.php?h=3Hk1lBD6&p=1)
3. Test changes on the developer candidate 
   1. Verify developer candidate Update Repository is set to "Development" under Settings > Update Repository 
   2. Changes must pass the following criteria:
      1. It basically shouldn't break/affect any existing code. 
         1. TODO: Draft a document outlining minimum tests required for a pull request to merge with the master branch 
4. Submit a pull request. A pull request must be of significance. This means that each pull request (or commit) must trigger at least a minor (Y) or a patch (Z) bump to the version (X.Y.Z)
   1. Commits will typically be categorized as either a fix or a feature
      1. Use Git Commit Template to submit a proper commit message
5. Upon approval, maintainer will merge pull request with the master branch which triggers GitHub to upload new package onto the custom Production pypi server.

### Updates
There are two repositories where updates are pushed to.
Stable and tested updates are pushed onto the "Production" repository. The "Development" repository is meant to be isolated from
the production repository and where developers can push to test and
develope the application further. This repository is only available to developers only.

**WARNING:** Updates in the "Production" repository are pushed by GitHub via CI/pushes! This means that as a developer
you must be certain that what you push or pull request onto GitHub has been tested **100%** and deemed stable enough for our customer's
experience. Anything pushed onto the master branch is available to our customers as "updates".
Also, verify that the update process does **NOT** brick the product. Pushes/merges to the master branch
should only be done so by the author (Connor McMillan) or an appointed maintainer.