# Password is in ../secrets/postgres_passwd
cat ../secrets/postgres_passwd
echo ""
# change the required port 5401, 5402 or 5403

psql --host=localhost --port=5403 --username=postgres --dbname=postgres
