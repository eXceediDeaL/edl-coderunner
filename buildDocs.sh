echo 'Begin building docs...'

set -e

# Create a clean working directory for this script.
rm -rf docs
mkdir docs
cd docs

# Get the current gh-pages branch
git clone -b gh-pages https://git@$GH_REPO_REF .

##### Configure git.
# Set the push default to simple i.e. push only the current branch.
git config --global push.default simple
# Pretend to be an user called Travis CI.
git config user.name "Travis CI"
git config user.email "travis@travis-ci.org"

# Remove everything currently in the gh-pages branch.
# GitHub is smart enough to know which files have changed and which files have
# stayed the same and will only update the changed files. So the gh-pages branch
# can be safely cleaned, and it is sure that everything pushed later is the new
# documentation.

################################################################################
##### Generate the Doxygen code documentation and log the output.          #####
echo 'Generating docs'
# Redirect both stderr and stdout to the log file AND the console.
pwd
cd ..
make test
make cover
cd docs

################################################################################
##### Upload the documentation to the gh-pages branch of the repository.   #####
# Only upload if Doxygen successfully created the documentation.
# Check this by verifying that the html directory and the file html/index.html
# both exist. This is a good indication that Doxygen did it's work.
echo 'Uploading documentation to the gh-pages branch...'
git add --all
git commit -m "Deploy docs to GitHub Pages Travis build: ${TRAVIS_BUILD_NUMBER}" -m "Commit: ${TRAVIS_COMMIT}"
git push --force "https://${GH_REPO_TOKEN}@${GH_REPO_REF}" > /dev/null 2>&1
