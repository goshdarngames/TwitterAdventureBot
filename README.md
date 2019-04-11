Twitter Adventure Bot
=====================

A work-in-progress twitter bot that allows multiple users to play an 
Interactive Fiction game together.

Build Instructions
==================

Before building the repo you must include the project's git sub-modules:

    git submodule init

The project uses Docker to combine all its elements into a single 
image for execution.

The Dockerfile is in the root folder and can be built with this command:

    docker build -t 'tab:1' .


Project Structure
=================

Purpose of directories within the project:
    
    * VIRTUAL 
        - Python3 virtualenv for running and developing the system. 

    * game-runner 
        - Python modules for running the games. 

    * frotz
        - Git sub-module containing the frotz z-machine interpreter.
          https://gitlab.com/DavidGriffith/frotz
