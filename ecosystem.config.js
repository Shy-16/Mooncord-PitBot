// used to setup chron jobs to re-run tasks like un-pitting people
// starting from scratch? `pm2 start ecosystem.config.js`
// update to this config file? `pm2 reload ecosystem.config.js`
// need to kill all tasks in this file? `pm2 stop ecosystem.config.js`

module.exports = {
    apps: [{
        name: 'pitbot_tasks',
        script: "tasks.js",
        instances: 1,
        exec_mode: 'fork',
        cron_restart: "*/10 * * * *",
        watch: false,
        autorestart: false
    }],
}