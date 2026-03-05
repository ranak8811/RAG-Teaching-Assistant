from fastapi import APIRouter, HTTPException, Depends, Body
from auth.route import authenticate
from chat.chat_query import answer_query, generate_quiz
import datetime
from config.db import (
    chat_history_collection,
    quizzes_collection,
    quiz_history
)
from bson.objectid import ObjectId
from chat.model import QuizRequest, QuizAnswerRequest

router=APIRouter()

@router.post('/chat')
async def chat(user=Depends(authenticate), query: str = Body(..., embed=True)):
    if user['role'] != 'Student':
        raise HTTPException(
            status_code=403,
            detail='Only student ask questions',
        )
    
    response = await answer_query(
        query, user['role'], user['grade']
    )

    chat_history_collection.insert_one(
        {
            'user_id': user['user_id'],
            'timestamp': datetime.datetime.utcnow(),
            'query': query,
            'response': response['answer'],
            'sources': response['sources']
        }
    )

    return response

@router.post('/quiz')
async def quiz(request: QuizRequest, user=Depends(authenticate)):
    if user['role'] != 'Student':
        raise HTTPException(
            status_code=403,
            detail='Only student can generate quizzes',
        )
    
    response = await generate_quiz(
        request.topic,
        user['role'],
        user['grade'],
        request.num_questions
    )

    quiz_doc = {
        'user_id': user['user_id'],
        'timestamp': datetime.datetime.utcnow(),
        'topic': request.topic,
        'quiz_data': response['quiz'],
        'sources': response['sources']
    }

    result = quizzes_collection.insert_one(quiz_doc)

    return {
        'quiz': response['quiz'],
        'sources': response['sources'],
        'quiz_id': str(result.inserted_id)
    }


@router.post('/quiz/check')
async def check_quiz_answer(request: QuizAnswerRequest, user=Depends(authenticate)):
    quiz_doc = quizzes_collection.find_one(
        {"_id": ObjectId(request.quiz_id)}
    )

    if not quiz_doc:
        raise HTTPException(
            status_code=404,
            detail='Quiz not found'
            )
    
    if quiz_doc['user_id'] != user['user_id']:
        raise HTTPException(
            status_code=403,
            detail='You are not authorized to answer this quiz'
        )
    
    correct_answers = []
    for line in quiz_doc['quiz_data'].split('\n'):
        if line.startswith('Correct Answer:'):
            correct_answers.append(line.split(':')[1].strip()[0])

    if len(request.answers) != len(correct_answers):
        raise HTTPException(
            status_code=400,
            detail='Invalid number of answers'
        )
    
    score = 0
    results = []

    for i, ans in enumerate(request.answers):
        is_correct = ans.strip().upper() == correct_answers[i]
        if is_correct:
            score += 1

        results.append(
            {
                'question_number': i + 1,
                'user_answer': ans,
                'correct_answer': correct_answers[i],
                'is_correct': is_correct
            }
        )

    quiz_history.insert_one({
        "user_id": user["user_id"],
        "quiz_id": request.quiz_id,
        "timestamp": datetime.datetime.utcnow(),
        "topic": quiz_doc["topic"],
        "score": score,
        "total": len(correct_answers),
        "results": results,
        "quiz_content": quiz_doc["quiz_data"],
    })

    return {
        'message': f"Quiz submitted successfully with a score of {score}/{len(correct_answers)}",
        'score': score,
        'total': len(correct_answers),
        'results': results
    }        


@router.get('/quiz/history')
async def get_quiz_history(user = Depends(authenticate)):
    if user['role'] != 'Student':
        raise HTTPException(
            status_code=403,
            detail='Only student can access quiz history',
        )
    
    cursor = quiz_history.find({"user_id": user['user_id']}).sort('timestamp', -1)

    history = []
    
    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        doc["quiz_id"] = str(doc["quiz_id"])
        doc.pop("user_id", None)
        history.append(doc)

    return {
        'message': f"Found {len(history)} quizzes in history",
        'history': history
    }