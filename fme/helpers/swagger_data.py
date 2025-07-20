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
