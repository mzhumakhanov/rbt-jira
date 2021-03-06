# rbt-jira
integrating reviewboard and jira

## Installation
Just do a git clone. If you want to help in development, first fork and clone your own fork. :) 

## Required packages and their installation
rbt-jira is a written in python and requires python runtime to work. The recommended version is 2.7. Other than the bare-minimum installation of python, it requires a couple of packages to be installed: `argparse`, `rbtools`, `jira`

So for the uninitiated, the recommended way of installing python packages is `pip`. If you don't have `pip`, please install it. `pip` can be installed by `easy_install`(easy_install pip). If you don't even have `easy_install`  , then install [setuptools](https://pypi.python.org/pypi/setuptools). For installing setuptools, download the tarball, extract, go in the directory and do `python setup.py install`. Ultimately, you'll have `pip`, and you can do the following:

    pip install argparse rbtools jira # might have to do sudo
  
After installations, you should be ready to use the program.


## Usage
Go to your project's directory. e.g. I'm using it to work on `apache incubator lens`, so I'll do `cd /path/to/clone/of/incubator-lens`. I've already cloned `rbt-jira` on my system in path `/path/to/clone/of/rbt-jira`. I'll make sure I have the following things inside `/path/to/clone/of/incubator-lens/.reviewboardrc`:
    
    REVIEWBOARD_URL = "https://reviews.apache.org/"
    REPOSITORY = "lens"
    BRANCH = "master"
    TARGET_GROUPS = 'lens'
    GUESS_FIELDS = True

I'll assume you are using reviewboard(of course) and can understand what the above lines mean. So just change them accordingly. 

This is what help for the command shows:

      $ python /path/to/clone/of/rbt-jira -h
      usage: /path/to/clone/of/rbt-jira [-h] [action] [-j [JIRA [JIRA ...]]] [-b BRANCH] [-s SUMMARY]
                         [-d DESCRIPTION] [-r REVIEWBOARD] [-t TESTING_DONE]
                         [-c COMMENT] [-p]
                         
      
      rbt jira command line tool
      
      positional arguments:
        action                action of the command. One of post-review, submit-patch, commit and clean
      
      optional arguments:
        -h, --help            show this help message and exit
        -j [JIRA [JIRA ...]], --jira [JIRA [JIRA ...]]
                              JIRAs.
        -b BRANCH, --branch BRANCH
                              Tracking branch to create diff against
        -s SUMMARY, --summary SUMMARY
                              Summary for the reviewboard
        -d DESCRIPTION, --description DESCRIPTION
                              Description for reviewboard
        -r REVIEWBOARD, --rb REVIEWBOARD
                              Review board that needs to be updated
        -t TESTING_DONE, --testing-done TESTING_DONE
                              Text for the Testing Done section of the reviewboard
        -c COMMENT, --comment COMMENT
                              What to comment on jira
        -p, --publish         Whether to make the review request public
        
        
`action` can be `post-review`, `submit-patch`, `commit`, `clean`.

It's expected that you run the command in the directory that contains `.reviewboardrc`. So I'd run the command inside `/path/to/clone/of/incubator-lens/`.

### Post review
You either provide a jira id in `-j`, or it tries to deduce jira id from your git branch. Other than jira id, it needs reviewboard id if a request already exists. You can either provide that, or let it deduce itself from the jira id. For that, it keeps a locally stored mapping. If not found in the mapping, it falls back to looking at the issue's comments if a reviewboard url is mentioned. So if not provided, not found in the local mapping and no comments on the issue mentioning this, it assumes a new review request needs to be created. Otherwise it will try and update an already existing review request. 

In any case, it first uploads the new diff to the review request. The diff will be generated using `git diff $BRANCH..HEAD`. `BRANCH` can be provided in arguments but defaults to the value of BRANCH in the `.reviewboardrc`. 

if `SUMMARY` is provided, it's chosen to be the review request's summary. If not, summary is updated only when it's blank in the review request(which will happen if a new request was created). If blank, summary of the issue is picked and copied in review request's summary. Similar logic applies to the description of the review request.

If `TESTING_DONE` is provided, the review request is updated with the new value. 

If `publish` flag is on, the review request is made public. The first time the review request is made public, a comment will be added on the issue mentioning the review request. 


### Submit patch
Submit patch -- like post review -- checks if a corresponding reviewboard entry exists. If yes, it takes patch from the review board entry. If not, it checks the diff using `git diff $BRANCH..HEAD`. If diff is small enough, takes patch from there. If not, it recommends you create a reviewboard entry and exits.

After it has patch, it adds it to the issue as attachment, marks it patch available and posts a comment on the jira. 

Just like post-review, it needs `-j` argument, but can deduce from current branch name. 


### Commit
not yet implemented

### Clean
not yet implemented


## Optimal workflow for contributor
Keep your `$BRANCH` in sync with apache repo's `$BRANCH`. i.e. do not do any work on that branch. It shouldn't (ideally) matter whether you have forked the repo before cloning or not. Whenever you work on a jira, create a branch with the issue name(e.g. LENS-26) and work on that. 

git commits can be checkpoints(e.g. when you have to switch branch, you'll perform a checkpoint commit). So I've kept `committing` separate from `post-review`. Once you are sure you want to push a review request, do `rbt-jira post-review`. This will create the review request. You can open that, most of the fields will be already set. 

Generally when you create a review request, you get to see the diff and you decide some of the changes need rectifying. You will now browse through the diff of your review request (which is not published yet), make changes on your local, and once done, do a `git commit` followed by `rbt-jira post-review -p`. This will publish the request. You can provide `-d`, `-s`, `-t` as and when required. 

Another general assumption is that jira summary is the symptom of the problem. reviewboard summary can mention what is the actual change. So you'll provide summary once (anytime when you are doing post-review) and that will permanently become the summary of the review request.

Once you see that your review request is approved, you can do `rbt-jira submit-patch`. You can use this command also when you have made a very small change and directly want to submit patch to jira. 

For both of the commands, all changes you intend to send across must be committed. 
