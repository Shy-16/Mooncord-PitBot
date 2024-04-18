// used to setup chron jobs to re-run tasks like un-pitting people

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