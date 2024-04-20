const { execSync } = require('child_process');

require('dotenv').config();

console.log("running release task...");
console.log(execSync('poetry run python3 release_task.py --token ' + process.env.DISCORD_TOKEN));
console.log("release complete");
