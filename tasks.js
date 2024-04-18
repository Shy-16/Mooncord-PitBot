const { execSync } = require('child_process');

execSync('poetry run python3 release_task.py');