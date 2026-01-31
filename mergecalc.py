def min_lower_items_with_breakdown(needed):
    """
    Given `needed` items of level k+1,
    return:
    - minimum number of level-k items required
    - number of level-(k+1) items actually produced
    """
    best_cost = float("inf")
    best_produced = 0

    # Try possible numbers of 5->2 merges
    max_a = (needed + 1) // 2 + 3

    for a in range(max_a + 1):
        produced_a = 2 * a
        remaining = max(0, needed - produced_a)

        b = remaining  # 3->1 merges
        produced = produced_a + b
        cost = 5 * a + 3 * b

        if produced >= needed and cost < best_cost:
            best_cost = cost
            best_produced = produced

    return best_cost, best_produced


def calculate_with_intermediates(target_level, target_count):
    current_needed = target_count
    generated = {}

    for level in range(target_level, 1, -1):
        lower_needed, produced = min_lower_items_with_breakdown(current_needed)

        generated[level] = produced
        current_needed = lower_needed

    generated[1] = current_needed
    return current_needed, generated


if __name__ == "__main__":
    level = int(input("Enter target item level: "))
    count = int(input("Enter number of items needed at that level: "))

    level1_needed, generated = calculate_with_intermediates(level, count)

    print("\nResult:")
    print(f"Level-1 items needed: {level1_needed}\n")

    print("Items generated per level:")
    for lvl in sorted(generated.keys(), reverse=True):
        print(f"  Level {lvl}: {generated[lvl]} item(s)")
