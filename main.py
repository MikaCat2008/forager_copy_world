import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

if __name__ == "__main__":
    from application import Application

    game = Application()
    game.run()
