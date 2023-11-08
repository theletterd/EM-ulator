from collections import defaultdict
import random
import string

from flask import Blueprint
from flask import render_template
from flask import redirect

from em_ulator.models import Game
from em_ulator.models import Project
from em_ulator.models import Ticket
from em_ulator import config

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
    return render_template("game.html", tickets_by_group=tickets_by_group, game_id=game_id)


@home_app.route("/game/create", methods=["POST"])
def create_game():
    game = Game.create_new_game()
    from em_ulator import db

    random_project_name = ''.join(random.sample(string.ascii_uppercase, random.randrange(3, 8)))

    project = Project(
        name=random_project_name,
        ticket_offset=random.randrange(1000),
        game_id=game.id
    )
    db.session.add(project)
    db.session.commit()

    for i in range(20):
        Ticket.new_ticket(
            project,
            random.choice(config.ticket_names),
            "stuffff"
        )

    # then create a project
    # then create like 20 tickets in the project
    # which are all in "TODO"
    # Then redirect to game view which shows the tickets.

    # we are also going to need a ticket title generator, and a ticket description generator
    redirect_url = f'/game/{game.id}'
    return redirect(redirect_url)
