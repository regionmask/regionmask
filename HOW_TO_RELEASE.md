# How to issue a regionmask release in n easy steps

Time required: about an hour.

These instructions assume that `upstream` refers to the main repository
(<https://github.com/regionmask/regionmask>).

<!-- markdownlint-disable MD031 -->

 1. Ensure your master branch is synced to upstream:
     ```sh
     git switch master
     git pull upstream master
     ```
 2. Maybe write a release summary: ~50 words describing the high level features.
 3. Look over whats-new.rst and the docs. Make sure "What's New" is complete
    (check the date!) and add the release summary at the top.
 4. Open a PR with the release summary and whatsnew changes.
 5. After merging, again ensure your master branch is synced to upstream:
     ```sh
     git pull upstream master
     ```
 7. Check that the tests and ReadTheDocs build is passing!
 8. Tag the release (remove the curly braces):
      ```sh
      git tag -a v{0.X.Y} -m 'v{0.X.Y}'
      ```
 9. Ensure the dependencies for building are installed:
      ```sh
      mamba update pip
      python -m pip install setuptools setuptools-scm wheel twine check-manifest
      ```
10. Build source and binary wheels for PyPI:
      ```sh
      git clean -xdfn  # This removes any untracked files! - Dry run -
      git clean -xdf  # This removes any untracked files!
      git status # check for tracked files
      git restore -SW .  # This removes any tracked changes!
      python setup.py bdist_wheel sdist
      ```
11. Use twine to check the package build:
      ```sh
      twine check dist/regionmask*
      ```
12. Use twine to register and upload the release on PyPI. Be careful, you can't
    take this back!
      ```sh
      twine upload dist/regionmask-{0.X.Y}*
      ```
    You will need to be listed as a package owner at
    <https://pypi.python.org/pypi/regionmask> for this to work.
13. Push your changes to master:
      ```sh
      git push upstream master
      git push upstream --tags
      ```
14. Update the stable branch (used by ReadTheDocs) and switch back to master:
     ```sh
      git switch stable
      git rebase master
      git push --force upstream stable
      git switch master
     ```
    It's OK to force push to `stable` if necessary.
15. Add a section for the next release {0.X.Y+1} to doc/whats-new.rst:
     ```rst
     .. _whats-new.{0.X.Y+1}:

     v{0.X.Y+1} (unreleased)
     ---------------------

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
16. Commit your changes and push to master again:
      ```sh
      git commit -am 'New whatsnew section'
      git push upstream master
      ```
    You're done pushing to master!
17. Issue the release on GitHub. Click on "Draft a new release" at
    <https://github.com/regionmask/regionmask/releases>. Type in the version number
    and paste the release summary in the notes.
18. Update the docs. Login to <https://readthedocs.org/projects/regionmask/versions/>
    and switch your new release tag (at the bottom) from "Inactive" to "Active".
    It should now build automatically.
19. Release regionmask on conda - also update the requirements in meta.yaml <https://github.com/conda-forge/regionmask-feedstock>

<!-- markdownlint-enable MD013 -->

## Credit

These instructions were copied from xarray.
