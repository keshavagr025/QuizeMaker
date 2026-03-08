from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
from backend.config import Config
from backend.utils.auth_utils import token_required
from collections import defaultdict

dashboard_bp = Blueprint("dashboard", __name__)

def get_db():
    client = MongoClient(Config.MONGO_URI)
    return client.get_database()

@dashboard_bp.route("/history", methods=["GET"])
@token_required
def history():
    db = get_db()
    user_id = request.user_id
    quizzes = list(db.quizzes.find(
        {"user_id": user_id, "completed": True},
        {"results": 0}
    ).sort("completed_at", -1).limit(20))

    for q in quizzes:
        q["_id"] = str(q["_id"])
        if "created_at" in q:
            q["created_at"] = q["created_at"].isoformat()
        if "completed_at" in q:
            q["completed_at"] = q["completed_at"].isoformat()

    return jsonify(quizzes), 200

@dashboard_bp.route("/analytics", methods=["GET"])
@token_required
def analytics():
    db = get_db()
    quizzes = list(db.quizzes.find(
        {"user_id": request.user_id, "completed": True},
        {"score": 1, "difficulty": 1, "quiz_type": 1, "topic": 1, "completed_at": 1, "correct": 1, "total": 1}
    ).sort("completed_at", -1))

    if not quizzes:
        return jsonify({"empty": True}), 200

    score_trend = [
        {"date": q["completed_at"].strftime("%b %d"), "score": q.get("score", 0)}
        for q in reversed(quizzes[-10:])
    ]

    diff_stats = defaultdict(lambda: {"total": 0, "sum": 0})
    for q in quizzes:
        d = q.get("difficulty", "medium")
        diff_stats[d]["total"] += 1
        diff_stats[d]["sum"] += q.get("score", 0)

    diff_breakdown = {
        k: {"count": v["total"], "avg": round(v["sum"] / v["total"])}
        for k, v in diff_stats.items()
    }

    type_stats = defaultdict(int)
    for q in quizzes:
        type_stats[q.get("quiz_type", "mcq")] += 1

    scores = [q.get("score", 0) for q in quizzes]
    total_correct = sum(q.get("correct", 0) for q in quizzes)
    total_questions = sum(q.get("total", 0) for q in quizzes)

    return jsonify({
        "total_quizzes": len(quizzes),
        "avg_score": round(sum(scores) / len(scores)),
        "best_score": max(scores),
        "total_correct": total_correct,
        "total_questions": total_questions,
        "score_trend": score_trend,
        "difficulty_breakdown": diff_breakdown,
        "type_breakdown": dict(type_stats)
    }), 200

@dashboard_bp.route("/quiz/<quiz_id>", methods=["GET"])
@token_required
def get_quiz_result(quiz_id):
    db = get_db()
    quiz = db.quizzes.find_one({"_id": ObjectId(quiz_id), "user_id": request.user_id})
    if not quiz:
        return jsonify({"error": "Not found"}), 404
    quiz["_id"] = str(quiz["_id"])
    if "created_at" in quiz:
        quiz["created_at"] = quiz["created_at"].isoformat()
    if "completed_at" in quiz:
        quiz["completed_at"] = quiz["completed_at"].isoformat()
    return jsonify(quiz), 200