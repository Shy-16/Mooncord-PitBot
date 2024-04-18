module.exports = {
    apps: [{
        name: 'release_task',
        interpreter: 'poetry run python3',
        script: "release_task.py",
        instances: 1,
        exec_mode: 'fork',
        cron_restart: "*/5 * * * *",
        watch: false,
        autorestart: false
    }],
}