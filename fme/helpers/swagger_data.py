import sys
from drf_yasg import openapi

def doc_response(entity, title):
    entity_data = getattr(sys.modules[__name__], entity)()
    return {
        '200': openapi.Response(
            description='200 description',
            examples={
                'application/json': {
                    **entity_data,
                }
            }
        ),
        **response_400(title)
    }

def doc_response_delete():
    return {
        '204': openapi.Response(
            description='204 description',
            examples={}
        ),
        **response_400('entity')
    }

def response_400(title):
    return {
        '400': openapi.Response(
            description='400 description',
            examples={
                'application/json': {
                    'message': f'Invalid request resource',
                }
            }
        ),
        '401': openapi.Response(
            description='401 description',
            examples={
                'application/json': {
                    'message': f'{title} is unauthorise resource',
                }
            }
        ),
        '404': openapi.Response(
            description='404 description',
            examples={
                'application/json': {
                    'message': f'{title} not found',
                }
            }
        )
    }

def empty():
    return {}

def nin_verification_first_step():
    return {
        'data': {
            'verification_id':'595e45af-08e3-4821-acc2-bf3ee2fbd167', 'message':'Nin verification process successfully started'
        }
    }

def nin_verification_final_step():
    return {
        'data': {
            'verification_id':'595e45af-08e3-4821-acc2-bf3ee2fbd167', 'msg':'Nin verification successfully'
        }
    }

def nin_verification_token_resend():
    return {
        'data': {
            'verification_id':'595e45af-08e3-4821-acc2-bf3ee2fbd167', 'msg':'Nin verification token successfully resend'
        }
    }

def list_learner_data():
    return {
        "data": {
            "links": {
                "next": None,
                "previous": None
            },
            "total": 1,
            "page_size": 10,
            "current": 1,
            "entity": [
                {
                    "user": {
                        "id": 4,
                        "email": "johnmail@gmail.com",
                        "first_name": "Odun",
                        "last_name": "Adebisi",
                        "phone_number": "+2348108012345",
                        "last_active": "2025-07-19T06:12:15.800334Z",
                        "role": "Learner",
                        "status": "Active"
                    },
                    "account_type": "Student",
                    "learning_track": "Web Development",
                    "skill_cluster": "Frontend",
                    "work_type": "Onsite",
                    "industrial_prefrence": "Tech",
                    "portfolio_link": "https://john.doe.com/portfolio",
                    "state": "LAGOS",
                    "gender": "Male",
                    "resume": "https://api.object-storage.prunedge.com/coursera-dev-storage/resume/receipt.pdf",
                    "progress": 0
                }
            ]
        }
    }


def doc_response(entity, title):
    entity_data = getattr(sys.modules[__name__], entity)()
    return {
        '200': openapi.Response(
            description='200 description',
            examples={
                'application/json': {
                    **entity_data,
                }
            }
        ),
        **response_400(title)
    }

def doc_response_delete():
    return {
        '204': openapi.Response(
            description='204 description',
            examples={}
        ),
        **response_400('entity')
    }

def response_400(title):
    return {
        '400': openapi.Response(
            description='400 description',
            examples={
                'application/json': {
                    'message': f'Invalid request resource',
                }
            }
        ),
        '401': openapi.Response(
            description='401 description',
            examples={
                'application/json': {
                    'message': f'{title} is unauthorise resource',
                }
            }
        ),
        '404': openapi.Response(
            description='404 description',
            examples={
                'application/json': {
                    'message': f'{title} not found',
                }
            }
        )
    }

def empty():
    return {}

def nin_verification_first_step():
    return {
        'data': {
            'verification_id':'595e45af-08e3-4821-acc2-bf3ee2fbd167', 
            'message':'Nin verification process successfully started'
        }
    }

def nin_verification_final_step():
    return {
        'data': {
            'verification_id':'595e45af-08e3-4821-acc2-bf3ee2fbd167', 
            'msg':'Nin verification successfully'
        }
    }

def nin_verification_token_resend():
    return {
        'data': {
            'verification_id':'595e45af-08e3-4821-acc2-bf3ee2fbd167', 
            'msg':'Nin verification token successfully resend'
        }
    }

def platform_overview_data():
    return {
        "data": {
            "platform_overview": {
                "total_learners": {
                    "count": 73394,
                    "growth_percentage": 5.3,
                    "is_trending_up": True
                },
                "active_users": {
                    "count": 789,
                    "percentage": 78.5,
                    "currently_online": 156
                },
                "new_registrations": {
                    "count": 789,
                    "this_period": "month",
                    "pending_approval": 42
                },
                "completion_rate": {
                    "percentage": 12.3,
                    "certificates_issued": 156,
                    "is_system_healthy": False
                },
                "support_metrics": {
                    "pending_tickets": 17,
                    "technical_issues": 7,
                    "average_response_time": "2.3 hours"
                },
                "dropout_rate": {
                    "percentage": 15.2,
                    "is_concerning": True
                }
            }
        }
    }

def scholarship_distribution_data():
    return {
        "data": {
            "scholarship_distribution": {
                "total_states": 37,
                "total_students": 73394,
                "distribution_by_state": [
                    {
                        "state": "LAGOS",
                        "state_name": "Lagos",
                        "student_count": 12500,
                        "percentage": 17.0,
                        "avg_performance": 68.5,
                        "certification_count": 240,
                        "dropout_rate": 8.2
                    },
                    {
                        "state": "KWARA",
                        "state_name": "Kwara",
                        "student_count": 950,
                        "percentage": 1.3,
                        "avg_performance": 82.5,
                        "certification_count": 240,
                        "dropout_rate": 4.2
                    },
                    {
                        "state": "OGUN",
                        "state_name": "Ogun",
                        "student_count": 8200,
                        "percentage": 11.2,
                        "avg_performance": 72.1,
                        "certification_count": 180,
                        "dropout_rate": 6.5
                    }
                ],
                "featured_state": {
                    "state": "KWARA",
                    "state_name": "Kwara",
                    "student_count": 950,
                    "percentage": 1.3,
                    "avg_performance": 82.5,
                    "certification_count": 240,
                    "dropout_rate": 4.2
                },
                "top_performing_states": [
                    {
                        "state": "KWARA",
                        "state_name": "Kwara",
                        "avg_performance": 82.5
                    }
                ]
            }
        }
    }

def user_management_data():
    return {
        "data": {
            "total_users": 75420,
            "by_role": {
                "learners": 73394,
                "mentors": 1250,
                "facilitators": 680,
                "admins": 96
            },
            "by_status": {
                "active": 68500,
                "inactive": 4200,
                "disabled": 2720
            },
            "recent_activities": {
                "new_registrations_today": 45,
                "active_today": 2340,
                "pending_approvals": 156
            }
        }
    }

def learner_analytics_data():
    return {
        "data": {
            "summary": {
                "total_learners": 73394,
                "active_learners": 68500,
                "completion_rate": 12.3,
                "avg_progress": 45.8
            },
            "progress_distribution": {
                "beginner": 32500,
                "intermediate": 28900,
                "advanced": 8994,
                "completed": 3000
            },
            "demographics": {
                "gender": [
                    {"gender": "MALE", "count": 42500},
                    {"gender": "FEMALE", "count": 30894}
                ],
                "states": [
                    {"state": "LAGOS", "count": 12500},
                    {"state": "OGUN", "count": 8200},
                    {"state": "KANO", "count": 6800}
                ],
                "account_types": [
                    {"account_type": "STUDENT", "count": 58500},
                    {"account_type": "PROFESSIONAL", "count": 14894}
                ],
                "work_types": [
                    {"work_type": "ALL", "count": 35000},
                    {"work_type": "REMOTE", "count": 25000},
                    {"work_type": "ONSITE", "count": 13394}
                ]
            },
            "learning_tracks": [
                {
                    "learning_track": "Web Development",
                    "count": 28500,
                    "avg_progress": 52.3
                },
                {
                    "learning_track": "Data Science",
                    "count": 18200,
                    "avg_progress": 48.7
                },
                {
                    "learning_track": "Digital Marketing",
                    "count": 15600,
                    "avg_progress": 41.2
                }
            ],
            "trends": {
                "monthly_registrations": [
                    {"month": "2024-08", "count": 4200},
                    {"month": "2024-09", "count": 4800},
                    {"month": "2024-10", "count": 5200},
                    {"month": "2024-11", "count": 6100},
                    {"month": "2024-12", "count": 5800},
                    {"month": "2025-01", "count": 6500}
                ]
            }
        }
    }

def system_health_data():
    return {
        "data": {
            "database_status": "healthy",
            "active_sessions": 2340,
            "error_rate": 0.5,
            "response_time_avg": 120,
            "uptime": "99.9%",
            "last_updated": "2025-07-22T10:30:00Z"
        }
    }

def bulk_action_data():
    return {
        "data": {
            "message": "Successfully activated 15 users",
            "affected_count": 15
        }
    }

def list_learner_data():
    return {
        "data": {
            "links": {
                "next": None,
                "previous": None
            },
            "total": 1,
            "page_size": 10,
            "current": 1,
            "entity": [
                {
                    "user": {
                        "id": 4,
                        "email": "johnmail@gmail.com",
                        "first_name": "Odun",
                        "last_name": "Adebisi",
                        "phone_number": "+2348108012345",
                        "last_active": "2025-07-19T06:12:15.800334Z",
                        "role": "Learner",
                        "status": "Active"
                    },
                    "account_type": "Student",
                    "learning_track": "Web Development",
                    "skill_cluster": "Frontend",
                    "work_type": "Onsite",
                    "industrial_prefrence": "Tech",
                    "portfolio_link": "https://john.doe.com/portfolio",
                    "state": "LAGOS",
                    "gender": "Male",
                    "resume": "https://api.object-storage.prunedge.com/coursera-dev-storage/resume/receipt.pdf",
                    "progress": 0
                }
            ]
        }
    }

def learner_detail_data():
    return {
        "data": {
            "user": {
                "id": 4,
                "email": "johnmail@gmail.com",
                "first_name": "Odun",
                "last_name": "Adebisi",
                "phone_number": "+2348108012345",
                "last_active": "2025-07-19T06:12:15.800334Z",
                "role": "Learner",
                "status": "Active"
            },
            "account_type": "Student",
            "learning_track": "Web Development",
            "skill_cluster": "Frontend",
            "work_type": "Onsite",
            "industrial_prefrence": "Tech",
            "portfolio_link": "https://john.doe.com/portfolio",
            "state": "LAGOS",
            "gender": "Male",
            "resume": "https://api.object-storage.prunedge.com/coursera-dev-storage/resume/receipt.pdf",
            "progress": 65,
            "analytics": {
                "days_since_registration": 45,
                "last_activity_days_ago": 2,
                "is_active_learner": True
            }
        }
    }