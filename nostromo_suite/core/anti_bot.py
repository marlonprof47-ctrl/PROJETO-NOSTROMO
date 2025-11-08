def eula_agreement(eula_text: str) -> bool:
    print("\n----- EULA -----")
    print(eula_text)
    answer = input("\nDo you agree with the EULA? (Y/N): ").strip().upper()
    return answer == "Y"

def mini_captcha() -> bool:
    print("\n--- Anti-Bot Check ---")
    answer = input("What is 'Blue' spelled backwards? ").strip().lower()
    return answer == "eulb"