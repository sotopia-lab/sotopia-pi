#!/bin/bash

# Define the commit range
START_COMMIT="c8dfe91d6a17a8390d382affd187f9b162364e2f^"
END_COMMIT="d22e560192616ba09fb5e7f0515b22491e7f44d9"

# Set merge strategy to "theirs"
git config --global merge.conflictStyle diff3
git config --global merge.defaultToUpstream false

# List all commits in the range, in reverse order if needed
COMMITS=$(git rev-list --reverse $START_COMMIT..$END_COMMIT)

for COMMIT in $COMMITS; do
    # Extract the author date, name, and email of the commit
    AUTHOR_DATE=$(git show --format=%aD -s $COMMIT)
    AUTHOR_NAME=$(git show --format=%aN -s $COMMIT)
    AUTHOR_EMAIL=$(git show --format=%aE -s $COMMIT)
    
    # Set environment variables to preserve the authorship exactly as it was
    export GIT_COMMITTER_DATE="$AUTHOR_DATE"
    export GIT_AUTHOR_NAME="$AUTHOR_NAME"
    export GIT_AUTHOR_EMAIL="$AUTHOR_EMAIL"
    
    # Cherry-pick the commit without adding any signatures
    if git cherry-pick -x $COMMIT; then
        # Reset the GIT_COMMITTER_DATE to avoid affecting subsequent git operations
        unset GIT_COMMITTER_DATE
    else
        # Resolve conflicts by always choosing the latest version (theirs)
        git checkout --theirs .
        git add .
        
        # Continue with the cherry-pick
        git cherry-pick --continue
        unset GIT_COMMITTER_DATE
    fi
done

