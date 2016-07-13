# Contributing to Notebook Molecular Visualization


<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Contributing to Notebook Molecular Visualization](#contributing-to-notebook-molecular-visualization)
    - [Tips and guidelines](#tips-and-guidelines)
        - [Pull requests are always welcome](#pull-requests-are-always-welcome)
    - [Submission Guidelines](#submission-guidelines)
        - [Project Roles](#project-roles)
        - [Timing](#timing)
        - [Issues](#issues)
        - [Pull Requests](#pull-requests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- to generate: npm install doctoc: doctoc --gitlab --maxlevel 3 CONTRIBUTING.md-->



## Tips and guidelines

### Pull requests are always welcome

If your change is anything more significant than. Any significant improvement should be
documented as [a GitHub issue](https://github.com/autodesk/notebook-molecular-visualization/issues) before
starting work.


## Submission Guidelines

### Maintainers
Maintainers are responsible for responding to pull requests and issues, as well as guiding the direction of the project.

Aaron Virshup - Lead developer and maintainer<br>
Dion Amago - Maintainer<br>
Malte Tinnus - Maintainer

If you've established yourself as impactful contributors for the project, and are willing take on the extra work, we'd love to have your help maintaining it! Email the maintainers list at `moldesign_maintainers@autodesk.com` for details.

### Timing

We will attempt to address all issues and pull requests within one week. It may a bit longer before pull requests are actually merged, as they must be inspected and tested. 

### Issues

If `nbmolviz` isn't working like you expect, please open a new issue! We appreciate any effort you can make to avoid reporting duplicate issues, but please err on the side of reporting the bug if you're not sure.

Providing the following information will increase the chances of your issue being dealt with quickly:

* **Overview of the Issue** - Please describe the issue, and include any relevant exception messages or screenshots.
* **Environment** - Include relevant results of `pip freeze`, and your system configuration.
* **Help us reproduce the issue** - Please include code that will help us reproduce the issue. For complex situations, attach a notebook file.
* **Related Issues** - Please link to other issues in this project (or even other projects) that appear to be related 

### Pull Requests

Before you submit your pull request consider the following guidelines:

* Search GitHub for an open or closed Pull Request that relates to your submission. You don't want to duplicate effort.
* Make your changes in a new git branch:

     ```shell
     git checkout -b my-fix-branch [working-branch-name]
     ```

* Create your patch.
* Commit your changes using a descriptive commit message.

     ```shell
     git commit -a
     ```
  Note: the optional commit `-a` command line option will automatically "add" and "rm" edited files.

* Push your branch to GitHub:

    ```shell
    git push origin my-fix-branch
    ```

* In GitHub, send a pull request to `notebook-molecular-visualization:dev`
* Before any request is merged, you'll need to agree to the contribution boilerplate. Email us at `moldesign_maintainers@autodesk.com` for details. 
