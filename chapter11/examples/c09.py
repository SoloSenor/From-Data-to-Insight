for text in ("4", "bad"):
    try:
        count = int(text)
    except ValueError:
        print("invalid count")
    else:
        print("accepted", count)
