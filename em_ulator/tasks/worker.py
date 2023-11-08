import time

import em_ulator
from em_ulator.models import Game

class GameRunner():

    def run(self):
        while True:
            games = Game.get_all()
            for game in games:
                print(f"Tick for game {game.id}")
                game.tick()

            # transition each game
            print("sleeping for 5")
            time.sleep(5)


if __name__ == '__main__':
    app = em_ulator.create_app()
    with app.app_context():
        g = GameRunner()
        g.run()
