# Deployment via GUnicorn.

# Needs pyyaml & gunicorn to run.
gunicorn -k api.workers.MyUvicornWorker -w 2 main:create_app