TEMPD=$(mktemp -d)
# Dump the production database to a temporary file
mysqldump -u maria -p submission_ws > "$TEMPD"/submission_ws.sql
# Load the temporary file into the development database
mysql -u maria -p submission_ws_dev < "$TEMPD"/submission_ws.sql
