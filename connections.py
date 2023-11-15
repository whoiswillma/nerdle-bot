import re
from enum import Enum, auto
from typing import Optional, List

connections_re = re.compile(
    r"""
\s*Connections\s*
Puzzle\s\#([0-9]+)\s*
([🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪])\s*
([🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪])\s*
([🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪])\s*
([🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪])\s*
([🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪])?\s*
([🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪])?\s*
([🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪][🟨🟩🟦🟪])?\s*
(.*)
""",
    re.VERBOSE | re.DOTALL
)


class SpecialOrder(Enum):
    NATURAL_ORDER = auto()
    REVERSE_ORDER = auto()


class ConnectionsResult:
    puzzle_num: int
    guesses: List[str]

    def __init__(self, puzzle_num: int, guesses: List[str]):
        self.puzzle_num = puzzle_num
        self.guesses = guesses

        for guess in guesses:
            assert len(guess) == 4
            assert all(c in '🟨🟩🟦🟪' for c in guess)

    def __str__(self):
        return str({
            'puzzle_num': self.puzzle_num,
            'guesses': self.guesses
        })

    @property
    def num_guesses_correct(self) -> int:
        return sum(
            all(guess[i] == guess[0] for i in range(1, 4))
            for guess in self.guesses
        )

    @property
    def num_guesses_incorrect(self) -> int:
        return len(self.guesses) - self.num_guesses_correct

    @property
    def special_order(self) -> Optional[SpecialOrder]:
        if self.guesses == ['🟨🟨🟨🟨', '🟩🟩🟩🟩', '🟦🟦🟦🟦', '🟪🟪🟪🟪']:
            return SpecialOrder.NATURAL_ORDER
        elif self.guesses == ['🟪🟪🟪🟪', '🟦🟦🟦🟦', '🟩🟩🟩🟩', '🟨🟨🟨🟨']:
            return SpecialOrder.REVERSE_ORDER
        else:
            return None


def parse_connections_results(text: str) -> Optional[ConnectionsResult]:
    match = connections_re.fullmatch(text)
    if not match:
        return None

    puzzle_num, *guesses, comment = match.groups()

    guesses = list(filter(lambda guess: guess is not None, guesses))

    return ConnectionsResult(
        puzzle_num=int(puzzle_num),
        guesses=guesses
    )


def test_1():
    print(parse_connections_results("""
Connections 
Puzzle #153
🟦🟪🟦🟦
🟦🟦🟪🟦
🟦🟦🟦🟦
🟪🟨🟪🟪
🟪🟪🟪🟨

Yeahhhh, I didn’t get this one
"""))


def test_2():
    print(parse_connections_results("""
Connections 
Puzzle #153
🟦🟦🟦🟦
🟪🟪🟩🟩
🟨🟪🟩🟨
🟪🟪🟪🟪
🟨🟨🟨🟨
🟩🟩🟩🟩
"""))


def test_3():
    print(parse_connections_results("""
Connections 
Puzzle #153
🟦🟦🟦🟦
🟩🟩🟩🟩
🟪🟪🟪🟪
🟨🟨🟨🟨
"""))


if __name__ == '__main__':
    test_1()
    test_2()
    test_3()
