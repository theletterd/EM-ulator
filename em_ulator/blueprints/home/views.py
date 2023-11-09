from collections import defaultdict
import random

from flask import Blueprint
from flask import render_template
from flask import redirect

from em_ulator.models import Game
from em_ulator.models import Employee
from em_ulator.models import Project
from em_ulator.models import Ticket


home_app = Blueprint('home', __name__)


@home_app.route("/")
def index():
    # list out active games
    games = Game.get_all()
    return render_template("index.html", games=games)


@home_app.route("/game/<int:game_id>/")
def game(game_id):
    # ok so what we want to do now is to load up all tickets  associated
    # with this game, through projects.
    # so let's jank this bad boy up
    game = Game.get_game(game_id)
    if not game:
        return "no such game, dawg"

    tickets = game.get_all_tickets()
    grouped_tickets = defaultdict(list)
    for ticket in tickets:
        grouped_tickets[ticket.state.name].append(ticket)


    tickets_by_group = [
        ("To Do", grouped_tickets["Blocked"] + grouped_tickets["Open"]),
        ("In Progress", grouped_tickets["In Progress"]),
        ("In Review", grouped_tickets["In Review"]),
        ("Done", grouped_tickets["Closed"])
    ]
    return render_template("game.html", tickets_by_group=tickets_by_group, game=game)

@home_app.route("/game/<int:game_id>/force_tick", methods=["POST"])
def force_tick(game_id):
    game = Game.get_game(game_id)
    game.tick()
    redirect_url = f'/game/{game.id}'
    return redirect(redirect_url)


@home_app.route("/game/create", methods=["POST"])
def create_game():
    game = Game.create_new_game()

    # create Employees linked to Game
    for _ in range(random.randrange(4,10)):
        Employee.new_employee(game.id)


    for _ in range(1):
        project = Project.new_project(game.id)

        for _ in range(20):
            Ticket.new_ticket(project.id)


    redirect_url = f'/game/{game.id}'
    return redirect(redirect_url)
