from flask import Blueprint
from flask import render_template
import random

home_app = Blueprint('home', __name__)

@home_app.route("/")
def index():
    # list out active games
    fake_game_numbers = sorted(random.sample(range(100), 10))
    return render_template("index.html", games=fake_game_numbers)

@home_app.route("/game/<int:game_number>/")
def game(game_number):

    # 404 if no such game
    return render_template("game.html", number=random.randint(0, 100))


@home_app.route("/game/create")
def create_game():
    from em_ulator.models import Game
    Game.create_new_game()
    return "poops"
