# Learner
# Facilitator
# Mentor


# from nin (first, last, phone_number, gender, state)


# What is the best approch here
# Is it okey to run query for student/learner count for mentor or add learner_count field and update it on every student assign
    


# Example of Facilitator specializations 
# (Literature, Data Science, Graphic Design, Web Development, Digital Marketing, Cybersecurity,
#   Mobile App Development, UI/UX Design, AI Research, Business Analysis, Information Technology )

# User
    # first_name
    # last_name
    # email
    # phone_number
    # last_active
    # role (Learner, Mentor, Facilitator)
    # status (Active, Inactive, Disable) -> default to Disable



# Learner
    # account_type -> (student, professional)
    # learning_track (will get list of learning track put empty list or place holder)
    # skill_cluster (will get list of skill cluster)
    # work_type (All, Onsite, Remote)
    # industrial_prefrence (get list of industrial prefrence)
    # portfolio_link
    # state (list of nigerial state)
    # gender (Male, Female)
    # resume -> file upload | nullable
    # mentor -> link back to user mentor (relationship)

# Facilitator
    # specialization
    # highest_qualification
    # institusion
    # areas_of_expertise
    # learner_count

# Mentor
    # country
    # state
    # specialization
    # highest_qualification
    # institusion
    # areas_of_expertise




# I'm working on a skill assessment application in which there are four type of users, the screenshort show sample tables
# for learners, facilitators and mentors, I also have user form detail below 
# I want to come up  with a custom user model

# Note:
#     Im using django (djangorestframework)
#     perfomance query is of consign here
#     the administrator is the fourth type of user (does not need a form)
#     take note of mentee/learner current and overall count from the mentor display table
#     what can possibly be cateria for mentor rating


# INFORMATION FROM ADD/CREATE FORMS FOR LEARNER, MENTOR AND FACILITATOR

# Common User information -> these apprear in learner, facilitator and mentor form i.e common fields
    # first_name
    # last_name
    # email
    # phone_number
    # last_active -> Not in form, this is here because of last active on all users display table
    # role (Learner, Mentor, Facilitator) -> Not in form, this is here for user role/type
    # status (Active, Inactive, Disable) -> Not in form, this is here because of status on all users display table



# Learner
    # account_type (student, professional)
    # learning_track 
    # skill_cluster
    # work_type (All, Onsite, Remote)
    # industrial_prefrence
    # portfolio_link
    # state (list of nigerial state)
    # gender (Male, Female)
    # resume -> file upload


# Facilitator
    # specialization
    # highest_qualification
    # institusion
    # areas_of_expertise
    # learner_count

# Mentor
    # country
    # state
    # specialization
    # highest_qualification
    # institusion
    # areas_of_expertise

