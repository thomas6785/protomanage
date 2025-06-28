Suite of tools for register map management.

See full project documentation at
https://amd.atlassian.net/wiki/spaces/RFDCDEV/pages/867305545/

docs_gen is used to automatically update SOME of the documentation in the Confluence hierarchy linked above.

requirements.txt outlines requirements for developers contributing to this project - it is not needed to run the scripts.
Developers can run 'make venv-init' to initialise a Python venv with the necessary packages to develop and test this suite of tools.

'make dist' can be used to package a distribution in ./dist
The version number is taken from the git tag - if no tag has been assigned to the current commit, it will default to version 0.dev0