"""QuizGame class and interactive game loop."""

import sys
from typing import List, Optional
from quiz import Quiz
from storage import QuizStorage


class QuizGame:
    """퀴즈 게임의 전체 흐름과 사용자 인터랙션을 관리하는 컨트롤러 클래스.

    Attributes:
        storage (QuizStorage): 상태 저장 및 불러오기를 담당하는 객체
        quizzes (List[Quiz]): 현재 등록된 퀴즈 목록
        best_score (int): 기록된 최고 점수
        is_running (bool): 게임 루프 실행 여부
    """

    def __init__(self, storage: Optional[QuizStorage] = None) -> None:
        self.storage = storage or QuizStorage("state.json")
        self.quizzes: List[Quiz] = []
        self.best_score: int = 0
        self.is_running: bool = False
        self._initialize_data()

    def _initialize_data(self) -> None:
        """state.json에서 데이터를 불러와 메모리에 적재합니다."""
        self.quizzes, self.best_score, msg = self.storage.load_state()
        print(msg)

    def prompt_int(self, prompt_text: str, min_val: int, max_val: int) -> int:
        """공통 입력 예외 처리가 적용된 정수 입력 도우미 메서드.

        공백 제거, 빈 입력, 비숫자 입력, 허용 범위 초과를 모두 검증하며
        올바른 입력이 들어올 때까지 재입력을 유도합니다.

        Args:
            prompt_text (str): 사용자에게 보여줄 프롬프트 문구
            min_val (int): 입력 가능한 최소 정수
            max_val (int): 입력 가능한 최대 정수

        Returns:
            int: 유효성 검사를 통과한 정수
        """
        while True:
            raw_input = input(prompt_text).strip()

            if not raw_input:
                print("⚠️ 입력값이 비어 있습니다. 숫자를 입력해 주세요.\n")
                continue

            try:
                val = int(raw_input)
            except ValueError:
                print(f"⚠️ 잘못된 입력입니다. {min_val}~{max_val} 사이의 정수 숫자를 입력하세요.\n")
                continue

            if val < min_val or val > max_val:
                print(
                    f"⚠️ 허용 범위를 벗어났습니다. {min_val}~{max_val} 사이의 숫자를 입력하세요.\n"
                )
                continue

            return val

    def prompt_non_empty_str(self, prompt_text: str) -> str:
        """비어 있지 않은 문자열 입력을 보장하는 입력 도우미 메서드."""
        while True:
            text = input(prompt_text).strip()
            if not text:
                print("⚠️ 빈 값은 입력할 수 없습니다. 내용을 입력해 주세요.\n")
                continue
            return text

    def display_menu(self) -> None:
        """메인 콘솔 메뉴를 출력합니다."""
        print()
        print("=" * 40)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print("=" * 40)
        print("1. 퀴즈 풀기")
        print("2. 퀴즈 추가")
        print("3. 퀴즈 목록")
        print("4. 점수 확인")
        print("5. 종료")
        print("=" * 40)

    def handle_menu_selection(self, choice: int) -> None:
        """사용자가 선택한 메뉴 번호에 따라 해당 기능을 분기 실행합니다."""
        if choice == 1:
            self.play_quiz()
        elif choice == 2:
            self.add_quiz()
        elif choice == 3:
            self.show_quizzes()
        elif choice == 4:
            self.show_best_score()
        elif choice == 5:
            self.exit_game()

    def play_quiz(self) -> None:
        """저장된 퀴즈를 순차 출제하고 채점하여 결과를 안내 및 최고 점수를 갱신합니다."""
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요!")
            return

        total_questions = len(self.quizzes)
        print(f"\n📝 퀴즈를 시작합니다! (총 {total_questions}문제)")

        correct_count = 0
        for idx, quiz in enumerate(self.quizzes, start=1):
            print("\n" + "-" * 40)
            print(quiz.get_display_text(question_number=idx))
            print()
            user_answer = self.prompt_int("정답 입력 (1-4): ", 1, 4)

            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                correct_count += 1
            else:
                correct_choice_text = quiz.choices[quiz.answer - 1]
                print(
                    f"❌ 오답입니다! (정답: {quiz.answer}번 - {correct_choice_text})"
                )

        score = int((correct_count / total_questions) * 100)

        print("\n" + "=" * 40)
        print(f"🏆 결과: {total_questions}문제 중 {correct_count}문제 정답! ({score}점)")

        if score > self.best_score:
            print(f"🎉 축하합니다! 새로운 최고 점수입니다! (이전: {self.best_score}점 -> 현재: {score}점)")
            self.best_score = score
            self.storage.save_state(self.quizzes, self.best_score)
        else:
            print(f"📌 현재 최고 점수: {self.best_score}점")
        print("=" * 40)

    def add_quiz(self) -> None:
        """퀴즈 추가 (이후 커밋에서 구현 예정)"""
        print("\n⏳ 퀴즈 추가 기능이 곧 준비됩니다.")

    def show_quizzes(self) -> None:
        """퀴즈 목록 조회 (이후 커밋에서 구현 예정)"""
        print("\n⏳ 퀴즈 목록 기능이 곧 준비됩니다.")

    def show_best_score(self) -> None:
        """최고 점수 확인 (이후 커밋에서 구현 예정)"""
        print("\n⏳ 점수 확인 기능이 곧 준비됩니다.")

    def exit_game(self) -> None:
        """게임을 안전하게 저장하고 종료합니다."""
        print("\n💾 현재 게임 상태를 저장하는 중...")
        self.storage.save_state(self.quizzes, self.best_score)
        print("👋 퀴즈 게임을 종료합니다. 이용해 주셔서 감사합니다!")
        self.is_running = False

    def safe_shutdown(self) -> None:
        """강제 인터럽트 또는 예외 발생 시 비정상 종료를 방지하고 안전하게 저장합니다."""
        print("\n\n⚠️ 프로그램이 안전 종료 신호(KeyboardInterrupt / EOF)를 감지했습니다.")
        print("💾 가능한 범위에서 데이터를 저장하고 프로그램을 안전하게 종료합니다...")
        self.storage.save_state(self.quizzes, self.best_score)
        print("👋 안전하게 종료되었습니다. 안녕히 가세요!")

    def run(self) -> None:
        """게임의 메인 루프를 시작합니다."""
        self.is_running = True
        try:
            while self.is_running:
                self.display_menu()
                choice = self.prompt_int("선택 (1-5): ", 1, 5)
                self.handle_menu_selection(choice)
        except (KeyboardInterrupt, EOFError):
            self.safe_shutdown()
