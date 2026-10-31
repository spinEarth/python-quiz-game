"""Entry point for the Quiz Game console application."""

import sys
from game import QuizGame


def main() -> None:
    """퀴즈 게임 애플리케이션 진입점 함수."""
    try:
        game = QuizGame()
        game.run()
    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 프로그램을 안전하게 종료합니다.")
        sys.exit(0)
    except Exception as unexpected_err:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {unexpected_err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
