# Introduction to Git, Part 1

## Setting up

For this lab, pair up with someone else. Open your terminal. If you have
questions about how to access your terminal, ask your teammate.

Now make sure both of you have Github accounts by typing the following into
your terminal:

```bash
$ git --version
```

Note: I am working on a Mac. If you are using Windows and want to know the
Windows versions of terminal commands, there's a look-up table [here](http://www.lemoda.net/windows/windows2unix/windows2unix.html).

If you don't already have Git installed, do that now:

Create a [Github account](http://github.com).

Download and install the latest version of [Git](http://git-scm.com/downloads).

Configure Git with your name and email by typing the following into your terminal:

```bash
$ git config --global user.name "YOUR NAME"
$ git config --global user.email "YOUR EMAIL ADDRESS"
```

Now [create a new repository](https://github.com/new). Add a title and a
description, set the repo to Public, initialize with a _README_, and click Create.
Don't give your repos the same names!


## Working with a repository

Next, clone your empty repo. Look in the bottom righthand corner of the repo
page on Github to find the URL. The default is an HTTPS clone, which is fine to
use. There are other choices, like SSH, which you can read more about [here](https://help.github.com/articles/which-remote-url-should-i-use/).
"""

### Now in your terminal, type:

```bash
$ git clone PASTE THE URL HERE myclone
$ cd myclone
```

Then add some content to the empty myclone folder. Some simple text documents would be good.

Now add and commit those changes.

```bash
$ git add --all
$ git commit -m "A few additions."
```

Note: git add -all can be a bit ham-fisted and is not the only option. You can precision-add files using git add _FILENAME_.


View the log and push the changes back to Github.

```bash
$ git log
$ git push origin master
```

View your changes on the repo webpage.


## Breaking Git
#### Don't worry, you won't actually break it.

Now, clone your teammate's repo. Hopefully you gave your repos different names!

```bash
$ git clone (PASTE TEAMMATE URL HERE) teamclone
$ cd teamclone
```

Make more changes! Add some new files, commit them, and push back to the master.

Remember these 6 commands:
```
$ git add --all                      #Stage all the changes
$ git add (FILENAME)                 #Just stage one updated file
$ git status                         #Check the status to see changes/staged
$ git commit -m "Unique message."    #Commit the changes
$ git log                            #See the commit history
$ git push origin master             #Push the commits back to Github
```
Now, both teammates should edit the same line on the same file, and try to add, commit, and push changes back to Github.


What happened??


## Conflict Resolution
The first person to push the changes is successful.

The next person gets a failure message when they try to push. If they then type:

```bash
$ git pull  #syncs up with current repo version (combo of git fetch + git merge)
```

... Git sends a merge conflict error message:


This is called a merge conflict. Git tells you to fix the conflicts and then commit the result. Now let's resolve the merge conflict.
Use the error message to identify which file caused the conflict. Open that file in your text editor.

The file shows the changes made by both parties. The first section is the version of the current branch head. The second section is the version of master branch.
Let's decide to be nice in order to resolve the conflict. Edit the file accordingly. Then run:

```bash
$ git add [NAME OF FIXED FILE]
$ git commit -m "Fixed merge conflict."
$ git push origin master
```

Nice job! For more on advanced Git topics, check out [Pro Git](http://git-scm.com/book/en/v2) by Scott Chacon and Ben Straub.
