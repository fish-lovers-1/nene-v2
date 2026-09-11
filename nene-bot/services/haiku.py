import cmudict


STAGES = (5, 12, 17)
pronounciations = cmudict.dict()


def count_syllables(word: str) -> set[int] | None:
    variants = pronounciations.get("".join(filter(str.isalpha, word.lower())))
    if variants is None:
        return None
    count = set(sum(phone[-1].isdigit() for phone in variant) for variant in variants)
    return count


def reconstruct_haiku(words: list[str], potential_combs: list[list[tuple[int, int, int]]]) -> tuple[str, str, str] | None:
    if not potential_combs[-1]:
        return None

    for count, leaf_idx, stage in potential_combs[-1]:
        if stage == 3:
            haiku = [[], [], []]
            idx = len(potential_combs) - 1
            while idx > 0:
                prev_stage = potential_combs[idx - 1][leaf_idx][2]
                haiku[prev_stage].append(words[idx - 1])
                count, leaf_idx, stage = potential_combs[idx - 1][leaf_idx]
                idx -= 1
            return tuple(" ".join(reversed(haiku[i])) for i in range(3))


def get_haiku(message: str) -> tuple[str, str, str] | None:
    """
    1. Levels of tree
    2. Nodes at each level
    3. The total syllables, back pointer and stage idx
    """
    words = message.split()
    potential_combs: list[list[tuple[int, int, int]]] = [[(0, 0, 0)]]
    for idx, word in enumerate(words):
        word_count = count_syllables(word)
        if word_count is None:
            return None
        potential_combs.append([])
        for leaf_idx, (count, _, stage) in enumerate(potential_combs[-2]):
            potential_combs[-1] += list(filter(lambda x: x[2] is not None, [(count + s, leaf_idx, None if stage == 3 else stage if count + s < STAGES[stage] else stage + 1 if count + s == STAGES[stage] else None) for s in word_count]))

    return reconstruct_haiku(words, potential_combs)


if __name__ == "__main__":
    checks = ["evening", "temperature", "beloved", "favourite", "crooked", "learned"]
    for check in checks:
        print(count_syllables(check))
    haiku = get_haiku("An old silent pond A frog jumps into the pond Splash! Silence again.")
    print(haiku)
