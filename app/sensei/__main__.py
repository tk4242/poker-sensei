"""python -m sensei hash-password  … パスワードのハッシュを作る（.env の APP_PASSWORD_HASH に貼る）
   python -m sensei check          … 設定と問題集の形式を確認する"""
import getpass
import sys


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "hash-password":
        from .auth import hash_password
        pw = getpass.getpass("パスワード（12文字以上）: ")
        if len(pw) < 12 or pw != getpass.getpass("もう一度: "):
            print("12文字以上で、2回同じものを入力してください。")
            return 1
        print("APP_PASSWORD_HASH=" + hash_password(pw))
        return 0
    if cmd == "check":
        from . import content
        from .config import Config
        problems = Config().check() + content.validate_bank()
        print("\n".join(problems) or f"OK（問題集 {len(content.question_bank())} 問）")
        return 1 if problems else 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
