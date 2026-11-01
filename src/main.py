import argparse

def main():
    parser = argparse.ArgumentParser(description="YottaFlex synthetic feedback pipeline")
    parser.add_argument("--scale", choices=["starter", "full"], default="starter")
    parser.add_argument("--seed", type=int, default=20261022)
    args = parser.parse_args()
    print(f"Scaffold ready. scale={args.scale}, seed={args.seed}")
    print("Next: implement master data and deterministic child-record generation.")

if __name__ == "__main__":
    main()
