import unittest
import numpy as np
from PyQt6.QtCore import QSize
from mainDir.inputs.generator.generator_Color import ColorGenerator
from mainDir.inputs.generator.generator_Noise_Grain import GrainGenerator
from mainDir.inputs.generator.generator_Noise_Random import RandomNoiseGenerator
from mainDir.inputs.generator.generator_Noise_SaltAndPepper import SaltAndPepperGenerator
from mainDir.inputs.generator.generator_SMPTE import SMPTEBarsGenerator
from mainDir.inputs.player.player_StillImage import StillImagePlayer
from mainDir.inputs.player.player_StingerMixBus import StingerForMixBusPlayer


class TestSerialization(unittest.TestCase):

    def test_serialization_deserialization(self):
        # Lista di classi da testare, puoi aggiungere tutte le classi derivate da BaseClassExtended
        classes_to_test = [ColorGenerator, GrainGenerator, RandomNoiseGenerator, SaltAndPepperGenerator,
                           SMPTEBarsGenerator, StillImagePlayer]

        for cls in classes_to_test:
            with self.subTest(cls=cls):
                # Creazione dell'istanza originale della classe
                original_instance = cls(QSize(1920, 1080))

                # Serializzazione dell'istanza originale
                serialized_data = original_instance.serialize()

                # Creazione di una nuova istanza della stessa classe
                new_instance = cls(QSize(1920, 1080))

                # Deserializzazione dei dati nella nuova istanza
                new_instance.deserialize(serialized_data)

                # Verifica che i dati serializzati/deserializzati siano corretti
                self.assertEqual(original_instance._name, new_instance._name,
                                 "I nomi delle classi non corrispondono dopo la deserializzazione.")
                self.assertEqual(original_instance.resolution, new_instance.resolution,
                                 "Le risoluzioni non corrispondono dopo la deserializzazione.")
                self.assertEqual(original_instance.isFrameInverted, new_instance.isFrameInverted,
                                 "Lo stato di isFrameInverted non corrisponde dopo la deserializzazione.")
                self.assertEqual(original_instance.isFrameAutoScreen, new_instance.isFrameAutoScreen,
                                 "Lo stato di isFrameAutoScreen non corrisponde dopo la deserializzazione.")
                self.assertEqual(original_instance.isFrameCLAHE, new_instance.isFrameCLAHE,
                                 "Lo stato di isFrameCLAHE non corrisponde dopo la deserializzazione.")
                self.assertEqual(original_instance.isFrameHistogramEqualization,
                                 new_instance.isFrameHistogramEqualization,
                                 "Lo stato di isFrameHistogramEqualization non corrisponde dopo la deserializzazione.")
                self.assertEqual(original_instance.isFrameCLAHEYUV, new_instance.isFrameCLAHEYUV,
                                 "Lo stato di isFrameCLAHEYUV non corrisponde dopo la deserializzazione.")
                self.assertEqual(original_instance.isFrameHistogramEqualizationYUV,
                                 new_instance.isFrameHistogramEqualizationYUV,
                                 "Lo stato di isFrameHistogramEqualizationYUV non corrisponde dopo la deserializzazione.")
                self.assertEqual(original_instance.gamma, new_instance.gamma,
                                 "Il valore di gamma non corrisponde dopo la deserializzazione.")

                # Verifica che le proprietà specifiche della classe ColorGenerator corrispondano
                if isinstance(original_instance, ColorGenerator):
                    self.assertTrue(np.array_equal(original_instance.color, new_instance.color),
                                    "I colori non corrispondono dopo la deserializzazione.")
                    self.assertTrue(np.array_equal(original_instance._frame, new_instance._frame),
                                    "I frame non corrispondono dopo la deserializzazione.")

        # Test separato per StingerForMixBusPlayer che richiede un parametro aggiuntivo
        with self.subTest(cls=StingerForMixBusPlayer):
            # Creazione dell'istanza originale della classe
            original_instance = StingerForMixBusPlayer(
                r"C:\pythonCode\openPyVisionBook\openPyVisionCOMM\mainDir\imgs\testSequence", 1, QSize(1920, 1080))

            # Serializzazione dell'istanza originale
            serialized_data = original_instance.serialize()

            # Creazione di una nuova istanza della stessa classe
            new_instance = StingerForMixBusPlayer(
                r"C:\pythonCode\openPyVisionBook\openPyVisionCOMM\mainDir\imgs\testSequence", 1, QSize(1920, 1080))

            # Deserializzazione dei dati nella nuova istanza
            new_instance.deserialize(serialized_data)

            # Verifica che i dati serializzati/deserializzati siano corretti
            self.assertEqual(original_instance._name, new_instance._name,
                             "I nomi delle classi non corrispondono dopo la deserializzazione.")
            self.assertEqual(original_instance.resolution, new_instance.resolution,
                             "Le risoluzioni non corrispondono dopo la deserializzazione.")
            self.assertEqual(original_instance.isFrameInverted, new_instance.isFrameInverted,
                             "Lo stato di isFrameInverted non corrisponde dopo la deserializzazione.")
            self.assertEqual(original_instance.isFrameAutoScreen, new_instance.isFrameAutoScreen,
                             "Lo stato di isFrameAutoScreen non corrisponde dopo la deserializzazione.")
            self.assertEqual(original_instance.isFrameCLAHE, new_instance.isFrameCLAHE,
                             "Lo stato di isFrameCLAHE non corrisponde dopo la deserializzazione.")
            self.assertEqual(original_instance.isFrameHistogramEqualization,
                             new_instance.isFrameHistogramEqualization,
                             "Lo stato di isFrameHistogramEqualization non corrisponde dopo la deserializzazione.")
            self.assertEqual(original_instance.isFrameCLAHEYUV, new_instance.isFrameCLAHEYUV,
                             "Lo stato di isFrameCLAHEYUV non corrisponde dopo la deserializzazione.")
            self.assertEqual(original_instance.isFrameHistogramEqualizationYUV,
                             new_instance.isFrameHistogramEqualizationYUV,
                             "Lo stato di isFrameHistogramEqualizationYUV non corrisponde dopo la deserializzazione.")
            self.assertEqual(original_instance.gamma, new_instance.gamma,
                             "Il valore di gamma non corrisponde dopo la deserializzazione.")


if __name__ == '__main__':
    unittest.main()
