# Half month index: 1 = early Jan, 2 = late Jan ... 24 = late Dec.
# Each crop: name, group, dict of kind -> list of (start, end) inclusive half month ranges.
# Kinds: I sow indoors / under cover, S sow outside, P plant out, H harvest.
# General UK timings (middle of England), aligned with RHS guidance and June's Year Planner.

def r(*pairs):
    return [tuple(p) for p in pairs]

GROUPS = [
    ("Salads and quick crops", [
        ("Salad leaves", {"I": r((5, 6)), "S": r((7, 16)), "H": r((9, 20))}),
        ("Rocket", {"S": r((7, 17)), "H": r((9, 21))}),
        ("Spinach", {"S": r((5, 10), (15, 18)), "H": r((9, 13), (18, 22))}),
        ("Radishes", {"S": r((5, 18)), "H": r((7, 20))}),
        ("Spring onions", {"S": r((5, 16)), "H": r((9, 20))}),
        ("Chard", {"S": r((7, 14)), "H": r((13, 22))}),
    ]),
    ("Roots and onions", [
        ("Carrots", {"S": r((7, 14)), "H": r((13, 22))}),
        ("Beetroot", {"I": r((5, 6)), "S": r((7, 14)), "H": r((12, 20))}),
        ("Parsnips", {"S": r((6, 10)), "H": r((1, 6), (19, 24))}),
        ("Potatoes", {"P": r((6, 8)), "H": r((12, 20))}),
        ("Onions (sets)", {"P": r((5, 8), (19, 21)), "H": r((13, 17))}),
        ("Garlic", {"P": r((3, 6), (19, 23)), "H": r((12, 16))}),
        ("Leeks", {"I": r((5, 7)), "P": r((11, 14)), "H": r((1, 8), (17, 24))}),
    ]),
    ("Cabbage family", [
        ("Kale", {"S": r((7, 12)), "P": r((11, 14)), "H": r((1, 8), (17, 24))}),
        ("Cabbage (summer, autumn)", {"I": r((5, 6)), "S": r((7, 10)), "P": r((9, 13)), "H": r((13, 22))}),
        ("Brussels sprouts", {"I": r((5, 6)), "S": r((7, 8)), "P": r((10, 12)), "H": r((1, 4), (19, 24))}),
        ("Purple sprouting broccoli", {"S": r((7, 10)), "P": r((11, 14)), "H": r((3, 10))}),
    ]),
    ("Peas and beans", [
        ("Peas", {"I": r((5, 6)), "S": r((7, 12)), "H": r((11, 17))}),
        ("Broad beans", {"S": r((3, 8), (20, 22)), "H": r((10, 15))}),
        ("French beans", {"I": r((8, 9)), "S": r((10, 13)), "P": r((10, 12)), "H": r((14, 19))}),
        ("Runner beans", {"I": r((8, 9)), "S": r((10, 12)), "P": r((10, 12)), "H": r((14, 19))}),
    ]),
    ("Tender crops (after your last frost)", [
        ("Tomatoes", {"I": r((4, 7)), "P": r((10, 11)), "H": r((14, 19))}),
        ("Chillies and peppers", {"I": r((3, 6)), "P": r((10, 11)), "H": r((15, 20))}),
        ("Courgettes", {"I": r((8, 9)), "S": r((10, 11)), "P": r((10, 12)), "H": r((13, 19))}),
        ("Squash and pumpkins", {"I": r((8, 9)), "S": r((10, 11)), "P": r((10, 12)), "H": r((17, 20))}),
        ("Cucumbers", {"I": r((7, 9)), "P": r((10, 12)), "H": r((13, 18))}),
        ("Sweetcorn", {"I": r((8, 9)), "S": r((10, 11)), "P": r((10, 12)), "H": r((15, 18))}),
    ]),
    ("Herbs", [
        ("Basil", {"I": r((6, 11)), "P": r((11, 12)), "H": r((12, 18))}),
        ("Parsley", {"I": r((5, 6)), "S": r((7, 14)), "H": r((11, 22))}),
        ("Coriander", {"S": r((7, 16)), "H": r((10, 20))}),
    ]),
    ("Fruit", [
        ("Strawberries", {"P": r((5, 8), (15, 18)), "H": r((11, 15))}),
        ("Rhubarb", {"P": r((1, 6), (21, 24)), "H": r((7, 13))}),
        ("Currants and gooseberries", {"P": r((1, 6), (21, 24)), "H": r((12, 15))}),
        ("Raspberries", {"P": r((1, 6), (21, 24)), "H": r((12, 19))}),
    ]),
]

ALL_YEAR = ("Microgreens and pea shoots", "All year on a sunny windowsill: sow and cut every couple of weeks")

COOK = [
    ("Jan", "Leek and potato soup"),
    ("Feb", "Kale and bacon colcannon"),
    ("Mar", "Purple sprouting broccoli on toast"),
    ("Apr", "Rhubarb crumble"),
    ("May", "Radish and spring onion salad"),
    ("Jun", "Broad bean and mint smash"),
    ("Jul", "Courgette fritters"),
    ("Aug", "Tomato and basil salad"),
    ("Sep", "Runner bean chutney"),
    ("Oct", "Roast squash soup"),
    ("Nov", "Honey roast parsnips"),
    ("Dec", "Sprouts with bacon and chestnuts"),
]

# "Any garden" edition: timing relative to your average LAST SPRING FROST date.
# Columns: weeks from last frost, -12 .. +20 in 2 week steps handled by the renderer.
# For each crop: kind -> list of (start_week, end_week) relative to last frost.
# Harvest is shown as a text note because it depends on the length of the season.
FROST = [
    ("Salad leaves", {"I": [(-6, -3)], "S": [(-4, 14)]}, "4 to 8 weeks after sowing; sow again every 2 to 3 weeks"),
    ("Rocket", {"S": [(-4, 16)]}, "3 to 5 weeks after sowing"),
    ("Spinach", {"S": [(-6, 2), (12, 18)]}, "5 to 8 weeks; bolts in hot weather"),
    ("Radishes", {"S": [(-6, 16)]}, "3 to 5 weeks"),
    ("Spring onions", {"S": [(-6, 12)]}, "8 to 10 weeks"),
    ("Chard", {"S": [(-2, 10)]}, "8 weeks on, until hard frost"),
    ("Carrots", {"S": [(-3, 10)]}, "10 to 16 weeks"),
    ("Beetroot", {"I": [(-6, -3)], "S": [(-2, 10)]}, "8 to 12 weeks"),
    ("Parsnips", {"S": [(-4, 2)]}, "Autumn and winter, sweeter after frost"),
    ("Potatoes", {"P": [(-4, 2)]}, "Earlies 10 to 12 weeks; maincrop 16 to 20"),
    ("Onions (sets)", {"P": [(-6, -2)]}, "Late summer, when the leaves flop"),
    ("Garlic", {"P": [(-8, -4)]}, "Midsummer; best planted in autumn"),
    ("Leeks", {"I": [(-8, -4)], "P": [(4, 10)]}, "Autumn into winter"),
    ("Kale", {"S": [(-2, 6)], "P": [(4, 10)]}, "Autumn to spring, picking leaves"),
    ("Cabbage", {"I": [(-8, -5)], "S": [(-4, 0)], "P": [(-2, 4)]}, "12 to 20 weeks"),
    ("Brussels sprouts", {"I": [(-8, -5)], "S": [(-4, -2)], "P": [(1, 5)]}, "Autumn and winter"),
    ("Peas", {"I": [(-8, -5)], "S": [(-4, 4)]}, "10 to 12 weeks"),
    ("Broad beans", {"S": [(-10, -4)]}, "Early summer"),
    ("French beans", {"I": [(-3, 0)], "S": [(1, 7)], "P": [(1, 3)]}, "8 to 10 weeks, pick often"),
    ("Runner beans", {"I": [(-3, 0)], "S": [(1, 5)], "P": [(1, 3)]}, "12 weeks, pick often"),
    ("Tomatoes", {"I": [(-10, -6)], "P": [(1, 3)]}, "About 10 weeks after planting out"),
    ("Chillies and peppers", {"I": [(-12, -8)], "P": [(1, 3)]}, "About 12 weeks after planting out"),
    ("Courgettes", {"I": [(-4, -1)], "S": [(1, 4)], "P": [(1, 4)]}, "6 to 8 weeks after planting out"),
    ("Squash and pumpkins", {"I": [(-4, -1)], "S": [(1, 3)], "P": [(1, 4)]}, "Early autumn, before the first frost"),
    ("Cucumbers", {"I": [(-5, -2)], "P": [(1, 4)]}, "6 to 8 weeks after planting out"),
    ("Sweetcorn", {"I": [(-4, -1)], "S": [(1, 3)], "P": [(1, 4)]}, "When the silks turn brown and the juice is creamy"),
    ("Basil", {"I": [(-6, 4)], "P": [(2, 4)]}, "Pick the tips all summer"),
    ("Parsley", {"I": [(-8, -4)], "S": [(-2, 10)]}, "10 weeks on"),
    ("Coriander", {"S": [(-2, 14)]}, "6 to 8 weeks; sow little and often"),
]
