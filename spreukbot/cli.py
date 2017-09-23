import click


@click.group()
def cli():
    pass


@cli.group()
def db():
    pass


@db.command()
def init():
    from spreukbot.elastic import SayingDatabase
    db = SayingDatabase()
    db.init()


@db.command()
def reindex():
    from spreukbot.elastic import SayingDatabase
    db = SayingDatabase()
    db.reindex()


@cli.group()
def facebook():
    pass


@facebook.command()
@click.argument('album_id')
def fetch_album(album_id):
    import spreukbot.facebook as facebook
    print(facebook.fetch_album(album_id))


if __name__ == '__main__':
    cli()
