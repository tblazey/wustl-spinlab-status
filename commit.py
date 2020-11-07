#!/usr/bin/python

#Load libraries
from datetime import datetime
from git import Repo

#Commit
repo_dir = r'C:\Users\polarice\Documents\Github\wustl-spinlab-status'
repo_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
repo = Repo(repo_dir)
repo.index.add('temp_data.csv')
repo.index.add('assets/current.png')
repo.index.commit(repo_time)
origin = repo.remote()
origin.push()
