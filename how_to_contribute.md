# How to contribute in the code of this repo

## Requirements
```
git clone git@github.com:vschellervidal/geneweb_python.git
cd geneweb_python
```

## Create a ticket (issue)
1. Go to Issues -> ```New issue```
2. Clear title (ex: ameliorer le README) (⚠️ don't use accents or quotes)
3. Briefly describe what to do
4. Create the issue ```Create```

The bot will automatically create a new ```branch``` from ```main``` with the name of the issue.
Example: ```issue-1-ameliorer-le-readme```

## Go to the issue branch
1. Fetch remotes branches ```git fetch```
2. Go to the issue branch ```git switch issue-1-ameliorer-le-readme```

## Make your changes
0. Code what describe your issue
1. See modifying files ```git status```
2. Add files ```git add README.md```
3. Commit with a concise message ```git commit -m "ajouter section installation rapide"```
4. Push ```git push -u origin issue-1-ameliorer-le-readme```

At the first push, the bot will automatically open au ```Pull Request``` on ```main```

## Review a Pull Request
In coming...

## Go back to main
1. ```git switch main```
2. Delete the local branch of the ticket ```git branch -D issue-1-ameliorer-le-readme```
