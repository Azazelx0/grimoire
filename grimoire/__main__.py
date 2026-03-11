"""Allow running with: python -m grimoire"""
import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        from grimoire.banner import print_banner
        print_banner()
        from grimoire.updater import run_update
        run_update()
    else:
        from grimoire.cli import main
        main()
