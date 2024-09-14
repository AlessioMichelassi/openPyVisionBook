import sys
import cProfile
import pstats
import io

from mainDir.inputs.player.player_StillImage import StillImagePlayer
from videoApp import VideoApp  # Assicurati che questo sia l'import corretto


def main():
    # Inizializza l'input specifico
    path = r"/cap3/cap3_1/testClass/Grass_Valley_110_Switcher.jpg"
    noise_input = StillImagePlayer(path)
    app = VideoApp(sys.argv, noise_input)
    app.exec()


if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(30)
    print(s.getvalue())
