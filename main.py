from engine.app import Engine

def main():
    engine = Engine(width=1920, height=1080, title="PygamE", fps=60)

    engine.run()

    

if __name__ == "__main__":
    main()