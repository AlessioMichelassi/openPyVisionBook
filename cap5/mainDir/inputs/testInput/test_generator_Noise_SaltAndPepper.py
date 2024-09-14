import sys
import cProfile
import pstats
import io

from mainDir.inputs.generator.generator_Noise_SaltAndPepper import SaltAndPepperGenerator
from videoApp import VideoApp  # Assicurati che questo sia l'import corretto


def main():
    # Inizializza l'input specifico
    noise_input = SaltAndPepperGenerator()
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
