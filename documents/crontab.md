### setting crontab

when your OS is macOS or Linux :

```
$ crontab -e
```

Add a task as shown below:

```
50 * * * * curl -X PATCH http://127.0.0.1:8000/push >> /YOUR/PATH/logfile 2>&1
```

In the example above,

- **50 \* \* \* \* command** : Run the command every hour and 50 minutes.
- **>> /YOUR/PATH/logfile** : means that the execution result of the command is additionally written to the /YOUR/PATH/logfile.
- **2>&1** redirects standard errors to standard output so that errors are also recorded.

To output a log file to a terminal, modify the operation as follows:

```
50 * * * * curl -X PATCH http://127.0.0.1:8000/push | tee /YOUR/PATH/logfile
```
