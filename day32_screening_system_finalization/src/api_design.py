API_DESIGN = {

    "POST /screening/start": {
        "purpose": "Start a candidate screening session"
    },

    "POST /screening/answer": {
        "purpose": "Submit candidate answer for processing"
    },

    "POST /screening/complete": {
        "purpose": "Complete the screening session"
    },

    "GET /screening/{screening_id}": {
        "purpose": "Retrieve screening result"
    },

    "GET /screening/{screening_id}/report": {
        "purpose": "Retrieve recruiter-ready screening report"
    }
}