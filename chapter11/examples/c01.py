try:
    compile("if True print('ready')", "broken_sample.py", "exec")
except SyntaxError as exc:
    print(type(exc).__name__)
    print(exc.lineno)
