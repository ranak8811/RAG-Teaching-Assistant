from pydantic import BaseModel
from typing import Optional, List

class QuizRequest(BaseModel):
    topic: str
    num_questions: Optional[int] = 3

class QuizAnswerRequest(BaseModel):
    quiz_id: str
    answers: List[str]