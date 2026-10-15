import random
import unittest
from games import Uno, Mafia, COLORS

class GamesTest(unittest.TestCase):
    def test_uno_deck_and_simulations(self):
        for seed in range(100):
            random.seed(seed)
            g=Uno()
            self.assertEqual(len(g.deck)+sum(map(len,g.hands))+len(g.discard),108)
            for _ in range(2000):
                if g.winner is not None: break
                if g.turn==0:
                    choices=[i for i in range(len(g.hands[0])) if g.legal(0,i)]
                    if choices: g.play(choices[0],COLORS[0])
                    else: g.draw(0); g.turn=g.direction%4
                g.bots()
                self.assertEqual(len(g.deck)+sum(map(len,g.hands))+len(g.discard),108)
            self.assertIsNotNone(g.winner)

    def test_wild_four_restriction(self):
        g=Uno(); g.color=COLORS[0]
        g.hands[0]=[(COLORS[0],'1'),('🌈','+4')]
        self.assertFalse(g.legal(0,1))

    def test_mafia_simulations(self):
        for seed in range(100):
            random.seed(seed); g=Mafia()
            for _ in range(100):
                if g.winner: break
                target=random.choice(g.targets()) if 0 in g.alive else None
                if g.phase=='night': g.night(target)
                else: g.vote(target)
            self.assertIsNotNone(g.winner)
            self.assertEqual(len(g.alive),len(set(g.alive)))

if __name__=='__main__': unittest.main()
