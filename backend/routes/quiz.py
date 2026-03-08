from flask import Blueprint, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from backend.config import Config
from backend.utils.auth_utils import token_required
from backend.services.llm_service import generate_quiz_from_text
from backend.services.pdf_service import extract_text_from_pdf
import datetime
import traceback

quiz_bp = Blueprint("quiz", __name__)

def get_db():
    client = MongoClient(Config.MONGO_URI)
    return client.get_database()

@quiz_bp.route("/extract-pdf", methods=["POST"])
@token_required
def extract_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files allowed"}), 400
    try:
        text = extract_text_from_pdf(file.read())
        if len(text) < 50:
            return jsonify({"error": "PDF text too short or unreadable"}), 400
        return jsonify({"text": text[:5000]}), 200
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@quiz_bp.route("/generate", methods=["POST"])
@token_required
def generate():
    data = request.get_json()
    text = data.get("text", "").strip()
    num_questions = int(data.get("num_questions", 5))
    difficulty = data.get("difficulty", "medium")
    quiz_type = data.get("quiz_type", "mcq")
    topic = data.get("topic", "General")

    if not text or len(text) < 50:
        return jsonify({"error": "Text too short"}), 400
    if num_questions < 1 or num_questions > 15:
        return jsonify({"error": "Questions must be 1-15"}), 400
    if difficulty not in ["easy", "medium", "hard"]:
        return jsonify({"error": "Invalid difficulty"}), 400

    try:
        print(f"[GENERATE] text_len={len(text)}, num_q={num_questions}, diff={difficulty}, type={quiz_type}")
        print(f"[GENERATE] GROQ_API_KEY present: {'YES' if Config.GROQ_API_KEY else 'NO'}")
        
        quiz_data = generate_quiz_from_text(text, num_questions, difficulty, quiz_type)
        
        db = get_db()
        quiz_doc = {
            "user_id": request.user_id,
            "topic": topic,
            "difficulty": difficulty,
            "quiz_type": quiz_type,
            "questions": quiz_data["quiz"],
            "created_at": datetime.datetime.utcnow(),
            "completed": False
        }
        result = db.quizzes.insert_one(quiz_doc)
        print(f"[GENERATE] Quiz saved with id: {result.inserted_id}")
        return jsonify({"quiz_id": str(result.inserted_id), "questions": quiz_data["quiz"]}), 200

    except Exception as e:
        print(f"[GENERATE ERROR] {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@quiz_bp.route("/submit", methods=["POST"])
@token_required
def submit():
    data = request.get_json()
    quiz_id = data.get("quiz_id")
    answers = data.get("answers", {})

    db = get_db()
    quiz = db.quizzes.find_one({"_id": ObjectId(quiz_id), "user_id": request.user_id})
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    questions = quiz["questions"]
    correct = 0
    results = []

    for i, q in enumerate(questions):
        user_ans = answers.get(str(i), "").strip()
        correct_ans = q["correct"]
        is_correct = False

        if q["type"] == "mcq":
            is_correct = user_ans.upper() == correct_ans.upper()
        else:
            is_correct = user_ans.lower() == correct_ans.lower()

        if is_correct:
            correct += 1

        results.append({
            "question": q["question"],
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
            "options": q.get("options", {})
        })

    score_pct = round((correct / len(questions)) * 100)

    suggestion = None
    if score_pct >= 80 and quiz["difficulty"] == "easy":
        suggestion = {"message": "Excellent! You're ready to try Medium difficulty!", "next_level": "medium"}
    elif score_pct >= 80 and quiz["difficulty"] == "medium":
        suggestion = {"message": "Outstanding! Challenge yourself with Hard difficulty!", "next_level": "hard"}
    elif score_pct < 40 and quiz["difficulty"] == "hard":
        suggestion = {"message": "Consider practicing Medium difficulty first.", "next_level": "medium"}
    elif score_pct < 40 and quiz["difficulty"] == "medium":
        suggestion = {"message": "Try Easy difficulty to build your foundation.", "next_level": "easy"}

    db.quizzes.update_one({"_id": ObjectId(quiz_id)}, {"$set": {
        "completed": True,
        "score": score_pct,
        "correct": correct,
        "total": len(questions),
        "results": results,
        "completed_at": datetime.datetime.utcnow()
    }})

    user_quizzes = list(db.quizzes.find({"user_id": request.user_id, "completed": True}))
    total = len(user_quizzes)
    avg = round(sum(q.get("score", 0) for q in user_quizzes) / total) if total else 0
    db.users.update_one({"_id": ObjectId(request.user_id)}, {"$set": {"total_quizzes": total, "avg_score": avg}})

    return jsonify({
        "score": score_pct,
        "correct": correct,
        "total": len(questions),
        "results": results,
        "suggestion": suggestion
    }), 200