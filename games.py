import random
from collections import Counter

COLORS = ['🟥', '🟨', '🟩', '🟦']

class Uno:
    def __init__(self):
        self.deck = [(c, '0') for c in COLORS]
        self.deck += [(c, n) for c in COLORS for n in list('123456789') + ['🚫', '🔄', '+2'] for _ in range(2)]
        self.deck += [('🌈', n) for n in ['W', '+4'] for _ in range(4)]
        random.shuffle(self.deck)
        self.hands = [[self.deck.pop() for _ in range(7)] for _ in range(4)]
        idx = next(i for i,c in enumerate(self.deck) if c[1].isdigit())
        self.discard = [self.deck.pop(idx)]
        self.color = self.discard[-1][0]
        self.turn, self.direction, self.winner = 0, 1, None
        self.log = []

    def legal(self, p, i):
        c, n = self.hands[p][i]
        if n == '+4':
            return not any(x[0] == self.color for x in self.hands[p])
        return c == '🌈' or c == self.color or n == self.discard[-1][1]

    def draw(self, p, count=1):
        for _ in range(count):
            if not self.deck:
                top = self.discard.pop()
                self.deck, self.discard = self.discard, [top]
                random.shuffle(self.deck)
            if self.deck:
                self.hands[p].append(self.deck.pop())

    def play(self, i, color=None):
        p = self.turn
        if self.winner is not None or not 0 <= i < len(self.hands[p]) or not self.legal(p, i):
            raise ValueError('Bu kartani tashlab bo‘lmaydi.')
        c, n = self.hands[p][i]
        if c == '🌈' and color not in COLORS:
            raise ValueError('Rangni tanlang.')
        self.hands[p].pop(i)
        self.discard.append((c,n))
        self.color = color if c == '🌈' else c
        self.log.append(f'{"Siz" if p == 0 else "Bot " + str(p)}: {c}{n}')
        if len(self.hands[p]) == 1:
            self.log.append('UNO! 🎉')
        if n == '🔄':
            self.direction *= -1
        step = 1
        if n in ['+2', '+4']:
            self.draw((p + self.direction) % 4, int(n[1:]))
            step = 2
        elif n == '🚫':
            step = 2
        self.turn = (p + step * self.direction) % 4
        if not self.hands[p]:
            self.winner = p

    def bots(self):
        for _ in range(100):
            if self.turn == 0 or self.winner is not None:
                break
            p = self.turn
            legal = [i for i in range(len(self.hands[p])) if self.legal(p,i)]
            if not legal:
                self.draw(p)
                legal = [len(self.hands[p])-1] if self.legal(p,len(self.hands[p])-1) else []
            if legal:
                i = max(legal, key=lambda i: self.hands[p][i][1] in ['+2','🚫','🔄'])
                counts = Counter(c for c,n in self.hands[p] if c in COLORS)
                self.play(i, max(COLORS,key=lambda c: counts[c]))
            else:
                self.log.append(f'Bot {p}: karta oldi')
                self.turn = (p+self.direction)%4

class Mafia:
    def __init__(self):
        self.roles = ['Mafiya','Mafiya','Doktor','Detektiv','Fuqaro','Fuqaro','Fuqaro']
        random.shuffle(self.roles)
        self.alive = list(range(7))
        self.phase, self.day, self.winner = 'night', 1, None
        self.known = {}
        self.log = []

    def name(self,p):
        return 'Siz' if p == 0 else f'Bot {p}'

    def check(self):
        m = sum(self.roles[p]=='Mafiya' for p in self.alive)
        if m == 0: self.winner = 'Shahar'
        elif m >= len(self.alive)-m: self.winner = 'Mafiya'

    def targets(self):
        if self.phase == 'day': return [p for p in self.alive if p != 0]
        if self.roles[0] == 'Mafiya': return [p for p in self.alive if self.roles[p]!='Mafiya']
        return self.alive[:]

    def night(self,target=None):
        if self.phase != 'night' or self.winner: raise ValueError('Tun tugagan.')
        role = self.roles[0]
        mafia = [p for p in self.alive if self.roles[p]=='Mafiya']
        victims = [p for p in self.alive if p not in mafia]
        victim = target if role=='Mafiya' and 0 in self.alive else random.choice(victims)
        doctors = [p for p in self.alive if self.roles[p]=='Doktor']
        saved = (target if role=='Doktor' and 0 in self.alive else random.choice(self.alive)) if doctors else None
        if role=='Detektiv' and 0 in self.alive and target is not None:
            self.known[target] = self.roles[target]=='Mafiya'
            self.log.append(f'🔎 {self.name(target)}: {"Mafiya" if self.known[target] else "Mafiya emas"}')
        if victim != saved:
            self.alive.remove(victim)
            self.log.append(f'🌙 {self.name(victim)} halok bo‘ldi. Roli: {self.roles[victim]}')
        else: self.log.append('💉 Doktor bir kishini qutqardi!')
        self.check()
        self.phase='day'

    def vote(self,target=None):
        if self.phase != 'day' or self.winner: raise ValueError('Ovoz berish vaqti emas.')
        votes = []
        if 0 in self.alive:
            if target not in self.alive or target == 0: raise ValueError('Nishonni tanlang.')
            votes.append(target)
        for p in self.alive:
            if p == 0: continue
            choices = [q for q in self.alive if q!=p]
            if self.roles[p]=='Mafiya': choices=[q for q in choices if self.roles[q]!='Mafiya']
            votes.append(random.choice(choices))
        counts = Counter(votes)
        highest = max(counts.values())
        leaders = [p for p,n in counts.items() if n == highest]
        self.log.append('🗳 Ovozlar: '+', '.join(f'{self.name(p)} — {n}' for p,n in counts.items()))
        if len(leaders)==1:
            p=leaders[0]
            self.alive.remove(p)
            self.log.append(f'🚪 {self.name(p)} chiqarildi. Roli: {self.roles[p]}')
        else: self.log.append('Teng ovoz: hech kim chiqarilmadi.')
        self.check()
        self.phase='night'
        self.day+=1
