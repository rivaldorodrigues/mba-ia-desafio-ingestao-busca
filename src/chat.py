from search import search_prompt


def main():
    chain = search_prompt()

    if not chain:
        print("Não foi possível iniciar o chat. Verifique os erros de inicialização.")
        return

    while True:
        print("\nFaça sua pergunta:")
        pergunta = input("> ").strip()

        if pergunta.lower() in ("sair", "exit", "quit"):
            print("Encerrando o chat.")
            break

        if not pergunta:
            continue

        resposta = chain.invoke(pergunta)
        print(f"\nRESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()
