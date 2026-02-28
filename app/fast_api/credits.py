from fastapi import APIRouter

router = APIRouter()

@router.get("/credits", tags=["credits"])
async def list_members():
    return {
        "the_thunderbolts": [
            {
                "name": "Matthew Lee",
                "major": "Computer Engineering",
                "grad_date": "May 2027",
            },
            {
                "name": "Theodore Ng",
                "major": "Computer Engineering",
                "grad_date": "May 2027",
            },
            {
                "name": "Steve Xing",
                "major": "Computer Science",
                "grad_date": "May 2027",
            },
            {
                "name": "Jimmy Lee",
                "major": "Computer Engineering",
                "grad_date": "Dec 2026",
            },
        ]
    }

