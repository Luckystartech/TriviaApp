import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_cors import CORS
import random


from sqlalchemy import text



from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

#create paginate questions function with 10 per page
def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
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
    CORS(app, resources={'/': {'origins': '*'}})

    # CORS Headers

    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
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
        current_question = paginate_questions(request, selection)

        categories_query = Category.query.order_by(Category.type).all()

        categories = {category.id: category.type for category in categories_query}

        if len(current_question) == 0:
            abort(404)
        
        return jsonify(
            {
                "success": True,
                "total_questions": len(Question.query.all()),
                "questions": current_question,
                "categories": categories,
                "current_category": None
            }
        )

    @app.route('/questions/<int:question_id>')
    def retrieve_questions_with_id(question_id):
      question = Question.query.filter(Question.id == question_id).one_or_none()
      categories = Category.query.all()
      categories_details = {}

      current_category = Category.query.filter(Category.id == question.category).one_or_none()

      if question is None:
        abort(404)

      for each_categories in categories:
            categories_details[each_categories.id] = each_categories.type
            

      else:
        return jsonify({
          'success': True,
          'question': question.format(),
          'categories': categories_details,
          'current_category': current_category.type
        })



    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        categories_details = {}

        for each_categories in categories:
            categories_details[each_categories.id] = each_categories.type

        if len(categories_details) == 0:
            abort(404)
        
        return jsonify(
            {
                "success": True,
                "total_categories": len(Category.query.all()),
                "categories": categories_details
                
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
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)
            
            else:
                question.delete()
                selection = Question.query.order_by(Question.id).all()
                current_question = paginate_questions(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "deleted": question_id,
                        "books": current_question,
                        "total_books": len(Question.query.all())
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

        #compare this with the frontend

        new_question = body.get("question", None)
        new_answer_text = body.get("answer", None)
        new_category = body.get("category", None)
        new_difficulty = body.get("difficulty", None)
        

        try:
            question = Question(question=new_question, answer=new_answer_text, category=new_category, difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "questions": current_question,
                    "total_questions": len(Question.query.all())
                }
            )

        except:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search_question():
        body = request.get_json()
        search = body.get("searchTerm", None)
        
        # if 'searchTerm' not in body:
        #     abort(400)

        if search:
            selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))).all()
               
            current_question = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "questions": current_question,
                    "total_questions": len(selection),
                    "current_category": None
                }
            )
        else:
            abort(404)
        
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions")
    def retrieve_category_question(category_id):
        category = Category.query.filter(Category.id == category_id).first()
        if category is None:
            abort(404)
        else:
            try:
                selection = Question.query.filter(Question.category == str(category_id)).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'current_category': category.type,
                    'questions': current_questions,
                    'total_questions': len(selection)
                })
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
    @app.route("/quizzes", methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            prev_questions = body.get('previous_questions', None)
            category = body.get('quiz_category', None)

            question = Question.query
            if category['id'] != 0:
                av_questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((prev_questions))).all()
            else:
                av_questions = Question.query.filter(Question.id.notin_((prev_questions))).all()
            
            if len(av_questions) > 0:
                next_question = random.choice(av_questions).format()

            return jsonify({
                'question': next_question,
                'success': True
            })
        except:
            abort(422)
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
    
    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not found"}),
            405,
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

