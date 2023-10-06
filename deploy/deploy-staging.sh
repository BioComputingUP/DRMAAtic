#!/usr/bin/bash
set -e
# Set the source and destination directories
SRC_DIR=.
DEST_DIR=django@perse:/var/django/apps/drmaatic-dev

# Set the exclude list
EXCLUDE_LIST=(.git .gitignore .gitmodules LICENSE README.md tests static figures logger.log .idea __pycache__ migrations)
rsync -av --exclude-from=<(printf '%s\n' "${EXCLUDE_LIST[@]}") "$SRC_DIR"/ "$DEST_DIR"/

STATIC_DIR=./drmaatic/static
rsync -av --exclude-from=<(printf '%s\n' "${EXCLUDE_LIST[@]}") "$STATIC_DIR"/ "$DEST_DIR"/drmaatic/static/

# Run the post-deploy script with the environment as argument
ssh django@perse "cd /var/django/apps/drmaatic-dev ; bash -s" < ./deploy/post-deploy.sh staging

# Restart apache to reload the wsgi app
ssh aledc@perse "sudo -S apache2ctl -t && sudo -S apache2ctl restart"
