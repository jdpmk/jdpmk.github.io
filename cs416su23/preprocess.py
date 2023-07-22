lines = []
augmented = []

with open("sp500.csv", "r") as src:
    lines = src.readlines()

lines = lines[1:]  # skip the csv header
lines.sort()

for line in lines:
    d, v = line.strip().split(",")
    v = float(v)

    md1 = None
    md2 = None
    mv1 = None
    mv2 = None
    
    i = 0
    while augmented and i < len(augmented) - 1:
        d1, v1, _, _, _, _ = augmented[i]
        d2, v2, _, _, _, _ = augmented[i + 1]
        if d2 > d:
            break
        if v1 <= v <= v2 or v1 >= v >= v2:
            md1 = d1
            md2 = d2
            mv1 = v1
            mv2 = v2
        i += 1

    assert(not md1 or not md2 or md1 < md2 < d)
    augmented.append((d, v, md1, mv1, md2, mv2))

with open("sp500aug.csv", "w") as dst:
    dst.write("Date,Value,Date1,Value1,Date2,Value2\n")
    for d, v, md1, mv1, md2, mv2 in augmented:
        dst.write(f"{d},{v},{md1},{mv1},{md2},{mv2}\n")
