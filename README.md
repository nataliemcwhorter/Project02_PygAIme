# RL Connect4 MLAI Project
Im really cool I actually made a nice readME.

## Description
Hi Guys. This is my Reinforcement Learning AI Connect4 Game made with pycharm.
Basically, the AI learns how to play connect 4 through 3 different training modes: vs. self, vs. random, and vs. human.
It has no instruction on how to play Connect4 besides knowing that pieces can't be placed in full columns.
My model also isn't learning from opponents moves. It's rewards and learning memory is based solely on its own performance.
This proved to be a challenge because how can it get good if it doesn't know how to win and can't really learn how
You can also play against your AI. Most options are available through the GUI accessed by running the main script.

Have fun I hope you like my project.

## Training
The 3 different modes are in order to best train the model. Random is good for starting out but the model will easily get comfortable
with just placing a piece in the same spot each time rather than strategizing 
because more likely than not the random moves is most unlikely to beat it.
The human play is theoretically the best because it is the best option for an opponent the model has at the moment. The human can make
strategic moves that then the AI, while not learning from the human, will learn from its reaction. Unfortunately, this approach is impractical
when thousands of training sessions are needed. Playing vs. self is good when there is a developed model. It is usually the best option for
after some training sessions with a human. It will play against the version of itself before the vs. self training session started and the
one model (not the opponent) will keep being updated throughout training. Training takes a very long time so **THIS IS YOUR WARNING** do not
go overboard with training sessions because it will not save if you stop midway through. I have spent too many times with my laptop open on my
passenger seat so I wouldn't loose my episodes. (I would say 14,000 episodes ~8 hours I think). You can also do it over and over again.

If you want to change how many episodes it is training, you can do so at the following location in the main script:

<img width="929" height="373" alt="Screenshot 2025-10-30 at 3 57 09 PM" src="https://github.com/user-attachments/assets/d39fdb8d-4115-41b7-9d1b-5cce353b0f33" />

## Loading and Saving Models
When I created this project, I knew it was going to take a long time and my model probably wasn't going to be very good. I thought it would be
smart to compare varying levels of badness to show that it was doing something. Sorry Mr. Cochran. If you're even reading this let me know.
Turns out I fixed my code and they were working pretty well. I also didn't name my models too well so not really sure which one is which. I must
say that these model names are better than my commits for FRC last year. Imagine a very long run on sentence with no spaces or differentiation 
between words. Yeah...

Anyways so I wanted to easily be able to access, differentiate, and create new models so old ones weren't getting written over. The GUI
allows you to choose which model you want to train and play against. additionally, if you want to create a new model, you can choose
a model name to save your model to at the following location in the main script:

<img width="988" height="561" alt="Screenshot 2025-10-30 at 4 17 04 PM" src="https://github.com/user-attachments/assets/83048d52-808d-4b90-8451-d504c98dcb13" />

## Gosh Natalie is so cool I wish I could be like her
yeah. the title says it all. I think that's all the important stuff, if not lmk. Have fun. It's pretty straightforwards. Also, Im always
accepting donations if u wanna spread the love. 🫡
