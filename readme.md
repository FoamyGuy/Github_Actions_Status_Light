## Setting up your API token as an environment variable

### Linux / Mac
- Create a file named `.env.sh`. Or something else if you prefer.
- Inside of it put this:
```shell
export GITHUB_API_TOKEN="ghp_yourtokenvaluehere"
```
- Substitute in your own GitHub Personal Access Token inside the quotes and save the file.
- Once the file is created run this command in a terminal:
```shell
source .env.sh
```
- Now the `GITHUB_API_TOKEN` environment variable will be available for use by the python script.
- In the same terminal run this to start the status listener
```shell
python3 github_actions_status_watcher.py
```

### Windows
Not sure. If anyone knows this process for modern windows please create issue or PR.