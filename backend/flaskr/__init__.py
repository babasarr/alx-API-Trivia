from ast import Or
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [categorie.format() for categorie in categories]

        if len(formatted_categories) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "categories": formatted_categories,
                "total_categories": len(Category.query.all()),
            }
        )


    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [categorie.format() for categorie in categories]
        current_category = formatted_categories[0]

        if len(current_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": current_questions,
                "total_questions": len(Question.query.all()),
                "categories": formatted_categories,
                "current_category": current_category

            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        try:

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        search = body.get("searchTerm", None)


        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "search": search,
                        "questions": current_questions,
                        "total_questions": len(selection.all()),
                    }
                )
            else:
                if new_question is None or new_answer is None:
                    abort(400)

                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "created": question.id,
                        "questions": current_questions,
                        "total_questions": len(Question.query.all()),
                    }
                )

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    # @app.route("/questions", methods=["POST"])
    # def search_question():
    #     body = request.get_json()

    #     search = body.get("search", None)

    #     try:
            
    #         selection = Question.query.order_by(Question.id).filter(
    #             Question.title.ilike("%{}%".format(search))
    #         )
    #         current_questions = paginate_questions(request, selection)

    #         return jsonify(
    #             {
    #                 "success": True,
    #                 "search": search,
    #                 "questions": current_questions,
    #                 "total_questions": len(selection.all()),
    #             }
    #         )

    #     except:
    #         abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:categorie_id>/questions")
    def categories_questions(categorie_id):

        categorie = Category.query.filter(Category.id == categorie_id).one_or_none()
        if categorie is None:
            abort(404)

        try:
            
            questions = Question.query.filter(Question.category ==  str(categorie.id))
            current_questions = paginate_questions(request, questions)
            categorie_format = categorie.format()


            return jsonify(
                {
                    "success": True,
                    "category": categorie_format,
                    "questions": current_questions,
                    "total_questions": len(current_questions),
                }
            )

        except:
            abort(400)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    
    @app.route("/quizzes", methods=["POST"])
    def play_quizzes():
        body = request.get_json()

        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)

        if quiz_category is None:
            questions = Question.query.order_by(Question.id).filter(Question.id not in previous_questions ).all()
        else :
            questions = Question.query.filter(Question.category == str(quiz_category['id'])).filter(Question.id not in previous_questions).all()

        questions_format = [question.format() for question in questions]
        
        
        question = random.choice(questions_format) if len(questions_format) != 0 else None


        return jsonify(
            {
                "success": True,
                "previous_questions": previous_questions,
                "quiz_category": quiz_category,
                "question": question,
            }
        )


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


    return app
