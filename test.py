def hello(name='you'):
    print('Hello', name)

if __name__ == '__main__':
    from py2cli import run
    run(hello)
