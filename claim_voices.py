from voicemod import trigger_claim

if __name__ == "__main__":
    count = 0
    while True:
        claimed = trigger_claim()
        if claimed:
            count += 1
            print(f"Claimed {count} voice.")
            continue
        break
    print(f"Claimed Voices: {count}.")
