import re
from typing import Optional

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


class ConnectionsResult:
    puzzle_num: int
    num_guesses_incorrect: int

    def __init__(self, puzzle_num: int, num_guesses_incorrect: int):
        self.puzzle_num = puzzle_num
        self.num_guesses_incorrect = num_guesses_incorrect

    def __str__(self):
        return str({
            'puzzle_num': self.puzzle_num,
            'num_guesses_incorrect': self.num_guesses_incorrect
        })


def parse_connections_results(text: str) -> Optional[ConnectionsResult]:
    match = connections_re.fullmatch(text)
    if not match:
        return None

    puzzle_num, *guesses, comment = match.groups()

    guesses = list(filter(lambda guess: guess is not None, guesses))
    num_guesses_correct = sum(
        1 for guess in guesses
        if guess is not None
        and all(guess[i] == guess[0] for i in range(1, 4))
    )
    num_guesses_incorrect = len(guesses) - num_guesses_correct

    return ConnectionsResult(
        puzzle_num=int(puzzle_num),
        num_guesses_incorrect=num_guesses_incorrect
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
