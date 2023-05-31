# How to issue a regionmask release in n easy steps

Time required: about an hour.

These instructions assume that `upstream` refers to the main repository
(<https://github.com/regionmask/regionmask>).

<!-- markdownlint-disable MD031 -->

1. Ensure your main branch is synced to upstream:
   ```sh
   git switch main
   git pull upstream main
   ```
1. Maybe write a release summary: ~50 words describing the high level features.
1. Look over whats-new.rst and the docs. Make sure "What's New" is complete
   (check the date!) and add the release summary at the top.
1. Open a PR with the release summary and what's new changes.
1. After merging, again ensure your main branch is synced to upstream:
   ```sh
   git pull upstream main
   ```
1. Check that the tests and ReadTheDocs build is passing!
1. Tag the release:
   ```sh
   git tag -a v0.X.Y -m 'v0.X.Y'
   ```
1. Ensure the dependencies for building are installed:
   ```sh
   mamba update pip
   python -m pip install build twine
   ```
1. Build source and binary wheels for PyPI:
   ```sh
   git clean -xdfn  # This removes any untracked files! - Dry run -
   ```
   For real
   ```sh
   git clean -xdf  # This removes any untracked files!
   git status # check for tracked files
   git restore -SW .  # This removes any tracked changes!
   python -m build
   ```
1. Use twine to check the package build:
   ```sh
   twine check --strict dist/regionmask*
   ```
1. Use twine to register and upload the release on PyPI. Be careful, you can't take this
   back!
   ```sh
   twine upload dist/*
   ```
   You will need to be listed as a package owner at <https://pypi.python.org/pypi/regionmask>
   for this to work.
1. Push your changes to main:
   ```sh
   git push upstream main
   git push upstream --tags
   ```
1. Add a section for the next release to doc/whats-new.rst:
   ```rst

   v0.X.Y (unreleased)
   --------------------

   Breaking Changes
   ~~~~~~~~~~~~~~~~

   Enhancements
   ~~~~~~~~~~~~

   Deprecations
   ~~~~~~~~~~~~

   New regions
   ~~~~~~~~~~~

   Bug Fixes
   ~~~~~~~~~

   Docs
   ~~~~

   Internal Changes
   ~~~~~~~~~~~~~~~~

   ```
1. Issue the release on GitHub. Click on "Draft a new release" at
   <https://github.com/regionmask/regionmask/releases>. Type in the version number
   and paste the release summary in the notes.
1. Update zenodo link.
1. Commit your changes and push to main again:
   ```sh
   git commit -am 'New whatsnew section'
   git push upstream main
   ```
   You're done pushing to main!
1. Check if the new docs get built. Login to <https://readthedocs.org/projects/regionmask/versions/>.
1. Release regionmask on conda - also update the requirements in meta.yaml <https://github.com/conda-forge/regionmask-feedstock>

<!-- markdownlint-enable MD013 -->

## Credit

These instructions were copied from xarray.
