import typer
app = typer.Typer()

@app.command()
def print_hello() -> None:
    print("HELLO!")

@app.command()
def print_hello2() -> None:
    print("HELLO 2!")

app(["print-hello"],["print-hello2"])
