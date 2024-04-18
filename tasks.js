const { execSync } = require('child_process');

console.log("running release task...");
console.log(execSync('poetry run python3 release_task.py'));
console.log("release complete");
