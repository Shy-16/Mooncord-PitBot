module.exports = {
    apps: [{
        name: 'release_task',
        script: "poetry run release_task.py",
        instances: 1,
        exec_mode: 'fork',
        cron_restart: "*/5 * * * *",
        watch: false,
        autorestart: false
    }],
}