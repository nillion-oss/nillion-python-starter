from nada_dsl import *

def nada_main():
    # Define parties
    setter = Party(name="Setter")
    guesser = Party(name="Guesser")
    
    # Define inputs
    secret_number = SecretInteger(Input(name="secret_number", party=setter))
    guessed_number = SecretInteger(Input(name="guessed_number", party=guesser))
    
    # Logic to check if guess is correct
    is_correct = secret_number == guessed_number
    
    # Output the result
    return [Output(is_correct, "guess_result", guesser)]
