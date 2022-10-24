import click
from tlist_API import Dbloder


@click.group()
def group():
    pass


# @click.command()
# @click.option('--mode', default=2, help="Choose output mode: \n 1 for integer \n 2 for float")
# def echoinfo(mode: int):
#     click.echo(todolist.getinfo(mode))


if __name__ == "__main__":
    # group.add_command(echoinfo)
    # group()
    dbloder = Dbloder()
    if not dbloder.schema("test1"):
        dbloder.create("test1", {"Id": ["INTEGER", "PRIMARY KEY", "NOT NULL"]})
        
